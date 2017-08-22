# -*- coding: utf-8 -*-

import os
import sys
import subprocess


def log_heading(level, heading, blank_line=False, file_handle=sys.stdout):

    if level == 0:
        char = '#'
    elif level == 1:
        char = '*'
    elif level == 2:
        char = '='
    else:
        char = '-'

    file_handle.write('{0}\n'.format(char * 79))
    file_handle.write('{0} LOG {1} - {2}\n'.format(char, level, heading))
    file_handle.write('{0}\n'.format(char * 79))
    if blank_line:
        file_handle.write('\n')


def ensure_directory_exists(directory):

    if not os.path.exists(directory):
        os.makedirs(directory)


def ensure_parent_directory_exists(file_path):

    directory = os.path.dirname(file_path)
    ensure_directory_exists(directory)


def run_process(args):

    try:
        p = subprocess.Popen(args, bufsize=-1, shell=True,
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, close_fds=True)
        (stdoutdata, stderrdata) = p.communicate()
        if p.returncode != 0:
            raise OSError
        return (stdoutdata, stderrdata)
    except subprocess.CalledProcessError as e:
        raise
    except ValueError:
        raise
    except OSError:
        raise
    except KeyboardInterrupt:
        try:
            p.kill()
        except UnboundLocalError:
            pass
        raise KeyboardInterrupt


def generate_silence_wave(sample_rate, num_bits, length):

    file_name = 'silence-{}k-{}.wav'.format(sample_rate, num_bits)
    run_process('sox -n -r {}k -b {} -c 1 {} trim 0.0 {}'.format(
        sample_rate, num_bits, file_name, length))
    return file_name


