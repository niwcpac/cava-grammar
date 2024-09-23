/**
 interaction grammar
 Version: 0.1
 Author: Sunny Fugate

 Grammar for user/tool interactions within the Ghidra RE toolkit
 This grammar is incomplete and is likely to have errors while details are
 being developed.  Currently this is written to be a Context_free grammar.

 At a high level, the purpose of this grammar is to describe user interactions from the input device
 mediated by the Ghidra tool views and affordances which then cause a tool action to be performed

______________________________________________
Technical notes:
Grammar is written to be used with ANTLR (ANother Tool for Language Recognition)

Some helpful guides on grammar construction:
https://www.willowtreeapps.com/craft/an_introduction_to_language_lexing_and_parsing_with_antlr

https://github.com/antlr/antlr4/blob/master/doc/lexicon.md
https://github.com/antlr/antlr4/blob/master/doc/grammars.md
https://github.com/antlr/antlr4/blob/master/doc/lexer_rules.md
https://github.com/antlr/antlr4/blob/master/doc/parser_rules.md

Other helpful guides:
https://blog.knoldus.com/how_to_write_grammar_for_your_own_language_with_antlr_part_i_setting_up_the_environment_intellij_with_antlr/
https://blog.knoldus.com/creating_a_dsl_domain_specific_language_using_antlr_part_ii_writing_the_grammar_file/


**/
grammar interaction;

/*
 * Parser Rules
 */

/* Root rule defining basic statement in our interaction grammar

    The tool_action is optional as external instrumentation will not necessarily be able to detect whether or not
    Ghidra interpreted the intended action by the user.

    Examples:
        Mouse : Left Click > Ghidra : Menu : File : Open > ExecuteMenuAction : File : Open
*/
interaction : input_device COLON input_action RANGLE tool_context (RANGLE tool_action)? ;

// Define key input devices and actions
input_device : Mouse | Keyboard | Eye ;
input_action : mouse_action | keyboard_action | eye_action ;

/*
 Define mouse actions per button
 There are other mouse buttons/actions feasible (e.g. tripple click), but probably arent' relevant for Ghidra
 This current simplistic grammar also doesn't include mouse screen location information which may be
 different than application context information.
*/
mouse_action : mouse_button mouse_button_interaction | mouse_scroll_wheel mouse_scroll_wheel_interaction ;
mouse_button : Left | Right | Middle ; //TODO: additional buttons probably are not needed
mouse_button_interaction : Click | DoubleClick | PressDown | Release | Drag ; //TODO: hover?
mouse_scroll_wheel : Scroll;
mouse_scroll_wheel_interaction : Up | Down ;


/*
 TODO: define eye actions
*/
eye_action : TODO ; //TODO: define eye actions

/*
 Define keyboard actions
 So, this grammar currently ignores key press vs key release for the time being... might need extended
 The $terminal$ is intended just to provide shorthand for 'look this up elsewhere'
 It might be worth representing directly, but would need to be verbose __ perhaps as a separate file?
 Should be able to represent items such as:
 - key_typed: "g"
 - text_entry: "hello"
 - hotkey: "g"
 - hotkey: "Ctrl_Shift_L"
 One outstanding issue with this approach is that some items in Ghidra can be either a hotkey or a single key
 depending on their input context
*/
keyboard_action : key_typed | hotkey | text_entry ;
key_typed : KEY_CODE ;
text_entry : KEY_CODE+;
hotkey : ghidra_hotkey ;

ghidra_hotkey : TODO ; //TODO: ghidra hotkeys, which requires ascii table

/*
 Define Ghidra tool context which describes an associated Ghidra plugin, view, and loaded program
 A complexity here is that Ghidra's interface is often layered, so that a popover or context menu is contextual
 and appears only within a particular tool context.  For example:  A right click an address in the Code Browser
 brings up a context menu with menu items that depend on the fact that it was an address which was clicked and not
 a value.  We handle this by allowing display of a sequence of nested tool contexts:
 e.g. CodeBrowser(AddressContextMenu)
 This might need to be made explicit as many combinations are non_sensical.
 */
tool_context
    : tool_view
    | tool_view ProgramName //Optionally specify the loaded program
    ;

tool
    : Ghidra
    | CodeBrowserPlugin
    | DecompilePlugin
    | CavaListenerPlugin
    | FunctionGraphPlugin
    | GoToServicePlugin
    | CommentsPlugin
    | DataWindowPlugin
    ; //TODO: add to this list as we include additional tools

tool_view
    : tool
    | Ghidra COLON ghidra_view
    | CodeBrowserPlugin COLON code_browser_plugin_view
    | DecompilePlugin COLON decompile_plugin_view
    | CavaListenerPlugin COLON cava_listener_plugin_view
    | FunctionGraphPlugin COLON function_graph_plugin_view
    | GoToServicePlugin COLON goto_service_plugin_view
    | CommentsPlugin COLON comments_plugin_view
    | DataWindowPlugin COLON data_window_plugin_view
    ;

tool_action
    : tool COLON NoActionTaken
    | Ghidra COLON ghidra_action
    | CodeBrowserPlugin COLON code_browser_plugin_action
    | DecompilePlugin COLON decompile_plugin_action
    | CavaListenerPlugin COLON cava_listener_plugin_action
    | FunctionGraphPlugin COLON function_graph_plugin_action
    | GoToServicePlugin COLON goto_service_plugin_action
    | CommentsPlugin COLON comments_plugin_action
    | DataWindowPlugin COLON data_window_plugin_action
    ; //TODO additional plugins?

ghidra_view
    : Menu (COLON ghidra_menu)?
    | Toolbar COLON ghidra_toolbar
    ; // TODO additional top level ghidra views (e.g. dockable window layout/arrangement?)

ghidra_action
    : ExecuteMenuAction COLON ghidra_menu_action
    | ExecuteToolbarAction COLON ghidra_toolbar_action
    |
    ;

//TODO: need to define general purpose actions which are shared across

ExecuteMenuAction : 'ExecuteMenuAction' ;
ExecuteToolbarAction : 'ExecuteToolbarAction' ;
ExitTab : 'ExitTab' ;

ProgramLocation : ProgramAddress | LineNumber ;
HighlightChanged : 'HighlightChanged' ;

/*
Miscellaneous grammar rules that are used by other grammars
*/

// Meant to be used as a catch all for plugin options
PluginOption : GenericText ;

// scrollBar grammar
scrollBarLocation
    : HorizontalScrollBarLocation
    | VerticalScrollBarLocation
    ;

// Generic Toolbar grammar, that can be used by any plugin
toolbar_item
    : ProgramTab (COLON ExitTab)?
    | PluginOption
    | ExitPlugin
    ;


listing_view_element
    : ProgramAddress
    | PluginElement
    ;

decompiler_element
    : PluginElement
    ;

program_range
    : LSQUAREBRACE LineNumber HYPHEN LineNumber RSQUAREBRACE
    | LSQUAREBRACE ProgramAddress HYPHEN ProgramAddress RSQUAREBRACE
    ;

code_browser_plugin_view
    : ListingView (COLON listing_view_element)?
    | Toolbar COLON toolbar_item
    | ContextMenu COLON listing_view_context_menu
    | scrollBarLocation
    ; //TODO

//TODO: create string literals and move string literals below
/*
Do we want this level of granularity in the grammar? Deducing the specifics such as type from a
mouse click event is not trivial.
*/
listing_view_context_menu
    : Bookmark
    | ClearCodeBytes
    | ClearWithOptions
    | Copy
    | CopySpecial
    | Paste
    | Comments (COLON ( SetEOLComment | SetPlateComment | SetPostComment
                | SetPreComment | SetRepeatableComment | Set | ShowHistory ))?
    | Data (COLON ( ChooseDataType | CreateArray | TerminatedCString | TerminatedUnicode
                  | 'byte'  | 'char' | 'double' | 'dword' | 'float' | 'int' | 'long'
                  | 'longdouble' | 'pointer' | 'qword' | 'string' | 'uint' | 'ulong' | 'word' ))?
    | InstructionInfo
    | PatchInstruction
    | ProcessorManual
    | ProcessorOptions
    | CreateFunction
    | CreateThunkFunction
    | EditFunction
    | Function (COLON ( SetStackDepthChange | RenameFunction | SetStackDepthChange | AnalyzeStack ))?
    | EditLabel
    | RemoveLabel
    | SetAssociatedLabel
    | ShowLabelHistory
    | EditFieldName
    | ClearRegisterValues
    | SetRegisterValues
    | CollapseAllData
    | ToggleExpandCollapseData
    | Colors (COLON SetColor)?
    | Fallthrough (COLON (AutoOverride | Set))?
    | References (COLON ( AddReferencesFrom | AddEdit | DeleteReferences
                        | CreateRegisterReference | DeleteMemoryReferences
                        | ShowReferencesTo GenericSymbol
                        | ShowReferencesToAddress | ShowCallTrees ))?
    ;


code_browser_plugin_action
    : ListingView COLON FocusChanged  // This implies the focus was changed to this plugin
    | ListingView COLON ViewChanged (ProgramLocation | program_range)
    | ListingView COLON HighlightChanged program_range
    | ListingView COLON SelectionChanged program_range
    | ListingView COLON ContextMenu
    ;

decompile_plugin_view
    : Decompiler (COLON decompiler_element)?
    | Toolbar COLON toolbar_item
    | scrollBarLocation
    ;

decompile_plugin_action
    : Decompiler COLON FocusChanged
    | Decompiler COLON ViewChanged (ProgramLocation | program_range)
    | Decompiler COLON HighlightChanged program_range
    | Decompiler COLON SelectionChanged program_range
    ;

cava_listener_plugin_view
    : TODO
    ;

cava_listener_plugin_action
    : TODO
    ;

function_graph_plugin_view
    : TODO
    ;
function_graph_plugin_action
    : TODO
    ;

goto_service_radiobutton
    : CaseSensitive
    | DynamicLabels
    ;

goto_service_button
    : OK
    | Cancel
    ;

goto_service_plugin_view
    // Note that this refers to the status of the radio button prior to any action taken on it
    : RadioButton COLON goto_service_radiobutton  (COLON (On | Off))
    | Button COLON goto_service_button
    |
    ;
goto_service_plugin_action
    : RadioButton COLON goto_service_radiobutton (COLON (On | Off))
    | ExitPlugin
    ;

comments_plugin_view
    : TODO
    ;

comments_plugin_action
    : TODO
    ;

data_window_plugin_view
    : TODO
    ;

data_window_plugin_action
    : TODO
    ;


//TODO: other program plugins

/* Ghidra Application */
ghidra_menu
    : File (COLON file_menu)?
    | Edit (COLON edit_menu)?
    | Analysis (COLON analysis_menu)?
    | Graph (COLON graph_menu)?
    | Navigation (COLON navigation_menu)?
    | Search (COLON search_menu)?
    | Select (COLON select_menu)?
    | Tools (COLON tools_menu)?
    | Window (COLON window_menu)?
    | Help (COLON help_menu)?
    ;

file_menu
    : Open
    | Close ProgramName
    | CloseOthers
    | CloseAll
    | Save ProgramName (As)?
    | SaveAll
    | ImportFile
    | BatchImport
    | OpenFileSystem
    | AddToProgram
    | ExportProgram
    | LoadPDBFile
    | ParseCSource
    | Print
    | PageSetup
    | Configure
    | SaveTool
    | SaveToolAs
    | Export (COLON
        (ExportTool | ExportDefaultTool))?
    | CloseTool
    | ExitGhidra
    ;

edit_menu
    : ToolOptions
    | OptionsFor ProgramName
    | ClearCodeBytes
    | ClearWithOptions
    | ClearFlowAndRepair
    | Undo
    | Redo
    ;

analysis_menu
    : AutoAnalyze ProgramName
    | AnalyzeAllOpen
    | OneShot (COLON analysis_one_shot_menu)?
    | AnalyzeStack
    ;

analysis_one_shot_menu
    : ASCIIStrings
    | AggressiveInstructionFinder
    | CallConventionID
    | CallFixupInstaller
    | CreateAddressTables
    | DWARF
    | DecompilerParameterID
    | DecompilerSwitchAnalysis
    | DemanglerGNU
    | EmbeddedMedia
    | FunctionID
    | FunctionStartSearch
    | NonReturningFunctionsDiscovered
    | SharedReturnCalls
    | Stack
    ;

graph_menu
    : BlockFlow
    | CodeFlow
    | Calls
    | CallsUsingModel (COLON graph_calls_using_model_menu)?
    | AppendGraph
    | ReuseGraph
    | ShowLocation
    | GraphOutput (COLON
        (DefaultGraphDisplay | GraphExport))?
    ;

graph_calls_using_model_menu
    : IsolatedEntry
    | MultipleEntry
    | OverlappedCode
    | PartitionedCode
    ;

navigation_menu
    : ClearHistory
    | NextHistoryFunction
    | PreviousHistoryFunction
    | GoTo
    | GoToSymbolSource
    | GoToNextFunction
    | GoToPreviousFunction
    | GoToProgram
    | GoToLastActiveProgram
    | GoToLastActiveComponent
    | NextSelectedRange
    | PreviousSelectedRange
    | NextHighlightRange
    | PreviousHighlightRange
    | NextColorRange
    | PreviousColorRange
    ;

search_menu
    : LabelHistory
    | ProgramText
    | RepeatTextSearch
    | Memory
    | RepeatMemorySearch
    | ForMatchingInstructions (COLON
        (ExcludeOperands | IncludeOperands | IncludeOperandsExceptConstants))?
    | ForAddressTables
    | ForDirectTables
    | ForInstructionPatterns
    | ForScalars
    | ForStrings
    ;

select_menu
    : ProgramChanges
    | AllFlowsFrom
    | AllFlowsTo
    | LimitedFlowsFrom
    | LimitedFlowsTo
    | Subroutine
    | DeadSubroutines
    | Function
    | FromHighlight
    | ProgramHighlight (COLON
        (EntireSelection | Clear | AddSelection | SubtractSelection))?
    | ScopedFlow (COLON
        (ForwardScopedFlow | ReverseScopedFlow))?
    | Bytes
    | AllInView
    | ClearSelection
    | Complement
    | Data
    | Instructions
    | Undefined
    | CreateTableFromSelection
    | RestoreSelection
    | BackRefs
    | ForwardRefs
    ;

tools_menu
    : ProcessorManual
    | ProgramDifferences
    | GenerateChecksums
    ;

window_menu
    : Bookmarks
    | BundleManager
    | Bytes COLON ProgramName
    | ChecksumGenerator
    | Comments
    | Console
    | DataTypeManager
    | DataTypePreview
    | Decompiler
    | DefinedData
    | DefinedStrings
    | DisassembledView
    | EquatesTable
    | ExternalPrograms
    | FunctionCallGraph
    | FunctionCallTrees
    | FunctionGraph
    | FunctionTags
    | Functions
    | Listing COLON ProgramName
    | MemoryMap
    | ProgramTrees
    | Python
    | RegisterManager
    | RelocationTable
    | ScriptManager
    | SymbolReferences
    | SymbolTable
    | SymbolTree
    ;

help_menu
    : Contents
    | GhidraAPIHelp
    | UserAgreement
    | InstalledProcessors
    | AboutGhidra
    | About ProgramName
    ;

ghidra_menu_action
    : file_menu
    | edit_menu
    | analysis_menu
    | graph_menu
    | navigation_menu
    | search_menu
    | select_menu
    | tools_menu
    | window_menu
    | help_menu
    ;

ghidra_toolbar
    : Save
    | Back
    | Forward
    ; //TODO

ghidra_toolbar_action
    : TODO
    ; //TODO

/*
listing_view : field
             | listing_context_menu
             ;

field : LABEL
      | ADDRESS
      | BYTES
      | MNEMONIC
      | OPERANDS
      | EOL_COMMENT
      | XREF_HEADER
      | XREF
      ;

listing_context_menu : label_context_menu
                     | address_context_menu
                     | bytes_context_menu
                     | mnemonic_context_menu
                     | operands_context_menu
                     ;


label_context_menu : TODO ;
address_context_menu : TODO ;
bytes_context_menu : TODO ;
mnemonic_context_menu : TODO ;
operands_context_menu : TODO ;
*/



/******************************
 * Lexer Rules ;
 ******************************/
DOT : '.' ;
COLON : ':' ;
RANGLE : '>' ;
LBRACE : '{' ;
RBRACE : '}' ;
TODO : 'TODO' ;
AND : '&&' ;
LSQUAREBRACE : '[' ;
RSQUAREBRACE : ']' ;
HYPHEN : '-' ;

//Input Devices
Mouse : 'Mouse' ;
Keyboard : 'Keyboard' ;
Eye : 'Eye' ;

//Mouse Buttons
Left : 'Left' ;
Right : 'Right' ;
Middle : 'Middle' ;

//Mouse Button Interactions
Click : 'Click' ;
DoubleClick : 'DoubleClick' ;
PressDown : 'PressDown' ;
Release : 'Release' ;
Drag : 'Drag' ;
Hover : 'Hover' ;
Scroll : 'Scroll' ;
Down : 'Down' ;
Up : 'Up' ;


//Application Contexts
Ghidra : 'Ghidra' ;
CodeBrowserPlugin : 'CodeBrowserPlugin' ;
DecompilePlugin : 'DecompilePlugin' ;
CavaListenerPlugin : 'CavaListenerPlugin' ;
FunctionGraphPlugin : 'FunctionGraphPlugin' ;
GoToServicePlugin : 'GoToServicePlugin' ;
CommentsPlugin : 'CommentsPlugin' ;
DataWindowPlugin : 'DataWindowPlugin' ;

//Views
ListingView : 'ListingView' ;
Toolbar : 'Toolbar' ;
Menu : 'Menu' ;
ExitPlugin : 'ExitPlugin';
ContextMenu : 'ContextMenu' ;

//Misc Lexer rules
HorizontalScrollBarLocation : 'HorizontalScrollBarLocation['[0-9]+']' ;
VerticalScrollBarLocation : 'VerticalScrollBarLocation['[0-9]+']' ;
ProgramTab : 'ProgramTab' ;

//Generic Plugin actions
SelectionChanged : 'SelectionChanged' ;
ViewChanged : 'ViewChanged' ;
FocusChanged : 'FocusChanged' ;

/*
 * Ghidra Application Menus
 *
 * Application Menu maps the literal string from the interface to a token
 */
//Application Menu
File : 'File' ;
Edit : 'Edit' ;
Analysis : 'Analysis' ;
Graph : 'Graph' ;
Navigation : 'Navigation' ;
Search : 'Search' ;
Select : 'Select' ;
Tools : 'Tools' ;
Window : 'Window' ;
Help : 'Help' ;

//Application File Menu
Open : 'Open' ;
Close : 'Close' ;
CloseOthers : 'Close Others' ;
CloseAll : 'Close All' ;
Save : 'Save' ;
As : 'As' ;
SaveAll : 'Save All' ;
ImportFile : 'Import File' ;
BatchImport : 'Batch Import' ;
OpenFileSystem : 'Open File System' ;
AddToProgram : 'Add To Program' ;
ExportProgram : 'Export Program' ;
LoadPDBFile : 'Load PDB File' ;
ParseCSource : 'Parse C Source' ;
Print : 'Print' ;
PageSetup : 'Page Setup' ;
Configure : 'Configure' ;
SaveTool : 'Save Tool' ;
SaveToolAs : 'Save Tool As' ;
Export : 'Export' ;
    //File:Export Menu
    ExportTool : 'Export Tool' ;
    ExportDefaultTool : 'Export Default Tool' ;
CloseTool : 'Close Tool' ;
ExitGhidra : 'Exit Ghidra' ;

//Ghidra Edit Menu
ToolOptions : 'Tool Options' ;
OptionsFor : 'Options for' ;
//TODO: determine if we should represent explicit string shown in menu
ClearCodeBytes : 'Clear Code Bytes' ;
ClearWithOptions : 'Clear With Options' ;
ClearFlowAndRepair : 'Clear Flow and Repair' ;
Undo : 'Undo' ;
Redo :  'Redo' ;

//Ghidra Analysis Menu
AutoAnalyze : 'Auto Analyze' ;
AnalyzeAllOpen : 'Analyze All Open' ;
OneShot : 'One Shot' ;
    //Analyze:One Shot Menu
    ASCIIStrings : 'ASCII Strings' ;
    AggressiveInstructionFinder : 'Aggressive Instruction Finder' ;
    CallConventionID : 'Call Convention ID' ;
    CallFixupInstaller : 'Call-Fixup Installer' ;
    CreateAddressTables : 'Create Address Tables' ;
    DWARF : 'DWARF' ;
    DecompilerParameterID : 'Decompiler Parameter ID' ;
    DecompilerSwitchAnalysis : 'Decompiler Switch Analysis' ;
    DemanglerGNU : 'Demangler GNU' ;
    EmbeddedMedia : 'Embedded Media' ;
    FunctionID : 'Function ID' ;
    FunctionStartSearch : 'Function Start Search' ;
    NonReturningFunctionsDiscovered : 'Non-Returning Functions - Discovered' ;
    SharedReturnCalls : 'Shared Return Calls' ;
    Stack : 'Stack' ;
AnalyzeStack : 'Analyze Stack' ;

//Ghidra Graph Menu
BlockFlow : 'Block Flow' ;
CodeFlow : 'Code Flow' ;
Calls : 'Calls' ;
CallsUsingModel : 'Calls Using Model' ;
    //Graph:Calls Using Model Menu
    IsolatedEntry : 'Isolated Entry' ;
    MultipleEntry : 'Multiple Entry' ;
    OverlappedCode : 'Overlapped Code' ;
    PartitionedCode : 'Partitioned Code' ;
AppendGraph : 'Append Graph' ;
ReuseGraph : 'Reuse Graph' ;
ShowLocation : 'Show Location' ;
GraphOutput : 'Graph Output' ;
    //Graph:Graph Output Menu
    DefaultGraphDisplay : 'Default Graph Display' ;
    GraphExport : 'Graph Export' ;

//Ghidra Navigation Menu
ClearHistory: 'Clear History' ;
NextHistoryFunction : 'Next History Function' ;
PreviousHistoryFunction : 'Previous History Function' ;
GoTo: 'Go To' ;
GoToSymbolSource : 'Go To Symbol Source' ;
GoToNextFunction : 'Go To Next Function' ;
GoToPreviousFunction : 'Go To Previous Function' ;
GoToProgram : 'Go To Program' ;
GoToLastActiveProgram : 'Go To Last Active Program' ;
GoToLastActiveComponent : 'Go To Last Active Component' ;
NextSelectedRange : 'Next Selected Range' ;
PreviousSelectedRange : 'Previous Selected Range' ;
NextHighlightRange : 'Next Highlight Range' ;
PreviousHighlightRange : 'Previous Highlight Range' ;
NextColorRange : 'Next Color Range' ;
PreviousColorRange : 'Previous Color Range' ;

//Ghidra Search Menu
LabelHistory : 'Label History' ;
ProgramText : 'Program Text' ;
RepeatTextSearch : 'Repeat Text Search' ;
Memory : 'Memory' ;
RepeatMemorySearch : 'Repeat Memory Search' ;
ForMatchingInstructions : 'For Matching Instructions' ;
    //Search:For Matching Instructions Menu
    ExcludeOperands : 'Exclude Operands' ;
    IncludeOperands : 'Include Operands' ;
    IncludeOperandsExceptConstants : 'Include Operands (except constants)' ;
ForAddressTables : 'For Address Tables' ;
ForDirectTables : 'For Direct Tables' ;
ForInstructionPatterns : 'For Instruction Patterns' ;
ForScalars : 'For Scalars' ;
ForStrings : 'For Strings' ;

//Ghidra:Select Menu
ProgramChanges : 'Program Changes' ;
AllFlowsFrom : 'All Flows From' ;
AllFlowsTo : 'All Flows To' ;
LimitedFlowsFrom : 'Limited Flows From' ;
LimitedFlowsTo : 'Limited Flows To' ;
Subroutine : 'Subroutine' ;
DeadSubroutines : 'Dead Subroutines' ;
Function : 'Function' ;
FromHighlight : 'From Highlight' ;
ProgramHighlight : 'Program Higlight' ;
    //Select:Program Highlight Menu
    EntireSelection : 'Entire Selection' ;
    Clear : 'Clear' ;
    AddSelection : 'Add Selection' ;
    SubtractSelection : 'Subtract Selection' ;
ScopedFlow : 'Scoped Flow' ;
    //Select:Scoped Flow Menu
    ForwardScopedFlow : 'Forward Scoped Flow' ;
    ReverseScopedFlow : 'Reverse Scoped Flow' ;
Bytes : 'Bytes' ;
AllInView : 'All In View' ;
ClearSelection : 'Clear Selection' ;
Complement : 'Complement' ;
Data : 'Data' ;
Instructions : 'Instructions' ;
Undefined : 'Undefined' ;
CreateTableFromSelection : 'Create Table From Selection' ;
RestoreSelection : 'Restore Selection' ;
BackRefs : 'Back Refs' ;
ForwardRefs : 'Forward Refs' ;

//Ghidra Tools Menu
ProcessorManual : 'Processor Manual' ;
ProgramDifferences : 'Program Differences' ;
GenerateChecksums : 'Generate Checksums' ;

//Ghidra Window Menu
Bookmarks : 'Bookmarks' ;
BundleManager : 'Bundle Manager' ;
//Bytes : 'Bytes' ; //token already defined
ChecksumGenerator : 'Checksum Generator' ;
Comments : 'Comments' ;
Console : 'Console' ;
DataTypeManager : 'Data Type Manager' ;
DataTypePreview : 'Data Type Preview' ;
Decompiler : 'Decompiler' ;
DefinedData : 'Defined Data' ;
DefinedStrings : 'Defined Strings' ;
DisassembledView : 'Disassembled View' ;
EquatesTable : 'Equates Table' ;
ExternalPrograms : 'External Programs' ;
FunctionCallGraph : 'Function Call Graph' ;
FunctionCallTrees : 'Function Call Trees' ;
FunctionGraph : 'Function Graph' ;
FunctionTags : 'Function Tags' ;
Functions : 'Functions' ;
Listing : 'Listing' ProgramName ; //TODO
MemoryMap : 'Memory Map' ;
ProgramTrees : 'Program Trees' ;
Python : 'Python' ;
RegisterManager : 'Register Manager' ;
RelocationTable : 'Relocation Table' ;
ScriptManager : 'Script Manager' ;
SymbolReferences : 'Symbol References' ;
SymbolTable : 'Symbol Table' ;
SymbolTree : 'Symbol Tree' ;

//Ghidra Help Menu
Contents : 'Contents' ;
GhidraAPIHelp : 'Ghidra API Help' ;
UserAgreement : 'UserAgreement' ;
InstalledProcessors : 'Installed Processors' ;
AboutGhidra : 'About Ghidra' ;
About : 'About' ProgramName; //TODO

//Application Toolbar
//Save : 'Save' ; //Already define in application menu
Back : 'Back' ;
Forward : 'Forward' ;

NoActionTaken : 'NoAction' ;

//Keyboard Actions
KEY_CODE : 'KEY_'[A-Z_]+ ;

//To disambiguate from other strings, we enclose generic text in curly braces
ProgramName : '{'[0-9a-zA-Z_\-. ]+'}' ; //TODO:test me


//Since program addresses are used everywhere, we create a lexer rule for it
ProgramAddress : '0x'[0-9]+ ; // TODO : needs testing
LineNumber : [1-9]+[0-9]+ ;

//Text that is ripped directly from ghidra instrumentation. Meant to be used for fields.
PluginElement : '('GenericText')';

//Generic symbols such as __gmon_start__
GenericSymbol : [0-9a-zA-Z_]+ ; //TODO: test me

//Generic text matches ProgramAddress and LineNumber so must be last to capture other text strings
GenericText : [0-9a-zA-Z]+ ; //TODO: test me

//Skip all whitespace, allows there to be some, lots, or no space between tokens
WS : [ \t\r\n]+ -> skip ;