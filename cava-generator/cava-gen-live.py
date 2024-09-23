"""
File:    cava-gen-live.py
Author:  Froylan Maldonado
Email:   froylan.g.maldonado.civ@us.navy.mil
Created: September 2024
Description:
    This Python script handles live JSON event data from Ghidra
    instrumentation and generates grammar statements.
"""

from pylsl import StreamInlet, resolve_stream
from core.event_converter import *
from core.misc import *

streams = resolve_stream('type', "Markers")

inlet = StreamInlet(streams[0])
event_parser = EventParser()

while True:
    sample, timestamp = inlet.pull_sample()
    event = json.loads(sample[0])
    interaction = event_parser.parse_event(event)
    if interaction[0] is not None:
        print(str(interaction[0]))

