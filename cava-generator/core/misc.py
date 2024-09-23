"""
File:    misc.py
Author:  Froylan Maldonado
Email:   froylan.g.maldonado.civ@us.navy.mil
Created: September 2024
Description:
    Misc classes, enums, and dicts that are used by other files.
"""

import json
from enum import Enum, auto


class GRAMMAR_TYPE(Enum):
    UNHANDLED = auto()
    INTERACTION = auto()
    INPUT_DEVICE = auto()
    INPUT_ACTION = auto()
    TOOL_CONTEXT = auto()
    ACTION = auto()


def generate_output_file(grammar_statements, outputfile):
    output = open(outputfile, "a")

    for element in grammar_statements:
        output.write(str(element) + '\n')

    output.close()


internal_plugin_to_grammar = {
    'CavaCodeBrowserPlugin': "CodeBrowser : ListingView",
    'CavaDecompilePlugin': 'Decompiler',
    'CavaFunctionGraphPlugin_ListingPanel': 'FunctionGraph',
    'CavaTaskSequencingPanel_TaskInstructionsTextPane': 'TaskInstructions',
    'CavaTaskSequencingPanel_ActionButton': 'TaskInstructions : Button(OK)',
    'CavaTaskSequencingPanel': "TaskInstructions",
    'CavaTaskSequencingPanel_TaskResultTextPane': 'TaskInstructions',
    'TaskSurvey_q1r1': 'TaskSurveyRadioButton',
    'TaskSurvey_q1r3': 'TaskSurveyRadioButton',
    'TaskSurvey_q1r2': 'TaskSurveyRadioButton',
    'TaskSurvey_q1r4': 'TaskSurveyRadioButton',
    'TaskSurvey_q1r7': 'TaskSurveyRadioButton',
    'TaskSurvey_q1r6': 'TaskSurveyRadioButton',
    'TaskSurvey_q2r1': 'TaskSurveyRadioButton',
    'TaskSurvey_q2r3': 'TaskSurveyRadioButton',
    'TaskSurvey_q2r2': 'TaskSurveyRadioButton',
    'TaskSurvey_q2r4': 'TaskSurveyRadioButton',
    'TaskSurvey_q2r5': 'TaskSurveyRadioButton',
    'TaskSurvey_q2r6': 'TaskSurveyRadioButton',
    'TaskSurvey_q2r7': 'TaskSurveyRadioButton',
    'TaskSurvey_q3r1': 'TaskSurveyRadioButton',
    'TaskSurvey_q3r2': 'TaskSurveyRadioButton',
    'TaskSurvey_q3r3': 'TaskSurveyRadioButton',
    'TaskSurvey_q3r5': 'TaskSurveyRadioButton',
    'TaskSurvey_q3r7': 'TaskSurveyRadioButton',
    'TaskSurvey_q3r4': 'TaskSurveyRadioButton',
    'TaskSurvey_q3r6': 'TaskSurveyRadioButton',
    'TaskSurvey_q1r5': 'TaskSurveyRadioButton',
    'TaskSurvey_q3Comment': 'TaskSurveyCommentWindow',
    'TaskSurvey_SubmitResponses': 'TaskSurveySubmitButton',
    'CavaFunctionGraphPlugin': "FunctionGraph",
    'CavaFunctionGraphPlugin_SatelliteGraphViewer': "FunctionGraphSatelliteWindow"
}

sneakysnekMapping = {
    'backspace': 'KEY_BACKSPACE',
    '\b': 'KEY_BACKSPACE',
    'tab': 'KEY_TAB',
    'enter': 'KEY_RETURN',
    'return': 'KEY_RETURN',
    'shift': 'KEY_LEFT_SHIFT',
    'ctrl': 'KEY_LEFT_CTRL',
    'alt': 'KEY_LEFT_ALT',
    'pause': 'KEY_PAUSE',
    'capslock': 'KEY_CAPSLOCK',
    'esc': 'KEY_ESCAPE',
    'escape': 'KEY_ESCAPE',
    'pgup': 'KEY_PAGE_UP',
    'pgdn': 'KEY_PAGE_DOWN',
    'pageup': 'KEY_PAGE_UP',
    'pagedown': 'KEY_PAGE_DOWN',
    'end': 'KEY_END',
    'home': 'KEY_HOME',
    'left': 'KEY_LEFT',
    'up': 'KEY_UP',
    'right': 'KEY_RIGHT',
    'down': 'KEY_DOWN',
    'print': 'KEY_PRINT_SCREEN',
    'prtsc': 'KEY_PRINT_SCREEN',
    'prtscr': 'KEY_PRINT_SCREEN',
    'prntscrn': 'KEY_PRINT_SCREEN',
    'printscreen': 'KEY_PRINT_SCREEN',
    'insert': 'KEY_INSERT',
    'del': 'KEY_DELETE',
    'delete': 'KEY_DELETE',
    'win': 'KEY_LEFT_SUPER',
    'winleft': 'KEY_LEFT_SUPER',
    'winright': 'KEY_RIGHT_SUPER',
    'apps': 'KEY_RIGHT_SUPER',
    'num0': 'KEY_NUMPAD_0',
    'num1': 'KEY_NUMPAD_1',
    'num2': 'KEY_NUMPAD_2',
    'num3': 'KEY_NUMPAD_3',
    'num4': 'KEY_NUMPAD_4',
    'num5': 'KEY_NUMPAD_5',
    'num6': 'KEY_NUMPAD_6',
    'num7': 'KEY_NUMPAD_7',
    'num8': 'KEY_NUMPAD_8',
    'num9': 'KEY_NUMPAD_9',
    'multiply': 'KEY_NUMPAD_MULTIPLY',
    'add': 'KEY_NUMPAD_ADD',
    'subtract': 'KEY_NUMPAD_SUBTRACT',
    # 'decimal':           'KEY_NUMPAD_SUBTRACT', #something is wrong, suppose to be 'KEY_NUMPAD_DECIMAL'
    'divide': 'KEY_NUMPAD_DIVIDE',
    'f1': 'KEY_F1',
    'f2': 'KEY_F2',
    'f3': 'KEY_F3',
    'f4': 'KEY_F4',
    'f5': 'KEY_F5',
    'f6': 'KEY_F6',
    'f7': 'KEY_F7',
    'f8': 'KEY_F8',
    'f9': 'KEY_F9',
    'f10': 'KEY_F10',
    'f11': 'KEY_F11',
    'f12': 'KEY_F12',
    'numlock': 'KEY_NUMLOCK',
    'scrolllock': 'KEY_SCROLL_LOCK',
    'shiftleft': 'KEY_LEFT_SHIFT',
    'shiftright': 'KEY_RIGHT_SHIFT',
    'ctrlleft': 'KEY_LEFT_CTRL',
    'ctrlright': 'KEY_RIGHT_CTRL',
    'altleft': 'KEY_LEFT_ALT',
    'altright': 'KEY_RIGHT_ALT',
    # These are added because unlike a-zA-Z0-9, the single characters do not have a
    ' ': 'KEY_SPACE',
    'space': 'KEY_SPACE',
    '\t': 'KEY_TAB',
    '\n': 'KEY_RETURN',  # for some reason this needs to be cr, not lf
    '\r': 'KEY_RETURN',
    '\e': 'KEY_ESCAPE',
    "'": 'KEY_APOSTROPHE',
    '=': 'KEY_EQUALS',
    ',': 'KEY_COMMA',
    '-': 'KEY_MINUS',
    '.': 'KEY_PERIOD',
    '/': 'KEY_SLASH',
    ';': 'KEY_SEMICOLON',
    '[': 'KEY_LEFT_BRACKET',
    ']': 'KEY_RIGHT_BRACKET',
    '\\': 'KEY_BACKSLASH',
    '`': 'KEY_GRAVE',
    # KEYS I HAVE TO ADD
    '0': 'KEY_0',
    '1': 'KEY_1',
    '2': 'KEY_2',
    '3': 'KEY_3',
    '4': 'KEY_4',
    '5': 'KEY_5',
    '6': 'KEY_6',
    '7': 'KEY_7',
    '8': 'KEY_8',
    '9': 'KEY_9',
    'a': 'KEY_A',
    'b': 'KEY_B',
    'c': 'KEY_C',
    'd': 'KEY_D',
    'e': 'KEY_E',
    'f': 'KEY_F',
    'g': 'KEY_G',
    'h': 'KEY_H',
    'i': 'KEY_I',
    'j': 'KEY_J',
    'k': 'KEY_K',
    'l': 'KEY_L',
    'm': 'KEY_M',
    'n': 'KEY_N',
    'o': 'KEY_O',
    'p': 'KEY_P',
    'q': 'KEY_Q',
    'r': 'KEY_R',
    's': 'KEY_S',
    't': 'KEY_T',
    'u': 'KEY_U',
    'v': 'KEY_V',
    'w': 'KEY_W',
    'x': 'KEY_X',
    'y': 'KEY_Y',
    'z': 'KEY_Z'
}


class KeyboardKey(Enum):
    """Supporting the ANSI layout"""

    KEY_ESCAPE = "KEY_ESCAPE"
    KEY_F1 = "KEY_F1"
    KEY_F2 = "KEY_F2"
    KEY_F3 = "KEY_F3"
    KEY_F4 = "KEY_F4"
    KEY_F5 = "KEY_F5"
    KEY_F6 = "KEY_F6"
    KEY_F7 = "KEY_F7"
    KEY_F8 = "KEY_F8"
    KEY_F9 = "KEY_F9"
    KEY_F10 = "KEY_F10"
    KEY_F11 = "KEY_F11"
    KEY_F12 = "KEY_F12"
    KEY_PRINT_SCREEN = "KEY_PRINT_SCREEN"
    KEY_F13 = KEY_PRINT_SCREEN
    KEY_SCROLL_LOCK = "KEY_SCROLL_LOCK"
    KEY_F14 = KEY_SCROLL_LOCK
    KEY_PAUSE = "KEY_PAUSE"
    KEY_F15 = KEY_PAUSE

    KEY_GRAVE = "KEY_GRAVE"
    KEY_BACKTICK = KEY_GRAVE
    KEY_1 = "KEY_1"
    KEY_2 = "KEY_2"
    KEY_3 = "KEY_3"
    KEY_4 = "KEY_4"
    KEY_5 = "KEY_5"
    KEY_6 = "KEY_6"
    KEY_7 = "KEY_7"
    KEY_8 = "KEY_8"
    KEY_9 = "KEY_9"
    KEY_0 = "KEY_0"
    KEY_MINUS = "KEY_MINUS"
    KEY_DASH = KEY_MINUS
    KEY_EQUALS = "KEY_EQUALS"
    KEY_BACKSPACE = "KEY_BACKSPACE"
    KEY_INSERT = "KEY_INSERT"
    KEY_HOME = "KEY_HOME"
    KEY_PAGE_UP = "KEY_PAGE_UP"
    KEY_NUMLOCK = "KEY_NUMLOCK"
    KEY_NUMPAD_DIVIDE = "KEY_NUMPAD_DIVIDE"
    KEY_NUMPAD_SLASH = KEY_NUMPAD_DIVIDE
    KEY_NUMPAD_MULTIPLY = "KEY_NUMPAD_MULTIPLY"
    KEY_NUMPAD_STAR = KEY_NUMPAD_MULTIPLY
    KEY_NUMPAD_SUBTRACT = "KEY_NUMPAD_SUBTRACT"
    KEY_NUMPAD_DASH = KEY_NUMPAD_SUBTRACT

    KEY_TAB = "KEY_TAB"
    KEY_Q = "KEY_Q"
    KEY_W = "KEY_W"
    KEY_E = "KEY_E"
    KEY_R = "KEY_R"
    KEY_T = "KEY_T"
    KEY_Y = "KEY_Y"
    KEY_U = "KEY_U"
    KEY_I = "KEY_I"
    KEY_O = "KEY_O"
    KEY_P = "KEY_P"
    KEY_LEFT_BRACKET = "KEY_LEFT_BRACKET"
    KEY_RIGHT_BRACKET = "KEY_RIGHT_BRACKET"
    KEY_BACKSLASH = "KEY_BACKSLASH"
    KEY_DELETE = "KEY_DELETE"
    KEY_END = "KEY_END"
    KEY_PAGE_DOWN = "KEY_PAGE_DOWN"
    KEY_NUMPAD_7 = "KEY_NUMPAD_7"
    KEY_NUMPAD_8 = "KEY_NUMPAD_8"
    KEY_NUMPAD_9 = "KEY_NUMPAD_9"
    KEY_NUMPAD_ADD = "KEY_NUMPAD_ADD"
    KEY_NUMPAD_PLUS = KEY_NUMPAD_ADD

    KEY_CAPSLOCK = "KEY_CAPSLOCK"
    KEY_A = "KEY_A"
    KEY_S = "KEY_S"
    KEY_D = "KEY_D"
    KEY_F = "KEY_F"
    KEY_G = "KEY_G"
    KEY_H = "KEY_H"
    KEY_J = "KEY_J"
    KEY_K = "KEY_K"
    KEY_L = "KEY_L"
    KEY_SEMICOLON = "KEY_SEMICOLON"
    KEY_APOSTROPHE = "KEY_APOSTROPHE"
    KEY_RETURN = "KEY_RETURN"
    KEY_ENTER = KEY_RETURN
    KEY_NUMPAD_4 = "KEY_NUMPAD_4"
    KEY_NUMPAD_5 = "KEY_NUMPAD_5"
    KEY_NUMPAD_6 = "KEY_NUMPAD_6"

    KEY_LEFT_SHIFT = "KEY_LEFT_SHIFT"
    KEY_Z = "KEY_Z"
    KEY_X = "KEY_X"
    KEY_C = "KEY_C"
    KEY_V = "KEY_V"
    KEY_B = "KEY_B"
    KEY_N = "KEY_N"
    KEY_M = "KEY_M"
    KEY_COMMA = "KEY_COMMA"
    KEY_PERIOD = "KEY_PERIOD"
    KEY_SLASH = "KEY_SLASH"
    KEY_RIGHT_SHIFT = "KEY_RIGHT_SHIFT"
    KEY_UP = "KEY_UP"
    KEY_NUMPAD_1 = "KEY_NUMPAD_1"
    KEY_NUMPAD_2 = "KEY_NUMPAD_2"
    KEY_NUMPAD_3 = "KEY_NUMPAD_3"
    KEY_NUMPAD_RETURN = "KEY_NUMPAD_RETURN"
    KEY_NUMPAD_ENTER = KEY_NUMPAD_RETURN

    KEY_LEFT_CTRL = "KEY_LEFT_CTRL"
    KEY_LEFT_SUPER = "KEY_LEFT_SUPER"
    KEY_LEFT_WINDOWS = KEY_LEFT_SUPER
    KEY_LEFT_ALT = "KEY_LEFT_ALT"
    KEY_SPACE = "KEY_SPACE"
    KEY_RIGHT_ALT = "KEY_RIGHT_ALT"
    KEY_RIGHT_SUPER = "KEY_RIGHT_SUPER"
    KEY_RIGHT_WINDOWS = KEY_RIGHT_SUPER
    KEY_APP_MENU = "KEY_APP_MENU"
    KEY_RIGHT_CTRL = "KEY_RIGHT_CTRL"
    KEY_LEFT = "KEY_LEFT"
    KEY_DOWN = "KEY_DOWN"
    KEY_RIGHT = "KEY_RIGHT"
    KEY_NUMPAD_0 = "KEY_NUMPAD_0"
    KEY_NUMPAD_DECIMAL = "KEY_NUMPAD_DECIMAL"
    KEY_NUMPAD_PERIOD = KEY_NUMPAD_DECIMAL

    # macOS
    KEY_COMMAND = "KEY_COMMAND"
    KEY_FN = "KEY_FN"


keyboard_scan_code_mapping = {
    65307: KeyboardKey.KEY_ESCAPE,
    65470: KeyboardKey.KEY_F1,
    65471: KeyboardKey.KEY_F2,
    65472: KeyboardKey.KEY_F3,
    65473: KeyboardKey.KEY_F4,
    65474: KeyboardKey.KEY_F5,
    65475: KeyboardKey.KEY_F6,
    65476: KeyboardKey.KEY_F7,
    65477: KeyboardKey.KEY_F8,
    65478: KeyboardKey.KEY_F9,
    65479: KeyboardKey.KEY_F10,
    65480: KeyboardKey.KEY_F11,
    65481: KeyboardKey.KEY_F12,
    65377: KeyboardKey.KEY_PRINT_SCREEN,
    65300: KeyboardKey.KEY_SCROLL_LOCK,
    65299: KeyboardKey.KEY_PAUSE,
    96: KeyboardKey.KEY_GRAVE,
    49: KeyboardKey.KEY_1,
    50: KeyboardKey.KEY_2,
    51: KeyboardKey.KEY_3,
    52: KeyboardKey.KEY_4,
    53: KeyboardKey.KEY_5,
    54: KeyboardKey.KEY_6,
    55: KeyboardKey.KEY_7,
    56: KeyboardKey.KEY_8,
    57: KeyboardKey.KEY_9,
    48: KeyboardKey.KEY_0,
    45: KeyboardKey.KEY_MINUS,
    61: KeyboardKey.KEY_EQUALS,
    65288: KeyboardKey.KEY_BACKSPACE,
    65379: KeyboardKey.KEY_INSERT,
    65360: KeyboardKey.KEY_HOME,
    65365: KeyboardKey.KEY_PAGE_UP,
    65407: KeyboardKey.KEY_NUMLOCK,
    65455: KeyboardKey.KEY_NUMPAD_DIVIDE,
    65450: KeyboardKey.KEY_NUMPAD_MULTIPLY,
    65453: KeyboardKey.KEY_NUMPAD_SUBTRACT,
    65289: KeyboardKey.KEY_TAB,
    113: KeyboardKey.KEY_Q,
    119: KeyboardKey.KEY_W,
    101: KeyboardKey.KEY_E,
    114: KeyboardKey.KEY_R,
    116: KeyboardKey.KEY_T,
    121: KeyboardKey.KEY_Y,
    117: KeyboardKey.KEY_U,
    105: KeyboardKey.KEY_I,
    111: KeyboardKey.KEY_O,
    112: KeyboardKey.KEY_P,
    91: KeyboardKey.KEY_LEFT_BRACKET,
    93: KeyboardKey.KEY_RIGHT_BRACKET,
    92: KeyboardKey.KEY_BACKSLASH,
    65535: KeyboardKey.KEY_DELETE,
    65367: KeyboardKey.KEY_END,
    65366: KeyboardKey.KEY_PAGE_DOWN,
    65429: KeyboardKey.KEY_NUMPAD_7,
    65431: KeyboardKey.KEY_NUMPAD_8,
    65434: KeyboardKey.KEY_NUMPAD_9,
    65451: KeyboardKey.KEY_NUMPAD_ADD,
    65509: KeyboardKey.KEY_CAPSLOCK,
    97: KeyboardKey.KEY_A,
    115: KeyboardKey.KEY_S,
    100: KeyboardKey.KEY_D,
    102: KeyboardKey.KEY_F,
    103: KeyboardKey.KEY_G,
    104: KeyboardKey.KEY_H,
    106: KeyboardKey.KEY_J,
    107: KeyboardKey.KEY_K,
    108: KeyboardKey.KEY_L,
    59: KeyboardKey.KEY_SEMICOLON,
    39: KeyboardKey.KEY_APOSTROPHE,
    65293: KeyboardKey.KEY_RETURN,
    65430: KeyboardKey.KEY_NUMPAD_4,
    65437: KeyboardKey.KEY_NUMPAD_5,
    65432: KeyboardKey.KEY_NUMPAD_6,
    65505: KeyboardKey.KEY_LEFT_SHIFT,
    122: KeyboardKey.KEY_Z,
    120: KeyboardKey.KEY_X,
    99: KeyboardKey.KEY_C,
    118: KeyboardKey.KEY_V,
    98: KeyboardKey.KEY_B,
    110: KeyboardKey.KEY_N,
    109: KeyboardKey.KEY_M,
    44: KeyboardKey.KEY_COMMA,
    46: KeyboardKey.KEY_PERIOD,
    47: KeyboardKey.KEY_SLASH,
    65506: KeyboardKey.KEY_RIGHT_SHIFT,
    65362: KeyboardKey.KEY_UP,
    65436: KeyboardKey.KEY_NUMPAD_1,
    65433: KeyboardKey.KEY_NUMPAD_2,
    65435: KeyboardKey.KEY_NUMPAD_3,
    65421: KeyboardKey.KEY_NUMPAD_RETURN,
    65507: KeyboardKey.KEY_LEFT_CTRL,
    65513: KeyboardKey.KEY_LEFT_ALT,
    32: KeyboardKey.KEY_SPACE,
    65514: KeyboardKey.KEY_RIGHT_ALT,
    65508: KeyboardKey.KEY_RIGHT_CTRL,
    65361: KeyboardKey.KEY_LEFT,
    65364: KeyboardKey.KEY_DOWN,
    65363: KeyboardKey.KEY_RIGHT,
    65438: KeyboardKey.KEY_NUMPAD_0,
    65439: KeyboardKey.KEY_NUMPAD_PERIOD,
    65515: KeyboardKey.KEY_LEFT_WINDOWS,
    65516: KeyboardKey.KEY_RIGHT_WINDOWS,
    # Patched entries
    33: KeyboardKey.KEY_1,
    34: KeyboardKey.KEY_APOSTROPHE,
    35: KeyboardKey.KEY_3,
    36: KeyboardKey.KEY_4,
    37: KeyboardKey.KEY_5,
    38: KeyboardKey.KEY_7,
    40: KeyboardKey.KEY_9,
    41: KeyboardKey.KEY_0,
    42: KeyboardKey.KEY_8,
    43: KeyboardKey.KEY_EQUALS,
    58: KeyboardKey.KEY_SEMICOLON,
    60: KeyboardKey.KEY_COMMA,
    62: KeyboardKey.KEY_PERIOD,
    63: KeyboardKey.KEY_SLASH,
    64: KeyboardKey.KEY_2,
    65: KeyboardKey.KEY_A,
    66: KeyboardKey.KEY_B,
    67: KeyboardKey.KEY_C,
    68: KeyboardKey.KEY_D,
    69: KeyboardKey.KEY_E,
    70: KeyboardKey.KEY_F,
    71: KeyboardKey.KEY_G,
    72: KeyboardKey.KEY_H,
    73: KeyboardKey.KEY_I,
    74: KeyboardKey.KEY_J,
    75: KeyboardKey.KEY_K,
    76: KeyboardKey.KEY_L,
    77: KeyboardKey.KEY_M,
    78: KeyboardKey.KEY_N,
    79: KeyboardKey.KEY_O,
    80: KeyboardKey.KEY_P,
    81: KeyboardKey.KEY_Q,
    82: KeyboardKey.KEY_R,
    83: KeyboardKey.KEY_S,
    84: KeyboardKey.KEY_T,
    85: KeyboardKey.KEY_U,
    86: KeyboardKey.KEY_V,
    87: KeyboardKey.KEY_W,
    88: KeyboardKey.KEY_X,
    89: KeyboardKey.KEY_Y,
    90: KeyboardKey.KEY_Z,
    94: KeyboardKey.KEY_6,
    95: KeyboardKey.KEY_MINUS,
    123: KeyboardKey.KEY_LEFT_BRACKET,
    124: KeyboardKey.KEY_BACKSLASH,
    125: KeyboardKey.KEY_RIGHT_BRACKET,
    126: KeyboardKey.KEY_GRAVE,
    65056: KeyboardKey.KEY_TAB,
    65511: KeyboardKey.KEY_LEFT_ALT,
    65512: KeyboardKey.KEY_RIGHT_ALT
}

charMapping = {
    'KEY_SPACE': ' ',
    'KEY_APOSTROPHE': "'",
    'KEY_EQUALS': '=',
    'KEY_COMMA': ',',
    'KEY_MINUS': '-',
    'KEY_PERIOD': '.',
    'KEY_SLASH': '/',
    'KEY_SEMICOLON': ';',
    'KEY_LEFT_BRACKET': '[',
    'KEY_RIGHT_BRACKET': ']',
    'KEY_BACKSLASH': '\\',
    'KEY_GRAVE': '`',
    'KEY_0': '0',
    'KEY_1': '1',
    'KEY_2': '2',
    'KEY_3': '3',
    'KEY_4': '4',
    'KEY_5': '5',
    'KEY_6': '6',
    'KEY_7': '7',
    'KEY_8': '8',
    'KEY_9': '9',
    'KEY_NUMPAD_0': '0',
    'KEY_NUMPAD_1': '1',
    'KEY_NUMPAD_2': '2',
    'KEY_NUMPAD_3': '3',
    'KEY_NUMPAD_4': '4',
    'KEY_NUMPAD_5': '0',
    'KEY_NUMPAD_6': '6',
    'KEY_NUMPAD_7': '7',
    'KEY_NUMPAD_8': '8',
    'KEY_NUMPAD_9': '9',
    'KEY_A': 'a',
    'KEY_B': 'b',
    'KEY_C': 'c',
    'KEY_D': 'd',
    'KEY_E': 'e',
    'KEY_F': 'f',
    'KEY_G': 'g',
    'KEY_H': 'h',
    'KEY_I': 'i',
    'KEY_J': 'j',
    'KEY_K': 'k',
    'KEY_L': 'l',
    'KEY_M': 'm',
    'KEY_N': 'n',
    'KEY_O': 'o',
    'KEY_P': 'p',
    'KEY_Q': 'q',
    'KEY_R': 'r',
    'KEY_S': 's',
    'KEY_T': 't',
    'KEY_U': 'u',
    'KEY_V': 'v',
    'KEY_W': 'w',
    'KEY_X': 'x',
    'KEY_Y': 'y',
    'KEY_Z': 'z'
}
