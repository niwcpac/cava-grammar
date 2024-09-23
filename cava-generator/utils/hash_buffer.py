"""
File:    hash_buffer.py
Author:  Froylan Maldonado
Email:   froylan.g.maldonado.civ@us.navy.mil
Created: September 2024
Description:
    Hash buffer implementation for parsing ghidra isntrumentation events.
    
"""

import hashlib


class HashBuffer:

    def __init__(self, release=True):
        self.release_ = release
        self.events_ = []
        self.index_ = None

    def add(self, event):

        event_name = list(event.keys())[0]
        event_data = event.get(event_name)
        event_timestamp = event_data.get("Timestamp")
        event_hash = hashlib.md5(str(event).encode()).hexdigest()
        event_consumed = False

        mod_event = {
            "Name": event_name,
            "Data": event_data,
            "Timestamp": event_timestamp,
            "Hash": event_hash,
            "Consumed": event_consumed,
            "Event": event
        }

        self.events_.append(mod_event)

        if self.index_ is None:
            self.index_ = 0

        return True

    def current(self) -> dict or None:

        if self.index_ >= len(self.events_):
            if not self.release_:
                print("[ERROR] Fatal Error: current index is out of bounds!")
            return None

        return self.events_[self.index_]

    # Returns False if there is no more events left to parse
    def next(self):
        if self.has_next():
            self.index_ += 1

    def has_next(self) -> bool:
        if self.index_ is None:
            return False
        return not(self.index_ >= len(self.events_))

    # Purge removes all events from self.events_ between 0 and ending_index
    def purge(self, ending_index):

        if ending_index >= len(self.events_):
            if not self.release_:
                print("[ERROR] Fatal Error: Purge request was past ending index!")
                print("[ERROR] EventSize: ", len(self.events_), "EndingIndex: ", ending_index)
            return False

        self.events_ = self.events_[ending_index:]
        self.reset_index()

    def get_buffer_time_frame(self) -> float:

        first_event = self.events_[0]
        last_event = self.events_[-1]

        first_event_timestamp = first_event.get("Timestamp")
        last_event_timestamp = last_event.get("Timestamp")

        return last_event_timestamp - first_event_timestamp

    def reset_index(self):

        self.index_ = 0

    def get_event_list(self):

        return self.events_

    def get_index(self):

        return self.index_

    def debug(self):

        print("[INFO] Current: ", self.current())
        print("[INFO] BufferTimeFrame: ", self.get_buffer_time_frame())

    def is_release(self):
        return self.release_









