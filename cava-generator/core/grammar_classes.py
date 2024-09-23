"""
File:    grammar_classes.py
Author:  Froylan Maldonado
Email:   froylan.g.maldonado.civ@us.navy.mil
Created: September 2024
Description:
    Grammar classes that event_converter uses to construct grammars.
"""

from abc import ABCMeta, abstractmethod
from core.misc import *


class CavaGrammar:
    __metaclass__ = ABCMeta

    @abstractmethod
    def __str__(self) -> str:
        """Return string representation of grammar statement"""

    @property
    def grammarType(self):
        """Return grammar type"""

    @abstractmethod
    def set_fragment(self, fragment, grammar_type=None):
        """Set fragment of grammar statement"""

    @abstractmethod
    def get_fragment(self, grammar_type=None):
        """Returns the fragment that is set. Returns an empty string is not set."""


class Interaction(CavaGrammar):

    def __init__(self):
        self.grammarType_ = GRAMMAR_TYPE.INTERACTION
        self.input_device_ = InputDevice()
        self.input_action_ = InputAction()
        self.tool_context_ = ToolContext()
        self.action_ = Action()

        self.type_to_fragment = {
            GRAMMAR_TYPE.INPUT_DEVICE: self.input_device_,
            GRAMMAR_TYPE.INPUT_ACTION: self.input_action_,
            GRAMMAR_TYPE.TOOL_CONTEXT: self.tool_context_,
            GRAMMAR_TYPE.ACTION: self.action_}

    def set_fragment(self, fragment, grammar_type=None):
        if grammar_type is None:
            print(f"Need to specify grammar type for fragment.")
            exit(1)
        if fragment is None:
            print(f"[ERROR] Fragment is of type None! Exiting...")
            exit(1)

        self.type_to_fragment[grammar_type].set_fragment(fragment)

    def set_sentence(self, input_device, input_action, tool_context, tool_action):
        self.input_device_.set_fragment(input_device)
        self.input_action_.set_fragment(input_action)
        self.tool_context_.set_fragment(tool_context)
        self.action_.set_fragment(tool_action)

    def get_fragment(self, grammar_type):
        return self.type_to_fragment[grammar_type]

    def __str__(self) -> str:
        grammar_string = str(self.input_device_) + " : " + str(self.input_action_)

        if str(self.tool_context_) != "":
            grammar_string = grammar_string + " > " + str(self.tool_context_)
            if str(self.action_) != "":
                grammar_string = grammar_string + " > " + str(self.action_)

        return grammar_string

    def grammarType(self):
        return self.grammarType_


class InputDevice(CavaGrammar):

    def __init__(self):
        self.grammarType_ = GRAMMAR_TYPE.INPUT_DEVICE
        self.device_ = ""

    def set_fragment(self, device, grammar_type=None):
        self.device_ = device

    def get_fragment(self, grammar_type=None):
        return self.device_

    def grammarType(self):
        return self.grammarType_

    def __str__(self) -> str:
        return self.device_


class InputAction(CavaGrammar):

    def __init__(self):
        self.grammarType_ = GRAMMAR_TYPE.INPUT_ACTION
        self.input_action_ = ""

    def set_fragment(self, action, grammar_type=None):
        self.input_action_ = action

    def get_fragment(self, grammar_type=None):
        return self.input_action_

    def grammarType(self):
        return self.grammarType_

    def __str__(self) -> str:
        return self.input_action_


class ToolContext(CavaGrammar):

    def __init__(self):
        self.grammarType_ = GRAMMAR_TYPE.TOOL_CONTEXT
        self.context_ = ""

    def set_fragment(self, context, grammar_type=None):
        self.context_ = context

    def get_fragment(self, grammar_type=None):
        return self.context_

    def grammarType(self):
        return self.grammarType_

    def __str__(self) -> str:
        return self.context_


class Action(CavaGrammar):

    def __init__(self):
        self.grammarType_ = GRAMMAR_TYPE.ACTION
        self.action_ = ""

    def set_fragment(self, action, grammar_type=None):
        self.action_ = action

    def get_fragment(self, grammar_type=None):
        return self.action_

    def grammarType(self):
        return self.grammarType_

    def __str__(self) -> str:
        return self.action_
