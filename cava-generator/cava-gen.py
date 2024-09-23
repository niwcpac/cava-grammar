"""
File:    cava-gen.py
Author:  Froylan Maldonado
Email:   froylan.g.maldonado.civ@us.navy.mil
Created: September 2024
Description:
    This Python script handles JSON event data from Ghidra
    instrumentation and generates grammar statements.
"""

from core.grammar_classes import *
from core.event_converter import *
from core.misc import *
import json
import argparse
from utils.buffer import get_frame
from utils.hash_buffer import *


def generate_grammar_statements(inputfile, outputfile, release, buffer_size=30):

    instrumentation_hash_buffer = HashBuffer(release)
    event_parser = EventParser()
    grammar_events = []

    with open(inputfile) as json_events:
        for event_string in json_events:
            event = json.loads(event_string)
            instrumentation_hash_buffer.add(event)
            if instrumentation_hash_buffer.get_buffer_time_frame() > buffer_size:
                while instrumentation_hash_buffer.has_next():
                    grammar_statements = event_parser.parse_event(instrumentation_hash_buffer)
                    instrumentation_hash_buffer.next()
                    if grammar_statements is not None:
                        grammar_events = grammar_events + grammar_statements
                instrumentation_hash_buffer = HashBuffer(release)
                generate_output_file(grammar_events, outputfile)
                grammar_events = []

        while instrumentation_hash_buffer.has_next():
            grammar_statements = event_parser.parse_event(instrumentation_hash_buffer)
            instrumentation_hash_buffer.next()
            if grammar_statements is not None:
                grammar_events = grammar_events + grammar_statements

        generate_output_file(grammar_events, outputfile)


def main():
    parser = argparse.ArgumentParser(description="Generate grammar statements based off given event data.")
    parser.add_argument("-i", "--inputfile", type=str, default='lsl_data.json',
                        help="path to event data (Default: lsl_data.json)")
    parser.add_argument("-o", "--outputfile", type=str, default='default.txt',
                        help="Output file name for grammar statements (Default: default.txt)")
    parser.add_argument("--release", action="store_true", help="Additional information for debugging")
    args = parser.parse_args()

    # Setting variables 
    inputfile = args.inputfile
    outputfile = args.outputfile

    generate_grammar_statements(inputfile, outputfile, False, buffer_size=100)


main()
