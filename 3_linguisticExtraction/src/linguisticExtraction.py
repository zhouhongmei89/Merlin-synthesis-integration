
import cPickle
import gzip
import os, sys, errno
import os.path
import time
import math
import shutil
import pdb
import subprocess
import socket

import numpy
import numpy.distutils.__config__

from utils.providers import ListDataProvider
from frontend.label_normalisation import HTSLabelNormalisation, XMLLabelNormalisation
from frontend.silence_remover import SilenceRemover
from frontend.silence_remover import trim_silence
from frontend.min_max_norm import MinMaxNormalisation
from frontend.acoustic_composition import AcousticComposition
from frontend.mean_variance_norm import MeanVarianceNorm
from frontend.label_composer import LabelComposer
from frontend.label_modifier import HTSLabelModification
from frontend.merge_features import MergeFeat
import configuration
from utils.generate import generate_wav
from utils.learn_rates import ExpDecreaseLearningRate
from io_funcs.binary_io import  BinaryIOCollection
from logplot.logging_plotting import LoggerPlotter, MultipleSeriesPlot, SingleWeightMatrixPlot
import logging # as logging
import logging.config
import StringIO


def read_file_list(file_name):

    logger = logging.getLogger("read_file_list")

    file_lists = []
    fid = open(file_name)
    for line in fid.readlines():
        line = line.strip()
        if len(line) < 1:
            continue
        file_lists.append(line)
    fid.close()

    logger.debug('Read file list from %s' % file_name)
    return  file_lists

def prepare_file_path_list(file_id_list, file_dir, file_extension, new_dir_switch=True):
    if not os.path.exists(file_dir) and new_dir_switch:
        os.makedirs(file_dir)
    file_name_list = []
    for file_id in file_id_list:
        file_name = file_dir + '/' + file_id + file_extension
        file_name_list.append(file_name)

    return  file_name_list

def main_function(cfg):    

    logger = logging.getLogger("main")
    plotlogger = logging.getLogger("plotting")
    plotlogger.set_plot_path(cfg.plot_dir)

    data_dir = cfg.data_dir

    label_normaliser = HTSLabelNormalisation(question_file_name=cfg.question_file_name, add_frame_features=cfg.add_frame_features, subphone_feats=cfg.subphone_feats)
    add_feat_dim = sum(cfg.additional_features.values())
    lab_dim = label_normaliser.dimension + add_feat_dim + cfg.appended_input_dim
    logger.info('Input label dimension is %d' % lab_dim)
    suffix=str(lab_dim)
    label_data_dir = cfg.work_dir

    binary_label_dir      = os.path.join(label_data_dir, 'binary_label_'+str(label_normaliser.dimension))
    nn_label_dir          = os.path.join(label_data_dir, 'nn_no_silence_lab_'+suffix)
    nn_label_norm_dir     = os.path.join(label_data_dir, 'output')

    min_max_normaliser = None
    label_norm_file = 'label_norm_%s_%d.dat' %(cfg.label_style, lab_dim)
    label_norm_file = os.path.join(data_dir, label_norm_file)

    try:
        test_id_list = read_file_list(cfg.test_id_scp)
        logger.debug('Loaded file id list from %s' % cfg.test_id_scp)
    except IOError:
        logger.critical('Could not load file id list from %s' % cfg.test_id_scp)
        raise

    in_label_align_file_list = prepare_file_path_list(test_id_list, cfg.in_label_align_dir, cfg.lab_ext, False)
    binary_label_file_list   = prepare_file_path_list(test_id_list, binary_label_dir, cfg.lab_ext)
    nn_label_file_list       = prepare_file_path_list(test_id_list, nn_label_dir, cfg.lab_ext)
    nn_label_norm_file_list  = prepare_file_path_list(test_id_list, nn_label_norm_dir, cfg.lab_ext)

    logger.info('preparing label data (input) using standard HTS style labels')
    label_normaliser.perform_normalisation(in_label_align_file_list, binary_label_file_list, label_type=cfg.label_type)
    remover = SilenceRemover(n_cmp = lab_dim, silence_pattern = cfg.silence_pattern, label_type=cfg.label_type, remove_frame_features = cfg.add_frame_features, subphone_feats = cfg.subphone_feats)
    remover.remove_silence(binary_label_file_list, in_label_align_file_list, nn_label_file_list)

    min_max_normaliser = MinMaxNormalisation(feature_dimension = lab_dim, min_value = 0.01, max_value = 0.99)
    min_max_normaliser.load_min_max_values(label_norm_file)
    min_max_normaliser.normalise_data(binary_label_file_list, nn_label_norm_file_list)


        
if __name__ == '__main__':

    cfg=configuration.cfg
    logging.setLoggerClass(LoggerPlotter)
    logger = logging.getLogger("main")

    if len(sys.argv) != 2:
        logger.critical('usage: linguisticExtraction.py [config file name]')
        sys.exit(1)

    config_file = sys.argv[1]

    config_file = os.path.abspath(config_file)
    cfg.configure(config_file)
    main_function(cfg)

    sys.exit(0)
