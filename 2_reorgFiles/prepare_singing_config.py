# -*- coding: utf-8 -*-

import os
import yaml

import utils


class PrepareSingingConfig(object):

    def __init__(self, config_file):

        with file(config_file, 'r') as stream:
            self.config = yaml.load(stream)
        utils.log_heading(0, 'config dump')
        print(yaml.dump(self.config, default_flow_style=False))

        singing_data = self.config['singing-data']
        self.singing_phone_align_folder = singing_data['phone-align']
        self.singing_ending_silence = singing_data['ending-silence']
        self.singing_state_align_folder = singing_data['state-align']
        self.singing_phone_name_pattern = singing_data['phone-name-pattern']
        self.singing_f0_folder = singing_data['f0']

        merlin_data = self.config['merlin-data']
        folder = merlin_data['folder']
        self.merlin_state_align_folder = os.path.join(
            folder, merlin_data['state-align'])
        self.merlin_lf0_folder = os.path.join(
            folder, merlin_data['lf0'])


