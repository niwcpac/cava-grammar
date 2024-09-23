"""
File:    event_converter.py
Author:  Froylan Maldonado
Email:   froylan.g.maldonado.civ@us.navy.mil
Created: September 2024
Description:
    Converts Ghidra instrumentation events into Grammar statements.
"""

from abc import ABCMeta, abstractmethod
from core.grammar_classes import Interaction
from core.misc import GRAMMAR_TYPE, keyboard_scan_code_mapping, internal_plugin_to_grammar, charMapping
from utils.hash_buffer import HashBuffer
from utils.grammar_event import GrammarEvent


class EventParser:
    """
    EventParser is an object that holds all the event converter classes. 

    Its purpose is to take json events and delegate the conversion to a grammar statement
    to the event converter classes it holds.
    """

    def __init__(self):
        self.MouseEventConverter_ = MouseEvent()
        self.KeyboardEventConverter_ = KeyboardEvent()
        self.HeaderEventConverter_ = HeaderEvent()
        self.WindowEventConverter_ = WindowEvent()
        self.FieldMouseEventConverter_ = FieldMouseEvent()
        self.FieldInputEventConverter_ = FieldInputEvent()
        self.MousePressedEventConverter_ = MousePressedEvent()
        self.GhidraProgramActivatedEventConverter_ = GhidraProgramActivatedEvent()
        self.FunctionGraphVertexClickEvent_ = FunctionGraphVertexClickEvent()
        self.FunctionGraphEdgePickEvent_ = FunctionGraphEdgePickEvent()
        self.VerticalScrollbarAdjustmentEvent_ = VerticalScrollbarAdjustmentEvent()
        self.MouseEnteredEvent_ = MouseEnteredEvent(True)
        self.MouseExitedEvent_ = MouseExitedEvent(True)

    def parse_event(self, buffer: HashBuffer) -> list or None:
        """
        This function takes an event_frame and an index, and gets the underlying json event. We then take the
        json event and get the name of it to properly delegate the job of converting it to the proper class.

        Args:
            @param buffer: HashBuffer of instrumentation events being analyzed

        return : We return a tuple with the Interaction grammar statement and a timestamp. We return None, None
        if the json event is not supported.
        """

        '''
        Delegating the job of converting the event to a grammar statement
        '''

        # buffer.debug()
        event_name = buffer.current().get("Name")

        if event_name == "KeyboardEvent":
            return self.KeyboardEventConverter_.parse_event(buffer)
        elif event_name == "HeaderEvent":
            return self.HeaderEventConverter_.parse_event(buffer)
        elif event_name == "WindowEvent":
            return self.WindowEventConverter_.parse_event(buffer)
        elif event_name == "FieldMouseEvent":
            return self.FieldMouseEventConverter_.parse_event(buffer)
        elif event_name == "MousePressedEvent":
            return self.MousePressedEventConverter_.parse_event(buffer)
        elif event_name == "FieldInputEvent":
            return self.FieldInputEventConverter_.parse_event(buffer)
        elif event_name == "GhidraProgramActivatedEvent":
            return self.GhidraProgramActivatedEventConverter_.parse_event(buffer)
        elif event_name == "VerticalScrollbarAdjustmentEvent":
            return self.VerticalScrollbarAdjustmentEvent_.parse_event(buffer)
        elif event_name == "MouseEnteredEvent":
            return self.MouseEnteredEvent_.parse_event(buffer)
        elif event_name == "MouseExitedEvent":
            return self.MouseExitedEvent_.parse_event(buffer)
        '''
        elif event_name == "FunctionGraphVertexClickEvent":
            return self.FunctionGraphVertexClickEvent_.parse_event(buffer)
        elif event_name == "FunctionGraphEdgePickEvent":
            return self.FunctionGraphEdgePickEvent_.parse_event(buffer)
        
        '''


class EventConverter:
    """
    Abstract Class that all EventConverter child classes are meant to follow. 

    All children are expected to have the following functions implemented.
    """
    __metaclass__ = ABCMeta

    def __init__(self, debug=False):
        self.debug_ = debug

    @abstractmethod
    def parse_event(self, buffer: HashBuffer) -> list or None:
        """Create grammar statement with event data"""


class MouseEvent(EventConverter):
    """
    MouseEvent is meant to act as an object that handles converting a json event into 
    a grammar fragment for the input device and input action fragments.
    Currently, not being used.
    """

    def parse_event(self, buffer: HashBuffer) -> list or None:
        """
        This function is meant to take a json mouse event produced by the cava-platform and turn 
        it into a grammar fragment for the interaction grammar. Currently, mouse clicks
        and movement are supported, but drag events are not.

        Args:
            @param buffer: list-like data structure that holds json events.
        """

        '''
        Getting meta data from Json object
        '''
        event = buffer.current()
        interaction = Interaction()
        event_data = event.get("Data")
        event_name = event_data.get("Name")

        '''
        Setting up strings for the grammar statement we are going to generate
        '''
        if event_name == "MOVE":
            x_coord = event_data.get("X")
            y_coord = event_data.get("Y")
            event_action = "Move"
            event_metadata = "(" + str(x_coord) + ", " + str(y_coord) + ")"
        else:
            event_metadata = "Click"
            event_action = event_data.get("Button")
            event_action = event_action.lower()
            event_action = event_action.capitalize()

        input_device_fragment = "Mouse"
        input_action_fragment = event_action + " " + event_metadata

        interaction.set_fragment(input_device_fragment, GRAMMAR_TYPE.INPUT_DEVICE)
        interaction.set_fragment(input_action_fragment, GRAMMAR_TYPE.INPUT_ACTION)

        grammar_event = GrammarEvent(sentence=interaction,
                                     inferred=False,
                                     hash_list=event.get("Hash"),
                                     timestamp=event.get("Timestamp"),
                                     source_event=event.get("Event"))

        return [grammar_event]


class KeyboardEvent(EventConverter):
    """
    KeyboardEvent is meant to take KeyboardEvents and convert them to grammar fragments.

    Note that this class takes advantage of the buffer by stringing together keys that we have assumed
    to be typed in a continuous matter.
    """

    def parse_event(self, buffer: HashBuffer) -> list or None:
        """
        Takes a Keyboard event, extracts relevant information and creates 
        input action and input device grammar fragments.

        Args:
            @param buffer: list-like data structure that holds json events.
        """

        '''
        Checks if the current keyboard event we are converting has been consumed by a previous 
        keyboard event.
        '''
        if buffer.current().get("Consumed"):
            return None

        event = buffer.current()
        event_data = event.get("Data")

        '''
        Since the instrumentation software differentiates from keystrokes that are being pressed and being released, 
        we ignore the release strokes. This might cause issues if someone meant to hold down a key while typing...
        '''
        if event_data.get("EventName") == "UP":
            return None

        '''
        Gets all the keyboard events that meet some typing heuristic. Check the function documentation for more 
        information.
        '''
        typed = self.get_all_typing_events(buffer)

        if not typed:
            if self.debug_:
                print("[DEBUG] No typed string was detected")
            return None

        interaction = Interaction()
        typed.insert(0, event)

        typed_string, hashes = self.create_typing_string(typed)

        input_device_fragment = "Keyboard"
        input_action_fragment = typed_string

        interaction.set_fragment(input_device_fragment, GRAMMAR_TYPE.INPUT_DEVICE)
        interaction.set_fragment(input_action_fragment, GRAMMAR_TYPE.INPUT_ACTION)

        grammar_event = GrammarEvent(sentence=interaction,
                                     inferred=False,
                                     hash_list=hashes,
                                     timestamp=event.get("Timestamp"),
                                     source_event=event.get("Event"))

        if self.debug_:
            grammar_event.debug()

        return [grammar_event]

    def get_all_typing_events(self, buffer: HashBuffer) -> list:
        """
        This function, given an event frame, and the index of where the current event is being analyzed,
        returns a list of all json events

        Args:
            @param buffer: HashBuffer data structure that holds instrumentation events
        """

        typing = []
        last_typed_event = buffer.current()
        event_list = buffer.get_event_list()
        index = buffer.get_index()

        for i in range(index + 1, len(event_list)):

            event = event_list[i]

            """
            Too many debug statements, keep blocked unless debugging this code.
            if self.debug_:
                print("[DEBUG] Event Name: ", event.get("Name"))
            """

            if event.get("Name") == "KeyboardEvent":

                '''
                EventName refers to if the stroke of the keyboard event was either up or down.
                '''
                event_data = event.get("Data")
                key_stroke = event_data.get("EventName")

                if key_stroke == "DOWN":

                    '''
                    Now, we know that a keyboard event other than the one we started with is in the buffer. Now
                    we must check if the keyboard event is within .91 secs of the last typed key. If it is, then we 
                    treat it as the last typed event and add it to the list of typed keyboard events.
                    '''
                    last_typed_event_time = last_typed_event.get("Timestamp")
                    curr_keyboard_event_time = event.get("Timestamp")
                    time_diff = curr_keyboard_event_time - last_typed_event_time

                    if self.debug_:
                        print("[DEBUG] Keystroke Time Diff: ", time_diff)

                    if time_diff < .91:
                        typing.append(event)
                        last_typed_event = event
                    else:
                        break

        return typing

    def create_typing_string(self, typed) -> (str, list):
        """
        Returns string of keys that were typed given a list of keyboard events

        Args:
            @param typed: List of keyboard json events
        """

        typed_string = ""
        hashes = []

        # This section tries to replicate the string that would've appeared on-screen while
        # typing
        for event in typed:
            key = event.get("Data").get("Key")
            hashes.append(event.get("Hash"))
            event["Consumed"] = True

            if key == "KEY_BACKSPACE" or key == "KEY_DELETE":
                typed_string = typed_string[:-1]
                continue

            transformed = charMapping.get(key)

            if transformed is None:
                continue

            typed_string += transformed

        return typed_string, hashes


class HeaderEvent(EventConverter):
    """
    HeaderEvents occur whenever a user interacts with the toolbar headers in ghidra. 
    This class is meant to take those HeaderEvents and convert them into grammar statements.
    """

    def parse_event(self, buffer: HashBuffer) -> list or None:
        """
        Takes HeaderEvent, extracts relevant information and then 
        creates grammar fragments for the give interaction grammar
        statement.

        Args:
            @param buffer: HashBuffer data structure that holds instrumentation events.
        """

        '''
        Since no other events consume Header Events, we don't check if it was consumed like Keyboard Events.
        
        We extract relevant information from the Json object.
        '''
        header_event = buffer.current()
        header_data = header_event.get("Data")
        interaction = Interaction()
        header = header_data.get("Header")
        header_event_type = header_data.get("EventType")
        header_menu_item = header_data.get("MenuItem")
        header_submenu_item = header_data.get("SubMenuItem")

        '''
        Note, that header events can only be produced by a mouse. 
        '''
        input_device_fragment = "Mouse"

        '''
        We convert the information found into strings that fit our grammar we have defined in a separate document.
        '''
        if header_event_type == "LeftClick":
            input_action_fragment = "Left Click"
        elif header_event_type == "RightClick":
            input_action_fragment = "Right Click"
        elif header_event_type == "MiddleClick":
            input_action_fragment = "Middle PressDown"
        else:
            input_action_fragment = "Move"

        '''
        Header events may not have certain fields. So, here we just double check and mark them as empty if the field 
        is None.
        '''
        if header_menu_item is None:
            header_menu_item = ""

        if header_submenu_item is None:
            header_submenu_item = ""

        header_meta_data = ""

        '''
        If certain fields are not emtpy, then we create a string that concatenates this information into a string that 
        fits the grammar.
        '''
        if header_menu_item != "":
            header_meta_data = header_menu_item
            if header_submenu_item != "":
                header_meta_data = header_meta_data + " : " + header_submenu_item

        tool_context_fragment = "Toolbar : " + header

        if header_meta_data != "":
            tool_context_fragment = tool_context_fragment + " : " + header_meta_data

        interaction.set_fragment(input_device_fragment, GRAMMAR_TYPE.INPUT_DEVICE)
        interaction.set_fragment(input_action_fragment, GRAMMAR_TYPE.INPUT_ACTION)
        interaction.set_fragment(tool_context_fragment, GRAMMAR_TYPE.TOOL_CONTEXT)

        grammar_event = GrammarEvent(sentence=interaction,
                                     inferred=False,
                                     hash_list=[header_event.get("Hash")],
                                     timestamp=header_event.get("Timestamp"),
                                     source_event=header_event.get("Event"))

        if self.debug_:
            grammar_event.debug()

        return [grammar_event]


class WindowEvent(EventConverter):
    """
    Takes a WindowEvent, extracts relevant information,
    then creates a grammar fragment.

    Note that a window event can be several things. If a mouse cursor was moved to another plugin,
    or if a user performed any sort of mouse action inside a plugin such as a left click, then a window event will
    also be created on top of other instrumentation that captures those actions.
    """

    def parse_event(self, buffer: HashBuffer) -> list or None:
        """
        Extracts relevant information from a WindowEvent, then delegates the task of creating a grammar statement
        depending on what type of window event it was.

        Args:
            @param buffer: HashBuffer data structure that holds instrumentation events.
        """

        if buffer.current().get("Consumed"):
            return None

        '''
        Need to figure out what type of window event this creates since a window event is rather generic.
        '''
        event = buffer.current()
        window_event_data = event.get("Data")
        event_type = window_event_data.get("EventType")

        if self.debug_:
            print("[DEBUG] WindowEvent Type: ", event_type)

        if event_type == "MouseEntry":
            return self.create_mouse_entry_sentence(event)
        elif event_type == "MouseExit":
            return self.create_mouse_exit_sentence(event)
        else:
            return self.create_mouse_click_sentence(event)

    def create_mouse_entry_sentence(self, event) -> list or None:
        """
        This function takes a window event and creates a grammar statement which states that the mouse has
        entered a new plugin.

        Args:
            @param event: Singular Window Event from a HashBuffer object.
        """

        interaction = Interaction()
        window_event_data = event.get("Data")
        event["Consumed"] = True

        input_device = "Mouse"
        input_action = "Move : Enter"
        tool_context = window_event_data.get("WindowName")

        interaction.set_fragment(input_device, GRAMMAR_TYPE.INPUT_DEVICE)
        interaction.set_fragment(input_action, GRAMMAR_TYPE.INPUT_ACTION)
        interaction.set_fragment(tool_context, GRAMMAR_TYPE.TOOL_CONTEXT)

        grammar_event = GrammarEvent(sentence=interaction,
                                     inferred=False,
                                     hash_list=[event.get("Hash")],
                                     timestamp=event.get("Timestamp"),
                                     source_event=event.get("Event"))

        if self.debug_:
            grammar_event.debug()

        return [grammar_event]

    def create_mouse_exit_sentence(self, event) -> list or None:
        """
        This function takes a window event and creates a grammar statement which states that the mouse has
        exited a new plugin.

        Args:
            @param event: Singular Window Event from a HashBuffer object.

        """
        interaction = Interaction()

        event["Consumed"] = True
        window_event_data = event.get("Data")

        input_device = "Mouse"
        input_action = "Move : Exit"
        tool_context = window_event_data.get("WindowName")

        interaction.set_fragment(input_device, GRAMMAR_TYPE.INPUT_DEVICE)
        interaction.set_fragment(input_action, GRAMMAR_TYPE.INPUT_ACTION)
        interaction.set_fragment(tool_context, GRAMMAR_TYPE.TOOL_CONTEXT)

        grammar_event = GrammarEvent(sentence=interaction,
                                     inferred=False,
                                     hash_list=[event.get("Hash")],
                                     timestamp=event.get("Timestamp"),
                                     source_event=event.get("Event"))

        if self.debug_:
            grammar_event.debug()

        return [grammar_event]

    def create_mouse_click_sentence(self, event) -> list or None:
        """
        This function takes a window event and creates a grammar statement which states that the mouse has
        been clicked while inside a plugin.

        Args:
            @param event: Singular Window Event from a HashBuffer object.
        """

        interaction = Interaction()

        window_event_data = event.get("Data")
        event_type = window_event_data.get("EventType")
        event_source = window_event_data.get("WindowName")

        input_device_fragment = "Mouse"

        if event_type == "LeftClick":
            input_action_fragment = "Left Click"
        elif event_type == "RightClick":
            input_action_fragment = "Right Click"
        elif event_type == "MiddleClick":
            input_action_fragment = "Middle PressDown"
        else:
            input_action_fragment = "Move"

        tool_context_fragment = event_source

        interaction.set_fragment(input_device_fragment, GRAMMAR_TYPE.INPUT_DEVICE)
        interaction.set_fragment(input_action_fragment, GRAMMAR_TYPE.INPUT_ACTION)
        interaction.set_fragment(tool_context_fragment, GRAMMAR_TYPE.TOOL_CONTEXT)

        grammar_event = GrammarEvent(sentence=interaction,
                                     inferred=False,
                                     hash_list=[event.get("Hash")],
                                     timestamp=event.get("Timestamp"),
                                     source_event=event.get("Event"))

        if self.debug_:
            grammar_event.debug()

        return [grammar_event]


class FieldMouseEvent(EventConverter):
    """
    Takes a FieldMouseEvent and generates a grammar statement.

    Field Mouse Events only occur when a user left/middle clicks an element inside the CavaCodeBrowser, CavaDecompiler,
    and CavaFunctionGraph plugin. Field Mouse Events then contain information on what specific element was interacted
    with and in what plugin the interaction occurred.

    We utilize FieldLocationEvents in this class to figure out how the Ghidra UI changed from the interaction.
    Depending on the amount of clicks, we can deduce how the UI changed and construct the appropriate tool action
    grammar statement.
    """

    def parse_event(self, buffer: HashBuffer) -> list or None:
        """
        Extracts relevant information from a FieldMouseEvent, then delegates the task of creating tool action fragment
        depending on what type of FieldMouseEvent it is.

        Args:
            @param buffer: HashBuffer data structure that holds instrumentation events.
        """

        event = buffer.current()

        interaction = Interaction()

        event_data = event.get("Data")
        plugin_name = event_data.get("EventSource")
        field = event_data.get("FieldText")
        event_button = event_data.get("MouseButton")
        event_count = event_data.get("ClickCount")

        '''
        Constructing the generic grammar fragments that all field mouse events are going to have.
        
        NOTE: A weird quirk of how ghidra works causes it to not produce a field mouse event when a field is right 
        clicked. That means we will never have a field mouse event where the mouse button is Right. We keep in here in 
        case future release of ghidra change how that is produced.
        '''
        if event_button == 1:
            mouse_button = "Left"
        elif event_button == 2:
            mouse_button = "Middle"
        else:
            mouse_button = "Right"

        if event_count == 1:
            mouse_action = "Click"
        elif event_count == 2:
            mouse_action = "DoubleClick"
        else:
            mouse_action = "MultipleClicks"

        input_device = "Mouse"
        input_action = mouse_button + " " + mouse_action
        tool_context = internal_plugin_to_grammar.get(plugin_name) + " : " + "Field(" + field + ")"
        tool_action = ""
        hash_list = []

        if self.debug_:
            print("PluginName:", plugin_name)
            print("MappingToGrammar: ", internal_plugin_to_grammar.get(plugin_name))

        interaction.set_fragment(input_device, GRAMMAR_TYPE.INPUT_DEVICE)
        interaction.set_fragment(input_action, GRAMMAR_TYPE.INPUT_ACTION)
        interaction.set_fragment(tool_context, GRAMMAR_TYPE.TOOL_CONTEXT)

        if self.debug_:
            print("Grammar Statement Before FieldLocation Extraction: ", str(interaction))
        '''
        Note that middle clicking a field causes it to be highlighted along with other occurrences of the same field.
        
        When we left click, a highlight doesn't happen, instead the focus of the program changes to where the user 
        left clicked. 
        
        Two completely different tool action fragments are described above so we must differentiate them.
        '''
        if mouse_button == "Left":
            tool_action, hash_list = self.create_left_click_tool_action_fragment(buffer, mouse_action)
        elif mouse_button == "Middle":
            tool_action = self.create_mouse_wheel_click_tool_action_fragment(buffer)

        if tool_action != "":
            interaction.set_fragment(tool_action, GRAMMAR_TYPE.ACTION)

        hash_list.append(event.get("Hash"))
        grammar_event = GrammarEvent(sentence=interaction,
                                     inferred=False,
                                     hash_list=hash_list,
                                     timestamp=event.get("Timestamp"),
                                     source_event=event.get("Event"))

        if self.debug_:
            grammar_event.debug()

        return [grammar_event]

    def create_left_click_tool_action_fragment(self, buffer: HashBuffer, mouse_action) -> (str, list):
        """
        When a field is (double)left-clicked, Ghidra then produces several FieldLocationEvents. These
        FieldLocationEvents are essentially internal events that tell other plugins to change the focus of the program
        to another line of code. We can use these to figure out where the focus of the program was changed to due to a
        (double)left-click.

        But it's not simple as looking for FieldLocationEvents that happened after a FieldMouseEvent. Due to how internal
        instrumentation is performed, we can have FieldLocationEvents appear BEFORE a FieldMouseEvent is detected! So we
        have to check previous and future field location events and see if they happened at a close enough interval.

        Now, due to how internal instrumentation works, a single left click can produce up to 3 different
        FieldLocationEvents, one for each plugin that is fully instrumented. But there's cases where less than 3 can
        appear. When a doubleleft-click is performed up there can be more than 6 FieldLocationEvents! The first 3 are
        due to the first left click happening, and the others are due to the program jumping to where the field is
        defined in the binary. This jumping can cause the CavaDecompilerPlugin to produce more than 3 FieldLocationEvents!
        This is due to how the jumping is coded internally in Ghidra.

        Keep the above in mind when reading the following.
        """

        selection_changed = {}

        '''
        We load all FieldLocationEvents that occur within the FieldMouseEvent we are converting. The heuristics for 
        which events to load can be seen in the function doc.
        '''
        field_location_events = load_field_location_events(buffer)
        tool_action = ""
        hash_list = []

        if mouse_action == "Click":
            field_location_events = reversed(field_location_events)

        '''
        When a single left click is performed, then we need to iterate in reverse to keep the "oldest" FieldLocationEvents
        in our hashmap since theres the possibility that more than 6 FieldLocationEvents were loaded!
        
        The opposite is the case when a doubleleft-click happens. We need the "newest" FieldLocationEvents.        
        '''
        for field_event in field_location_events:

            if field_event.get("Consumed"):
                continue

            field_event_data = field_event.get("Data")
            plugin_name = field_event_data.get("EventSource")
            selection_changed[plugin_name] = field_event

        '''
        This creates the tool action fragment from the FieldLocationEvents that we ended up choosing.
        '''
        for plugin_name, field_event in selection_changed.items():

            mod = " && "

            if tool_action == "":
                mod = ""

            # field_event["Consumed"] = True
            hash_list.append(field_event.get("Hash"))
            tool_action_field = field_event.get("Data").get("FieldText")
            tool_action += mod + internal_plugin_to_grammar.get(
                plugin_name) + " : SelectionChanged : " + "Field(" + tool_action_field + ")"

        return tool_action, hash_list

    def create_mouse_wheel_click_tool_action_fragment(self, buffer: HashBuffer) -> str:
        """
        When a field is mouse wheel clicked, that field and every instance of that field is then
        highlighted yellow in the decompiler and any other occurrence in the code browser listing panel.

        Args:
            @param buffer: list-like data structure that holds instrumentation events.
        """
        '''
        Not finished being implemented yet. The grammar doesn't support this actions just yet.
        '''

        event = buffer.current()
        event_data = event.get("Data")
        plugin = event_data.get("EventSource")
        field = event_data.get("FieldText")

        tool_action = internal_plugin_to_grammar.get(plugin) + " : " + " SetHighlight(" + field + ")"

        return tool_action


class MousePressedEvent(EventConverter):
    """
    This class is used to convert MousePressedEvents into grammar statements.

    For most cases, this class will produce grammar statements that other converters
    already produce. But in the case that a user performs a right click, we can detect if that action produced a popup
    context menu.
    """

    def parse_event(self, buffer: HashBuffer) -> list or None:
        """
        Extracts relevant information from a MousePressedEvent.

        For most cases, this event will produce duplicate grammar statements that are not very useful since the field
        mouse event contains more information. But in the case of Mouse right-clicks, this event contains important
        information.

        The right click events that this event produces contain what field was right-clicked, and where the event took
        place and if a context menu appeared due to the right-click.

        Args:
            @param buffer: HashBuffer data structure that holds instrumentation events.
        """

        event = buffer.current()

        interaction = Interaction()
        event_data = event.get("Data")
        event_button = event_data.get("MouseButton")
        event_count = event_data.get("ClickCount")
        plugin_name = event_data.get("EventSource")
        tool_context = ""
        tool_action = ""
        hash_list = []
        hash_from_field = ""
        grammar_statements = []

        if event_button == 1:
            mouse_button = "Left"
        elif event_button == 2:
            mouse_button = "Middle"
        else:
            mouse_button = "Right"
            '''
            When this is true, then that means that this right click produced a context menu. And we know that a field 
            location event also occurred because that's how Ghidra works internally. So we get the correct 
            FieldLocationEvent and extract its field to use in the tool action fragment.
            '''
            if event_data.get("IsPopupTrigger"):
                '''
                This loads all recent FieldLocationEvents that occurred within this event.
                '''
                field_events = load_field_location_events(buffer)
                '''
                Since we need a singular FieldLocationEvent field, we need to get the one where the EventSource 
                is the same as the MousePressedEvent.
                '''
                field, hash_from_field = get_field_from_plugin(field_events, plugin_name)
                tool_action = internal_plugin_to_grammar.get(
                    plugin_name) + " : Field(" + field + ") : " + "Context Menu"
                tool_context = internal_plugin_to_grammar.get(plugin_name) + " : Field(" + field + ")"
                grammar_statements = self.generate_inferred_right_click_events(buffer, field, plugin_name)

        if event_count == 1:
            mouse_action = "Click"
        elif event_count == 2:
            mouse_action = "DoubleClick"
        else:
            mouse_action = "MultipleClicks"

        input_device = "Mouse"
        input_action = mouse_button + " " + mouse_action

        if tool_context == "":
            tool_context = internal_plugin_to_grammar.get(plugin_name)

        if self.debug_:
            print("EventName: ", event.get("Name"))
            print("PluginName:", plugin_name)
            print("MappingToGrammar: ", internal_plugin_to_grammar.get(plugin_name))

        hash_list.append(event.get("Hash"))
        interaction.set_fragment(input_device, GRAMMAR_TYPE.INPUT_DEVICE)
        interaction.set_fragment(input_action, GRAMMAR_TYPE.INPUT_ACTION)
        interaction.set_fragment(tool_context, GRAMMAR_TYPE.TOOL_CONTEXT)

        if tool_action != "":
            interaction.set_fragment(tool_action, GRAMMAR_TYPE.ACTION)
            hash_list.append(hash_from_field)
            if self.debug_:
                print("Tool Action Fragment: ", tool_action)
                print("Hash List: ", hash_list)

        grammar_event_core = GrammarEvent(sentence=interaction,
                                          inferred=False,
                                          hash_list=hash_list,
                                          timestamp=event.get("Timestamp"),
                                          source_event=event.get("Event"))

        grammar_statements.insert(0, grammar_event_core)

        if self.debug_:
            for e in grammar_statements:
                e.debug()

        return grammar_statements

    def generate_inferred_right_click_events(self, buffer: HashBuffer, field: str, plugin_name: str) -> list:
        """
        This function creates inferred grammar statements that assumed a right click event occurred.

        Since we can't detect(with current instrumentation) what happens inside a pop-up box, we need to state inferred
        grammar statements; such as making a comment, or relabeling a field.

        Args:
            @param buffer: A list-like data structure that holds instrumentation events.
            @param field: The field that was interacted.
            @param plugin_name: The plugin where the right-click occurred.

            @return list: This list must be a list of grammar events.
        """

        right_click_comment = Interaction()
        right_click_relabel = Interaction()
        event = buffer.current()
        hash_list = [buffer.current().get("Hash")]

        right_click_comment.set_fragment("Mouse", GRAMMAR_TYPE.INPUT_DEVICE)
        right_click_comment.set_fragment("Left Click", GRAMMAR_TYPE.INPUT_ACTION)
        right_click_comment.set_fragment(internal_plugin_to_grammar.get(plugin_name) + " : Field(" + field + ") : "
                                         + "Context Menu" + " : " + "Set Comment...", GRAMMAR_TYPE.TOOL_CONTEXT)
        right_click_comment.set_fragment("Open(CommentPlugin)", GRAMMAR_TYPE.ACTION)

        right_click_relabel.set_fragment("Mouse", GRAMMAR_TYPE.INPUT_DEVICE)
        right_click_relabel.set_fragment("Left Click", GRAMMAR_TYPE.INPUT_ACTION)
        right_click_relabel.set_fragment(internal_plugin_to_grammar.get(plugin_name) + " : Field(" + field + ") : "
                                         + "Context Menu" + " : " + "relabel", GRAMMAR_TYPE.TOOL_CONTEXT)
        right_click_relabel.set_fragment("Open(RelabelPlugin)", GRAMMAR_TYPE.ACTION)

        grammar_event_comment = GrammarEvent(sentence=right_click_comment,
                                             inferred=True,
                                             hash_list=hash_list,
                                             timestamp=event.get("Timestamp"),
                                             source_event=event.get("Event"))
        grammar_event_relabel = GrammarEvent(sentence=right_click_relabel,
                                             inferred=True,
                                             hash_list=hash_list,
                                             timestamp=event.get("Timestamp"),
                                             source_event=event.get("Event"))

        if self.debug_:
            grammar_event_relabel.debug()
            grammar_event_comment.debug()

        return [grammar_event_comment, grammar_event_relabel]


class FieldInputEvent(EventConverter):
    """
    This class takes a FieldInputEvent and converts it into a grammar statement.

    A Field Input Event occurs when a user has a field selected and presses a key on the
    keyboard. The Field Input Event includes booleans indicating if any modifiers were also
    held (i.e. CTRL, ALT, SHIFT).
    """

    def parse_event(self, buffer: HashBuffer) -> list or None:
        """
        Extracts relevant information from a FieldInputEvent, and constructs a grammar statement.

        Args:
            @param buffer: A list-like data structure that holds instrumentation events.
        """

        event = buffer.current()

        interaction = Interaction()

        event_data = event.get("Data")
        event_source = event_data.get("EventSource")
        is_ctrl_pressed = event_data.get("CtrlDown")
        is_shift_pressed = event_data.get("ShiftDown")
        field = event_data.get("FieldText")
        is_alt_pressed = event_data.get("AltDown")
        hash_list = [event.get("Hash")]
        '''
        An astute observer might notice that a Field Input Event also contains a variable for the Key that was pressed
        which is already represented by a char. The problem with this variable is that keys pressed in conjunction with 
        a modifier key have a different char representation (if you want to know more look at X11 documentation).
        
        So instead we need to get the KeyCode and use a dictionary that maps our KeyCode to the actual Key that was 
        pressed. That dictionary was taken from SneakySnek source code with a few modifications to work with our Linux
        environment. 
        '''
        key_code = event_data.get("KeyCode")
        key_pressed = keyboard_scan_code_mapping.get(key_code)

        if key_pressed is None:
            return None

        keys_pressed = ""

        if is_ctrl_pressed is True:
            keys_pressed += "CTRL "
        if is_shift_pressed is True:
            keys_pressed += "SHIFT "
        if is_alt_pressed is True:
            keys_pressed += "ALT "

        keys_pressed += str(key_pressed.value) + " "

        input_device = "Keyboard"
        input_action = keys_pressed
        tool_context = internal_plugin_to_grammar.get(event_source) + " : " + "Field(" + field + ")"

        if self.debug_:
            print("SourceEvent: ", event.get("Name"))
            print("PluginName:", event_source)
            print("MappingToGrammar: ", internal_plugin_to_grammar(event_source))

        interaction.set_fragment(input_device, GRAMMAR_TYPE.INPUT_DEVICE)
        interaction.set_fragment(input_action, GRAMMAR_TYPE.INPUT_ACTION)
        interaction.set_fragment(tool_context, GRAMMAR_TYPE.TOOL_CONTEXT)

        grammar_event = GrammarEvent(sentence=interaction,
                                     inferred=False,
                                     hash_list=hash_list,
                                     timestamp=event.get("Timestamp"),
                                     source_event=event.get("Event"))

        if self.debug_:
            grammar_event.debug()

        return [grammar_event]


class GhidraProgramActivatedEvent(EventConverter):
    """
    Takes  a GhidraProgramActivated Event and creates a grammar statement.

    Note that this grammar statement that is produced is completely inferred. Meaning that
    the event that is passed is incomplete, but knowing that it occurred in our
    experiment platform, there's only one way for this event to take place.

    This event only occurs when a user loads a different program. So, this would only happen in the experiment
    platform if the user clicked on the program tabs inside the Listing Panel.
    """

    def parse_event(self, buffer: HashBuffer) -> list or None:
        """
        Extracts relevant information from a GhidraProgramActivatedEvent and creates a grammar statement.

        Args:
            @param buffer: List-like data structure that holds instrumentation events.
        """
        event = buffer.current()

        interaction = Interaction()

        event_data = event.get("Data")
        program_name = event_data.get("ProgramName")

        if program_name is None:
            return None

        input_device, input_action, hash_list = get_input_fragments(buffer)

        if input_device is None:
            return self.inferred_program_activated_events(buffer, )

        tool_context = "CodeBrowser" + " : " + " ProgramTab(" + "\"" + program_name + "\"" + ")"
        tool_action = "Ghidra load \"" + program_name + "\""

        interaction.set_sentence(input_device, input_action, tool_context, tool_action)
        hash_list.insert(0, event.get("Hash"))

        grammar_event = GrammarEvent(sentence=interaction,
                                     inferred=False,
                                     hash_list=hash_list,
                                     timestamp=event.get("Timestamp"),
                                     source_event=event.get("Event"))

        if self.debug_:
            grammar_event.debug()

        return [grammar_event]

    def inferred_program_activated_events(self, buffer: HashBuffer) -> list:

        program_name = buffer.current().get("Data").get("ProgramName")
        inferred_left_click = Interaction()
        inferred_middle_click = Interaction()
        input_device = "Mouse"
        input_action_left = "Left Click"
        input_action_middle = "Middle Click"
        tool_context = "CodeBrowser" + " : " + " ProgramTab(" + "\"" + program_name + "\"" + ")"
        tool_action = "Ghidra load \"" + program_name + "\""

        inferred_left_click.set_sentence(input_device, input_action_left, tool_context, tool_action)
        inferred_middle_click.set_sentence(input_device, input_action_middle, tool_context, tool_action)

        hash_list = [buffer.current().get("Hash")]
        event = buffer.current()

        grammar_event_left = GrammarEvent(sentence=inferred_left_click,
                                          inferred=True,
                                          hash_list=hash_list,
                                          timestamp=event.get("Timestamp"),
                                          source_event=event.get("Event"))
        grammar_event_middle = GrammarEvent(sentence=inferred_middle_click,
                                            inferred=True,
                                            hash_list=hash_list,
                                            timestamp=event.get("Timestamp"),
                                            source_event=event.get("Event"))

        if self.debug_:
            grammar_event_middle.debug()
            grammar_event_left.debug()

        return [grammar_event_left, grammar_event_middle]


# TODO Function Graph vertex click events might act different than expected. Need to double check on VM. Disabling event converter for now.
class FunctionGraphVertexClickEvent(EventConverter):
    """
    This class takes a FunctionGraphVertexClickEvent and converts it into a grammar statement.

    This event is created from internal instrumentation. It occurs whenever a user decides to interact with a Function
    Graph Block. One thing to note is that this event is only produced when a user left/middle clicks. But due to
    the json event we can't tell which one occurred. So we leave the event with an ambiguous Input device action.
    """

    def parse_event(self, buffer: HashBuffer) -> list or None:
        """
        Extracts relevant information from a FunctionGraphVertexClickEvent and constructs a grammar statement.

        Args:
            @param buffer: list-like structure that holds instrumentation events
        """

        input_device, input_action, hash_list = get_input_fragments(buffer)

        if input_device is None:
            return self.inferred_function_graph_vertex_click_events(buffer)

        event = buffer.current()
        event_count = event.get("Data").get("MouseClickCount")
        hash_list.insert(0, event.get("Hash"))

        if event_count == 1:
            mouse_action = "Click"
        elif event_count == 2:
            mouse_action = "DoubleClick"
        else:
            mouse_action = "MultipleClicks"

        interaction = Interaction()

        event_data = event.get("Data")
        vertex_title = event_data.get("VertexTitle")
        event_source = event_data.get("EventSource")

        tool_context = internal_plugin_to_grammar.get(event_source) + " : " + "Vertex(" + vertex_title + ")"
        tool_action = internal_plugin_to_grammar.get(event_source) + " : " + "SelectionChanged : " + \
                      "Vertex(" + vertex_title + ")"

        if self.debug_:
            print("PluginName:", event_source)
            print("MappingToGrammar: ", internal_plugin_to_grammar.get(event_source))

        interaction.set_sentence(input_device, input_action + " " + mouse_action, tool_context, tool_action)

        grammar_event = GrammarEvent(sentence=interaction,
                                     inferred=False,
                                     hash_list=hash_list,
                                     timestamp=event.get("Timestamp"),
                                     source_event=event.get("Event"))

        if self.debug_:
            grammar_event.debug()

        return [grammar_event]

    # TODO: Make sure the middle click tool_action fragment is the same as the left click.
    def inferred_function_graph_vertex_click_events(self, buffer: HashBuffer) -> list:

        event = buffer.current()
        event_data = event.get("Data")
        vertex_title = event_data.get("VertexTitle")
        event_source = event_data.get("EventSource")

        inferred_left_click = Interaction()
        inferred_middle_click = Interaction()
        hash_list = [event.get("Hash")]

        tool_context = internal_plugin_to_grammar.get(event_source) + " : " + "Vertex(" + vertex_title + ")"

        inferred_left_click.set_sentence("Mouse", "Left Click", tool_context,
                                         internal_plugin_to_grammar.get(event_source) + " : " +
                                         "SelectionChanged : " + "Vertex(" + vertex_title + ")")
        inferred_middle_click.set_sentence("Mouse", "Middle Click", tool_context,
                                           internal_plugin_to_grammar.get(event_source) + " : " +
                                           "SelectionChanged : " + "Vertex(" + vertex_title + ")")

        grammar_event_left = GrammarEvent(sentence=inferred_left_click,
                                          inferred=True,
                                          hash_list=hash_list,
                                          timestamp=event.get("Timestamp"),
                                          source_event=event.get("Event"))

        grammar_event_middle = GrammarEvent(sentence=inferred_middle_click,
                                            inferred=True,
                                            hash_list=hash_list,
                                            timestamp=event.get("Timestamp"),
                                            source_event=event.get("Event"))

        return [grammar_event_left, grammar_event_middle]


class FunctionGraphEdgePickEvent(EventConverter):
    """
    This class takes a FunctionGraphEdgePickEvent and returns a grammar statement.

    The event is produced whenever someone left-clicks on an edge between two blocks on the function graph; or when
    someone interacts with another part of Ghidra, and a deselect of the edge occurs.

    When an edge is clicked, then that edge is then thickened. When it is unpicked, the edge goes back to its normal
    state.

    When the latter happens the picked_state value is set to "PICKED". Since different actions can cause for the edge to be
    "UNPICKED" we don't consider that case since the input device, and input action can be vastly different things.
    """

    def parse_event(self, event_frame, index) -> Interaction or None:
        """
        Extracts relevant information from a FunctionGraphEdgePickEvent and constructs a grammar statement.

        Args:
            @param event_frame: list structure that holds json events.
            @param index: Index of event_frame of where the event being converted is located.
        """
        event = event_frame[index][0]

        interaction = Interaction()

        event_data = event.get("FunctionGraphEdgePickEvent")
        event_source = event_data.get("EventSource")
        picked_state = event_data.get("EdgePickedState")
        starting_address = event_data.get("StartingAddress")
        ending_address = event_data.get("EndingAddress")

        '''
        Since we don't know what could've caused the edge "UNPICKED" state, we ignore this case.
        '''
        if picked_state == "UNPICKED":
            return None

        input_device = "Mouse"
        input_action = "Left" + " *(Click | DoubleClick | MultipleClicks)"
        tool_context = internal_plugin_to_grammar.get(
            event_source) + " : " + "Edge(" + starting_address + ", " + ending_address + ")"

        if self.debug_:
            print("PluginName:", event_source)
            print("MappingToGrammar: ", internal_plugin_to_grammar(event_source))

        interaction.set_fragment(input_device, GRAMMAR_TYPE.INPUT_DEVICE)
        interaction.set_fragment(input_action, GRAMMAR_TYPE.INPUT_ACTION)
        interaction.set_fragment(tool_context, GRAMMAR_TYPE.TOOL_CONTEXT)

        return interaction


class VerticalScrollbarAdjustmentEvent(EventConverter):
    """
    This class takes VerticalScrollbarAdjustmentEvents and constructs grammar statements.

    Since each time a scroll bar is adjusted, this class considers all events that occurred within
    2 seconds of each other to be part of one scroll bar adjustment event. The 2 seconds is arbitrary and might
    need additional testing to find a better heuristic.

    One thing to note is that scroll bar events can be generated due to how navigation works in Ghidra. So it could've
    occurred due to some interaction not involving the scroll bar.
    """

    def parse_event(self, buffer: HashBuffer) -> list or None:
        """
        Constructs a grammar statement based on all vertical scroll bar events that passed a heuristic we defined.
        This function then consumes all events that were used by the grammar statement.

        Args:
            @param buffer: list-like data structure that holds instrumentation events
        """

        '''
        An scroll bar event can be consumed by a previous scroll bar event.
        '''
        if buffer.current().get("Consumed"):
            return None

        event = buffer.current()
        event_data = event.get("Data")

        last_scroll_event, hash_list = self.consume_scroll_events(buffer)

        if len(hash_list) < 2:
            print("[INFO] Hash List less than 2, assuming ghidra event generated. Skipping...")
            return None

        hash_list.insert(0, event.get("Hash"))

        tool_context = internal_plugin_to_grammar.get(event_data.get("EventSource")) + " : " + "ScrollbarLocation" + \
                       "[" + str(event_data.get("ScrollbarLocation")) + "]"

        tool_action_scroll_position = "ScrollbarLocation" + "[" + \
                                      str(last_scroll_event.get("Data").get("ScrollbarLocation")) + "]"
        tool_action = internal_plugin_to_grammar.get(
            event_data.get("EventSource")) + " : " + tool_action_scroll_position

        return self.generate_inferred_statements(event, tool_context, tool_action, hash_list)

    def generate_inferred_statements(self, event: dict, tool_context: str, tool_action: str, hash_list: list):

        inferred_drag = Interaction()
        inferred_left_click = Interaction()
        inferred_mouse_wheel_up = Interaction()
        inferred_mouse_wheel_down = Interaction()

        inferred_drag.set_sentence("Mouse", "Drag", tool_context, tool_action)
        inferred_left_click.set_sentence("Mouse", "Left Click", tool_context, tool_action)
        inferred_mouse_wheel_up.set_sentence("Mouse", "MouseWheel Up", tool_context, tool_action)
        inferred_mouse_wheel_down.set_sentence("Mouse", "MouseWheel Down", tool_context, tool_action)

        grammar_event_drag = GrammarEvent(sentence=inferred_drag,
                                          inferred=True,
                                          hash_list=hash_list,
                                          timestamp=event.get("Timestamp"),
                                          source_event=event.get("Event"))

        grammar_event_left_click = GrammarEvent(sentence=inferred_left_click,
                                                inferred=True,
                                                hash_list=hash_list,
                                                timestamp=event.get("Timestamp"),
                                                source_event=event.get("Event"))

        grammar_event_mouse_wheel_down = GrammarEvent(sentence=inferred_mouse_wheel_down,
                                                      inferred=True,
                                                      hash_list=hash_list,
                                                      timestamp=event.get("Timestamp"),
                                                      source_event=event.get("Event"))

        grammar_event_mouse_wheel_up = GrammarEvent(sentence=inferred_mouse_wheel_up,
                                                    inferred=True,
                                                    hash_list=hash_list,
                                                    timestamp=event.get("Timestamp"),
                                                    source_event=event.get("Event"))

        return [grammar_event_left_click, grammar_event_mouse_wheel_up, grammar_event_mouse_wheel_down,
                grammar_event_drag]

    def consume_scroll_events(self, buffer: HashBuffer) -> (dict, list):
        """
        This functions returns all scroll events that meet the following criteria.

        When the initial scroll event is evaluated to valid, we then check the next occurring scroll event and check if
        it appeared within 2 seconds. If it did, then we add it to the list of scroll events we are returning and we
        consider it to be the new initial scroll event and repeat the process.

        Note that this function can possibly return an empty list.
        """

        last_scroll_event = buffer.current()

        if self.debug_:
            print("[DEBUG] Initial Vertical Scroll Bar Event, ", last_scroll_event)

        index = buffer.get_index()
        event_frame = buffer.get_event_list()
        hash_list = []

        for i in range(index + 1, len(event_frame)):

            event = event_frame[i]

            if event.get("Name") == "VerticalScrollbarAdjustmentEvent":
                if event.get("Data").get("EventSource") == last_scroll_event.get("Data").get("EventSource"):

                    last_scroll_event_time = last_scroll_event.get("Timestamp")
                    curr_scroll_event_time = event.get("Timestamp")

                    time_diff = curr_scroll_event_time - last_scroll_event_time

                    if self.debug_:
                        print("[DEBUG] Event being Checked: ", event)
                        print("[DEBUG] Time Difference: ", time_diff)

                    if time_diff < 5.0:
                        if self.debug_:
                            print("Event was consumed! Number of events consumed: ", len(hash_list) + 1)
                        event["Consumed"] = True
                        hash_list.append(event.get("Hash"))
                        last_scroll_event = event
                    else:
                        return last_scroll_event, hash_list

        return last_scroll_event, hash_list

    def get_scroll_input_fragments(self, buffer: HashBuffer) -> (str, str, str) or (str, str, None):

        event_list = buffer.get_event_list()
        index = buffer.get_index()

        for i in reversed(range(index)):

            event = event_list[i]

            if event.get("Name") == "MouseEvent":
                mouse_event_data = event.get("Data")

                if mouse_event_data.get("EventName") == "MOVE":
                    return "Mouse", "Drag", event.get("Hash")
                if mouse_event_data.get("EventName") == "CLICK":
                    return "Mouse", "Left Click", event.get("Hash")
                if mouse_event_data.get("EventName") == "SCROLL":
                    mouse_wheel_dir = mouse_event_data.get("Direction")
                    mouse_wheel_dir = mouse_wheel_dir.lower()
                    mouse_wheel_dir = mouse_wheel_dir.capitalize()
                    return "Mouse", "MouseWheel " + mouse_wheel_dir, event.get("Hash")

        return "Mouse", "Drag", None

    # This function is now deprecated and no longer used...
    def create_scroll_tool_action(self, scroll_events):
        """
        This function creates the tool action fragment for VerticalScrollbarAdjustmentEvents.

        We consider one scroll bar sentence to be one where the user scrolls until they stop scrolling for more
        than 2 seconds. So for example, if someone scrolls for 1 second, then stops for another sec, and keeps scrolling;
        then that action will still be considered one scroll action.
        """

        diff = first_scroll_event_scroll_position - second_scroll_event_scroll_position

        if diff < 0:
            direction = "DOWN"
        else:
            direction = "UP"

        scroll_events[0][1] = True
        scroll_events[1][1] = True

        prev_scroll_event_position = second_scroll_event_scroll_position

        for i in range(2, len(scroll_events)):

            curr_scroll_event_position = scroll_events[i][0].get("VerticalScrollbarAdjustmentEvent").get(
                "ScrollbarLocation")

            diff = curr_scroll_event_position - prev_scroll_event_position

            if direction == "UP":
                if diff < 0:
                    return "ScrollLocation" + "[" + str(prev_scroll_event_position) + "]"
                else:
                    scroll_events[i][1] = True
                    prev_scroll_event_position = curr_scroll_event_position
            else:
                if diff > 0:
                    return "ScrollLocation" + "[" + str(prev_scroll_event_position) + "]"
                else:
                    scroll_events[i][1] = True
                    prev_scroll_event_position = curr_scroll_event_position

        return "ScrollLocation" + "[" + str(prev_scroll_event_position) + "]"


class MouseEnteredEvent(EventConverter):
    """
    This class takes a MouseEnteredEvent and converts it to a grammar statement.

    This event is generated by internal Ghidra instrumentation. This means that if a plugin isn't instrumented, it won't
    generate MouseEnteredEvents.

    Something to note is that for a lot of cases, that this will generate the same grammar statement as some
    WindowEvents.
    """

    def parse_event(self, buffer: HashBuffer) -> list or None:
        """
        Constructs a grammar statement from a MouseEnteredEvent.

        Args:
            @param buffer: list-like data structure that holds instrumentation events.
        """

        event = buffer.current()
        interaction = Interaction()
        event_data = event.get("Data")
        plugin_name = event_data.get("EventSource")
        hash_list = [event.get("Hash")]

        input_device = "Mouse"
        input_action = "Move : Enter"
        tool_context = internal_plugin_to_grammar.get(plugin_name)

        if self.debug_:
            print("PluginName:", plugin_name)
            print("MappingToGrammar: ", internal_plugin_to_grammar.get(plugin_name))

        interaction.set_fragment(input_device, GRAMMAR_TYPE.INPUT_DEVICE)
        interaction.set_fragment(input_action, GRAMMAR_TYPE.INPUT_ACTION)
        interaction.set_fragment(tool_context, GRAMMAR_TYPE.TOOL_CONTEXT)

        grammar_event = GrammarEvent(sentence=interaction,
                                     inferred=False,
                                     hash_list=hash_list,
                                     timestamp=event.get("Timestamp"),
                                     source_event=event.get("Event"))

        return [grammar_event]


class MouseExitedEvent(EventConverter):
    """
    This class takes a MouseExitedEvent and converts it to a grammar statement.

    This event is generated by internal Ghidra instrumentation. This means that if a plugin isn't instrumented, it won't
    generate MouseExitedEvents.

    Something to note is that for a lot of cases, that this will generate the same grammar statement as some
    WindowEvents.
    """

    def parse_event(self, buffer: HashBuffer) -> list or None:
        """
        Constructs a grammar statement based on MouseExitedEvent

        Args:
            @param buffer: list-like data structure that holds instrumentation events
        """

        event = buffer.current()
        interaction = Interaction()
        event_data = event.get("Data")
        plugin_name = event_data.get("EventSource")
        hash_list = [event.get("Hash")]

        input_device = "Mouse"
        input_action = "Move : Exit"
        tool_context = internal_plugin_to_grammar.get(plugin_name)

        if self.debug_:
            print("PluginName:", plugin_name)
            print("MappingToGrammar: ", internal_plugin_to_grammar.get(plugin_name))

        interaction.set_fragment(input_device, GRAMMAR_TYPE.INPUT_DEVICE)
        interaction.set_fragment(input_action, GRAMMAR_TYPE.INPUT_ACTION)
        interaction.set_fragment(tool_context, GRAMMAR_TYPE.TOOL_CONTEXT)

        grammar_event = GrammarEvent(sentence=interaction,
                                     inferred=False,
                                     hash_list=hash_list,
                                     timestamp=event.get("Timestamp"),
                                     source_event=event.get("Event"))

        return [grammar_event]


def load_field_location_events(buffer: HashBuffer) -> list:
    """
    This loads all field location events that occurred within .5 secs of the event that is located
    in event_frame with the index that is passed.

    @param buffer: HashBuffer data structure that contains instrumentation events
    """

    field_location_events = []
    source_event_time = buffer.current().get("Timestamp")
    index = buffer.get_index()
    event_list = buffer.get_event_list()
    '''
    We consider both directions of event_frame since field location events can occur within a 
    "bubble" surrounding the source event.
    '''
    for i in range(index + 1, len(event_list)):

        event = event_list[i]

        if event.get("Name") == "FieldLocationEvent":

            field_location_events.append(event)

        else:

            curr_event_time = event.get("Timestamp")

            diff = curr_event_time - source_event_time

            if diff > 1.5:
                break

    for i in reversed(range(index)):

        event = event_list[i]

        if event.get("Name") == "FieldLocationEvent":

            field_location_events.insert(0, event)

        else:

            curr_event_time = event.get("Timestamp")

            diff = source_event_time - curr_event_time

            if diff > 1.5:
                break

    return field_location_events


def get_field_from_plugin(field_events, plugin_name) -> (str, str):
    """
    Given a list of FieldLocationEvents, this function then returns the field-text value of the
    FieldLocationEvent that occurred in the given plugin.
    """

    for event in field_events:

        event_data = event.get("Data")
        event_source = event_data.get("EventSource")

        if event_source == plugin_name:
            # event["Consumed"] = True
            return event_data.get("FieldText"), event.get("Hash")

    '''
    This is possible in certain situations but for the most time it shouldn't.
    '''
    return "*(unknown)", ""


def get_input_fragments(buffer: HashBuffer) -> (str, str, list) or (None, None, None):
    src_timestamp = buffer.current().get("Timestamp")
    event_list = buffer.get_event_list()
    index = buffer.get_index()

    for i in reversed(range(index)):
        if event_list[i].get("Name") == "MouseEvent":
            curr_timestamp = event_list[i].get("Timestamp")
            diff = src_timestamp - curr_timestamp
            if diff > 1:
                return None, None, None
            elif event_list[i].get("Data").get("EventName") == "CLICK":
                mouse_event = event_list[i]
                mouse_data = mouse_event.get("Data")
                mouse_button = mouse_data.get("Button")
                mouse_button = mouse_button.lower()
                mouse_button = mouse_button.capitalize()
                input_device = "Mouse"
                input_action = mouse_button
                hash_list = [mouse_event.get("Hash")]

                return input_device, input_action, hash_list

    return None, None, None
