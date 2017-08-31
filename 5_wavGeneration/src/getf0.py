#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import re
import numpy

def get_f0(given_lf0_file, output_lf0_file, lf0_key, lf0_level):
    with open(given_lf0_file, 'rt') as handle:
        given_lf0s = handle.readlines()
    # fid = open(output_lf0_file,"w")
    given_lf0s_float = map(float, given_lf0s)
    feature_lf0_level = [len(lf0_level)] * len(given_lf0s_float)

    for i in range(len(given_lf0s_float)):
        if (given_lf0s_float[i] <= 3):
            feature_lf0_level[i] = 0
        else:
            for j in range(len(lf0_level)):
                if (given_lf0s_float[i] < lf0_level[j]):
                    feature_lf0_level[i] = j + 1
                    break

    f0_label = numpy.zeros([len(feature_lf0_level), len(lf0_key)])
    fid = open(output_lf0_file, "wb")
    print(given_lf0_file)

    for i in range(len(feature_lf0_level)):
        if feature_lf0_level[i] == 0:
            f0_label[i][0] = 0.99
            for j in range(1, len(lf0_key)):
                f0_label[i][j] = 0.01
        else:
            for j in range(len(lf0_key)):
                if int(feature_lf0_level[i]) <= int(lf0_key[j]):
                    f0_label[i][j] = 0.99
                else:
                    f0_label[i][j] = 0.01

    f0_label = numpy.array(f0_label, 'float32')
    f0_label.tofile(fid)
    fid.close()
    return

def get_lf0_key(lf0_question_set_path):
    questionfile = open(lf0_question_set_path)
    question_list = questionfile.readlines()

    return question_list

def get_lf0_level(lf0_level_file_path):
    f0_level = numpy.loadtxt(lf0_level_file_path)
    f0_diff_level = [0.0] * (len(f0_level) - 1)

    for i in range(0,len(f0_level) - 1):
        f0_diff_level[i] = (float(f0_level[i]) + float(f0_level[i+1])) / 2

    return f0_diff_level

def get_f0_label(lf0_question_set_path, lf0_level_file_path,given_lf0_folder, output_folder):
    lf0_key = get_lf0_key(lf0_question_set_path)
    lf0_level = get_lf0_level(lf0_level_file_path)
    get_f0(given_lf0_folder, output_folder, lf0_key, lf0_level)

if __name__ == '__main__':
    (_, lf0_question_set_path, lf0_level_file_path,given_lf0_folder, output_folder) = sys.argv
    get_f0_label(lf0_question_set_path, lf0_level_file_path,given_lf0_folder, output_folder)