"""
File:    buffer.py
Author:  Froylan Maldonado
Email:   froylan.g.maldonado.civ@us.navy.mil
Created: September 2024
Description:
    Buffer functions. 
"""


def get_frame(event_list, start, frame_size, res):

    mod_start = find_first_frame_event(event_list, start, res)
    end = find_last_frame_event(event_list, mod_start, frame_size)
    #print("Start : ", start, " Mod Start: ", mod_start, " End: ", end)
    frame = event_list[mod_start:end+1:]

    return frame, mod_start


def find_last_frame_event(event_list, start, frame_size) -> int:

    initial_event = event_list[start][0]
    initial_event_name = list(initial_event.keys())[0]
    initial_time = initial_event.get(initial_event_name).get("Timestamp")

    end_time = initial_time + frame_size
    # print("Initial time: ", initial_time, " End time: ", end_time)

    end = start

    for index in range(start+1, len(event_list)):

        event = event_list[index][0]
        event_name = list(event.keys())[0]
        curr_time = event.get(event_name).get("Timestamp")

        if curr_time < end_time:
            end += 1
        else:
            break

    return end


def find_first_frame_event(event_list, start, res) -> int:

    if start <= 0:
        return start

    first_new_event = event_list[start][0]
    first_new_event_name = list(first_new_event.keys())[0]
    time = first_new_event.get(first_new_event_name).get("Timestamp")

    new_start_time = time - res

    for index in reversed(range(start+1)):

        event = event_list[index][0]
        event_name = list(event.keys())[0]
        curr_time = event.get(event_name).get("Timestamp")

        if curr_time < new_start_time:
            return index + 1

    new_start = 0

    return new_start
