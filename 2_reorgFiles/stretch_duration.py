#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import re
#import pdb

def get_file_set(folder, extension):
    
   # print extension
    file_name_pattern = re.compile('^(.*)\.{}$'.format(extension))
    file_list = set()
    for dir_path, dir_names, file_names in os.walk(folder):
        file_names = sorted(file_names)
        for file_name in file_names:
            matched = file_name_pattern.match(file_name)
            if matched:
                file_list.add(matched.group(1))
    return file_list

def stretch_longest_dur(target_duration,state_durations):

    #target_duration=6
    #state_durations=[1,1,3,3,1]
    num_states = len(state_durations)
    rest_source = sum(state_durations)
    rest_target = target_duration
    max_state_dur=max(state_durations)
    indexM=state_durations.index(max_state_dur)

    #if max_state_dur<rest_source/2:
        #stretch_duration(target_duration,state_duration)
    #else:
    new_state_durations = [None] * num_states
    for state, state_duration in enumerate(state_durations):
        new_state=1
        if rest_source == 0:
            assert rest_target == 0
            break
        if state==indexM:
            if rest_target>=rest_source:
                new_state=max_state_dur+rest_target-rest_source
                new_state_durations[state]=new_state

            else:
                new_state=max_state_dur-(rest_source-rest_target)
                if new_state<1:
                    new_state_durations=stretch_duration(target_duration,state_durations)
                    break;
                else:
                    new_state_durations[state]=new_state
        else:
            new_state=state_duration
            new_state_durations[state]=new_state
        rest_source -= state_duration
        rest_target -= new_state
    return new_state_durations




def stretch_duration(target_duration, state_durations):

    #if target_duration==1055:
        #new_state_durations=[3,1036,5,5,6]
        #return new_state_durations

    num_states = len(state_durations)
    rest_source = sum(state_durations)
    rest_target = target_duration

    if rest_target >= rest_source:
        new_state_durations = [None] * num_states
        for state, state_duration in enumerate(state_durations):
            new_state_duration = int(round(
                float(state_duration) / rest_source * rest_target))
            new_state_durations[state] = new_state_duration
            rest_source -= state_duration
            rest_target -= new_state_duration
    else:
        new_state_durations = [1] * num_states
        rest_source -= num_states
        rest_target -= num_states
        for state, state_duration in enumerate(state_durations):
            if rest_source == 0:
                assert rest_target == 0
                break
            new_state_duration = 1 + int(round(
                float(state_duration - 1) / rest_source * rest_target))
            new_state_durations[state] = new_state_duration
            rest_source -= state_duration - 1
            rest_target -= new_state_duration - 1

    assert sum(new_state_durations) == target_duration
    assert min(new_state_durations) >= 1
    return new_state_durations


def adjust_alignments_one_file(phone_file_path, ending_silence,
                               state_original_file_path,
                               phone_name_pattern, state_file_path):

    num_states = 5
    frame_length = 50000

    phone_pattern = re.compile(r'^(\S+)\s(\S+)$')
    with open(phone_file_path, 'rt') as handle:
        lines = handle.readlines()
    phones = []
    time_stamps = []
    for line in lines:
        matched = phone_pattern.match(line.strip())
        if not matched:
            print('Phone alignment file {} error'.format(phone_file_path))
            break
        phones.append(matched.group(2))
        time_stamp = int(round(float(matched.group(1)) * 200))
        time_stamps.append(time_stamp)
   
    time_stamps.append(time_stamps[-1] + ending_silence)
    durations = zip(time_stamps[:-1], time_stamps[1:])
    durations = [pair[1] - pair[0] for pair in durations]
    if min(durations) < 5:
        print('Min duration in phone alignment file {} less than 25ms'.format(phone_file_path))
        return 0

    label_pattern = re.compile(
        r'^(\d+)\s(\d+)\s(.*?{}.*)$'.format(phone_name_pattern))
    with open(state_original_file_path, 'rt') as handle:
        lines = handle.readlines()
    if len(phones) * num_states != len(lines):
        print('Phone alignment file {} and state original file {} don\'t match' \
              .format(phone_file_path, state_original_file_path))

    start_times = [None] * len(phones) * num_states
    end_times = [None] * len(phones) * num_states
    labels = [None] * len(phones) * num_states
    time_stamp = 0
    state_index = 0
    for index in xrange(len(phones)):
        phone = phones[index]
        duration = durations[index]
        state_durations = [None] * num_states
        erroneous = False
        for state in xrange(num_states):
            line = lines[state_index].strip()
            matched = label_pattern.match(line)
            if not matched or matched.group(4).lower() != phone:
                print('State original alignment file {} error'.format(
                    state_original_file_path))
                erroneous = True
                break
            state_duration = ((int(matched.group(2)) - int(matched.group(1)))
                              / frame_length)
            state_durations[state] =state_duration
            labels[state_index] = matched.group(3)
            state_index += 1
        if erroneous:
            break

        new_state_durations = stretch_duration(duration, state_durations)
        #new_state_durations = stretch_longest_dur(duration, state_durations)

        state_index -= num_states
        for state in xrange(num_states):
            start_times[state_index] = time_stamp * frame_length
            time_stamp += new_state_durations[state]
            end_times[state_index] = time_stamp * frame_length
            state_index += 1

    if erroneous:
        return 0
    with open(state_file_path, 'wt') as handle:
        for state_index in xrange(len(labels)):
            handle.write('{} {} {}\n'.format(
                start_times[state_index], end_times[state_index],
                labels[state_index]))

    return time_stamps[-1]


def adjust_alignments(phone_align_folder, ending_silence,
                      state_align_original_folder,
                      phone_name_pattern, state_align_folder):

    phone_file_set = get_file_set(phone_align_folder, 'txt')
    state_file_set = get_file_set(state_align_original_folder, 'lab')
    file_list = sorted(list(phone_file_set & state_file_set))
    file_lengths = {}
    for file_id in file_list:
        phone_file_path = os.path.join(
            phone_align_folder, '{}.txt'.format(file_id))
        state_original_file_path = os.path.join(
            state_align_original_folder, '{}.lab'.format(file_id))
        state_file_path = os.path.join(
            state_align_folder, '{}.lab'.format(file_id))
        print(phone_file_path)
        file_length = adjust_alignments_one_file(
            phone_file_path, ending_silence, state_original_file_path,
            phone_name_pattern, state_file_path)
        if file_length > 0:
            file_lengths[file_id] = file_length
    print

    return file_lengths


if __name__ == '__main__':

    (_, phone_align_folder, ending_silence,
     state_align_original_folder,
     phone_name_pattern, state_align_folder) = sys.argv
    ending_silence = int(ending_silence)

    adjust_alignments(phone_align_folder, ending_silence,
                      state_align_original_folder,
                      phone_name_pattern, state_align_folder)


