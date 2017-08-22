#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import re


def get_file_set(folder, extension):
    file_name_pattern = re.compile(r'^(\d{{10}})\.{}$'.format(extension))
    file_list = set()
    for dir_path, dir_names, file_names in os.walk(folder):
        file_names = sorted(file_names)
        for file_name in file_names:
            matched = file_name_pattern.match(file_name)
            if matched:
                file_list.add(matched.group(1))
    return file_list


### interpolate F0, if F0 has already been interpolated, nothing will be changed after passing this function
def interpolate_f0(lf0s):
    frame_number = len(lf0s)

    ip_data = lf0s

    last_value = 0.0
    for i in xrange(frame_number):
        if lf0s[i] <= 0.0:
            j = i + 1
            for j in range(i + 1, frame_number):
                if lf0s[j] > 0.0:
                    break
            if j < frame_number - 1:
                if last_value > 0.0:
                    step = (lf0s[j] - lf0s[i - 1]) / float(j - i)
                    for k in range(i, j):
                        ip_data[k] = lf0s[i - 1] + step * (k - i + 1)
                else:
                    for k in range(i, j):
                        ip_data[k] = lf0s[j]
            else:
                for k in range(i, frame_number):
                    ip_data[k] = last_value
        else:
            ip_data[i] = lf0s[i]
            last_value = lf0s[i]

    return ip_data


def Relpace_lf0_one_file(given_lf0_file, predicted_lf0_file, output_lf0_file):
    with open(given_lf0_file, 'rt') as handle:
        given_lf0s = handle.readlines()
    with open(predicted_lf0_file, 'rt') as handle:
        predicted_lf0s = handle.readlines()

    if len(given_lf0s) != len(predicted_lf0s):
        print "error! givenlf0 should have same count with predicted lf0"
        return

    given_lf0s_float = map (float, given_lf0s)
    given_lf0_interpolate = interpolate_f0(given_lf0s_float)
    output_lf0s = [None] * len(given_lf0s)
    for index in range(len(given_lf0s)):
        predicted_lf0s[index] = predicted_lf0s[index].strip()
        predicted_lf0 = float (predicted_lf0s[index])
        if predicted_lf0 < 0:
            output_lf0s[index] = predicted_lf0s[index]
        else:
            output_lf0s[index] = given_lf0_interpolate[index]

    with open(output_lf0_file, 'wt') as handle:
        for frame_index in xrange(len(output_lf0s)):
            handle.write('{}\n'.format(output_lf0s[frame_index]))
    return


def replace_f0(given_lf0_folder, predicted_lf0_folder,
                      output_folder):
    file_set = get_file_set(predicted_lf0_folder, 'lf0a')
    file_list = sorted(list(file_set))
    for file_id in file_list:
        given_file_path = os.path.join(
            given_lf0_folder, '{}.lf0a'.format(file_id))
        predicted_file_path = os.path.join(
            predicted_lf0_folder, '{}.lf0a'.format(file_id))
        output_file_path = os.path.join(
            output_folder, '{}.lf0a'.format(file_id))
        print(given_file_path)
        Relpace_lf0_one_file(given_file_path, predicted_file_path, output_file_path)
    print

    return


if __name__ == '__main__':
    (_, given_lf0_folder, predicted_lf0_folder,output_folder) = sys.argv

    replace_f0(given_lf0_folder, predicted_lf0_folder,
               output_folder)


