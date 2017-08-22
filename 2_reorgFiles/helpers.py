# -*- coding: utf-8 -*-

import os
import re


def extract_lab_files(state_align_file, output_folder):

    num_states = 5
    sentence_id_pattern = re.compile(r'^".+/(\d{10}\.lab)"$')
    with open(state_align_file, 'rt') as handle:
        line = handle.readline().strip()
        if line != '#!MLF!#':
            print('State align file heading error.')
            return
        status = 'enter-sentence'
        while True:
            line = handle.readline()
            if len(line) == 0:
                break
            line = line.strip()
            if status == 'enter-sentence':
                matched = sentence_id_pattern.match(line)
                if matched is None:
                    print('Sentence id not found.')
                    break
                output_file_name = os.path.join(output_folder, matched.group(1))
                print(output_file_name)
                lines = []
                status = 'next-phone'
            elif status == 'next-phone':
                if line == '.':
                    with open(output_file_name, 'wt') as output_handle:
                        for output_line in lines:
                            output_handle.write('{}\n'.format(output_line))
                    status = 'enter-sentence'
                else:
                    parts = line.split()
                    if len(parts) != 4:
                        print('First state format is wrong.')
                        break
                    lines.append(' '.join(parts[:3]))
                    for i in xrange(num_states - 1):
                        line = handle.readline().strip()
                        lines.append(line)

    print


