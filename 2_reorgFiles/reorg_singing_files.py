#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import math
import argparse

import utils
import helpers
from prepare_singing_config import PrepareSingingConfig
from stretch_duration import adjust_alignments

import sys
sys.path.append('../../merlin/src/io_funcs')
from binary_io import BinaryIOCollection


def generate_lf0(source_f0_folder, target_lf0_folder, file_lengths):

    io_funcs = BinaryIOCollection()
    for file_id, file_length in file_lengths.iteritems():
        source_file_path = os.path.join(source_f0_folder,
                                        '{}.f0'.format(file_id))
        target_file_path = os.path.join(target_lf0_folder,
                                        '{}.lf0'.format(file_id))
        with open(source_file_path, 'rt') as handle:
            lines = handle.readlines()
        f0s = [float(line) for line in lines]
        if len(lines) <= file_length:
            f0s += [0.] * (file_length - len(lines))
        else:
            f0s = f0s[:file_length]

        lf0s = [-1e+10] * file_length
        for i in xrange(file_length):
            if f0s[i] <= 10.0:
                continue
            lf0s[i] = math.log(f0s[i])

        print(target_file_path)
        io_funcs.array_to_binary_file(lf0s, target_file_path)

    print


def main(config):

    
    # state alignments adjustment
    phone_align_folder = config.singing_phone_align_folder
    ending_silence = config.singing_ending_silence
    state_align_original_folder = config.singing_state_align_folder
    phone_name_pattern = config.singing_phone_name_pattern
    state_align_folder = config.merlin_state_align_folder
    utils.log_heading(0, 'adjusting state alignments')
    utils.ensure_directory_exists(state_align_folder)
    file_lengths = adjust_alignments(
        phone_align_folder, ending_silence, state_align_original_folder,
        phone_name_pattern, state_align_folder)

    # lf0 file generation
    source_f0_folder = config.singing_f0_folder
    target_lf0_folder = config.merlin_lf0_folder
    utils.log_heading(0, 'generating lf0 files')
    utils.ensure_directory_exists(target_lf0_folder)
    generate_lf0(source_f0_folder, target_lf0_folder, file_lengths)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Reorg the singing file structure.',
        epilog='State label files will be generated.')
    parser.add_argument('-c', '--config', required=True,
                        help='config file path')
    args = parser.parse_args()

    config = PrepareSingingConfig(args.config)
    main(config)


