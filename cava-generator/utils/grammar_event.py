"""
File:    grammar_event.py
Author:  Froylan Maldonado
Email:   froylan.g.maldonado.civ@us.navy.mil
Created: September 2024
Description:
    Grammar event that is generated when a grammar statement is constructed. 
    These are the events that are seen in the output file.
"""

from core.grammar_classes import Interaction


class GrammarEvent:

    def __init__(self, sentence: Interaction, inferred: bool, hash_list: list, timestamp: int, source_event: dict):
        self.sentence_ = sentence
        self.inferred_ = inferred
        self.hash_list_ = hash_list
        self.timestamp_ = timestamp
        self.source_event_ = source_event

    def __str__(self):
        return str({"Sentence": str(self.sentence_),
                    "Timestamp": self.timestamp_,
                    "Inferred": self.inferred_,
                    "Hashes": self.hash_list_})

    def debug(self):

        print(f'===== START: DEBUG GRAMMAR EVENT =====')
        print("Sentence: ", self.sentence_)
        print("Timestamp: ", self.timestamp_)
        print("Inferred: ", self.inferred_)
        print("SourceEvent: ", self.source_event_)
        print("Hashes: ")

        for event_hash in self.hash_list_:
            print(f'    {event_hash}')

        print(f'====== END: DEBUG GRAMMAR EVENT ======')
