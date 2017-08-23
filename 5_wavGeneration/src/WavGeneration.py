
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

from Replace_f0 import replace_f0
from getf0 import get_f0_label
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
from frontend.parameter_generation import ParameterGeneration
import configuration
from utils.generate import generate_wav
from utils.generate import run_process
from utils.learn_rates import ExpDecreaseLearningRate
from io_funcs.binary_io import  BinaryIOCollection
from logplot.logging_plotting import LoggerPlotter, MultipleSeriesPlot, SingleWeightMatrixPlot
import logging # as logging
import logging.config
import StringIO

def copyfile(sourpath,destpath):
    for f in os.listdir(sourpath):
	sourfile=sourpath+"//"+f
	shutil.copy(sourfile,destpath)

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

    try:
        test_id_list = read_file_list(cfg.test_id_scp)
        logger.debug('Loaded file id list from %s' % cfg.test_id_scp)
    except IOError:
        logger.critical('Could not load file id list from %s' % cfg.test_id_scp)
        raise


    logger.info('generating from DNN')

    var_dir   = os.path.join(data_dir, 'var')
    if not os.path.exists(var_dir):
        os.makedirs(var_dir)

    var_file_dict = {}
    for feature_name in cfg.out_dimension_dict.keys():
        var_file_dict[feature_name] = os.path.join(var_dir, feature_name + '_' + str(cfg.out_dimension_dict[feature_name]))

    ###normalisation information
    norm_info_file = os.path.join(data_dir, 'norm_info' + cfg.combined_feature_name + '_' + str(cfg.cmp_dim) + '_' + cfg.output_feature_normalisation + '.dat')
    gen_file_id_list = test_id_list
    ### comment the below line if you don't want the files in a separate folder
    gen_dir = cfg.test_synth_dir
    if not os.path.exists(gen_dir):
        os.mkdir(gen_dir)
    copyfile(cfg.nn_norm_temp_dir, gen_dir)
    try:
        os.makedirs(gen_dir)
    except OSError as e:
        if e.errno == errno.EEXIST:
            # not an error - just means directory already exists
            pass
        else:
            logger.critical('Failed to create generation directory %s' % gen_dir)
            logger.critical(' OS error was: %s' % e.strerror)
            raise

    gen_file_list = prepare_file_path_list(gen_file_id_list, gen_dir, cfg.cmp_ext)
    logger.debug('denormalising generated output using method %s' % cfg.output_feature_normalisation)

    fid = open(norm_info_file, 'rb')
    cmp_min_max = numpy.fromfile(fid, dtype=numpy.float32)
    fid.close()
    cmp_min_max = cmp_min_max.reshape((2, -1))
    cmp_min_vector = cmp_min_max[0, ]
    cmp_max_vector = cmp_min_max[1, ]

    if cfg.output_feature_normalisation == 'MVN':
        denormaliser = MeanVarianceNorm(feature_dimension = cfg.cmp_dim)
        denormaliser.feature_denormalisation(gen_file_list, gen_file_list, cmp_min_vector, cmp_max_vector)

    elif cfg.output_feature_normalisation == 'MINMAX':
        denormaliser = MinMaxNormalisation(cfg.cmp_dim, min_value = 0.01, max_value = 0.99, min_vector = cmp_min_vector, max_vector = cmp_max_vector)
        denormaliser.denormalise_data(gen_file_list, gen_file_list)
    else:
        logger.critical('denormalising method %s is not supported!\n' %(cfg.output_feature_normalisation))
        raise

    generator = ParameterGeneration(gen_wav_features = cfg.gen_wav_features, enforce_silence = cfg.enforce_silence)
    generator.acoustic_decomposition(gen_file_list, cfg.cmp_dim, cfg.out_dimension_dict, cfg.file_extension_dict, var_file_dict, do_MLPG=cfg.do_MLPG, cfg=cfg)

    #copyfile(cfg.in_lf0_dir, gen_dir)

    lf0_tmp_dir =os.path.join(gen_dir, 'lf0temp')
    if not os.path.exists(lf0_tmp_dir):
        os.mkdir(lf0_tmp_dir)

    given_lf0_folder =os.path.join(lf0_tmp_dir, 'given')
    predicted_lf0_folder =os.path.join(lf0_tmp_dir, 'predicted')
    output_lf0_folder =os.path.join(lf0_tmp_dir, 'output')

    if not os.path.exists(given_lf0_folder):
        os.mkdir(given_lf0_folder)
    if not os.path.exists(predicted_lf0_folder):
        os.mkdir(predicted_lf0_folder)
    if not os.path.exists(output_lf0_folder):
        os.mkdir(output_lf0_folder)

    for i in os.listdir(cfg.in_lf0_dir):
        if os.path.splitext(i)[1] == '.lf0':
            given_lf0 = os.path.join(cfg.in_lf0_dir,i)
            print(given_lf0)
            run_process('{x2x} +fa < {bin} > {asc}'
                        .format(x2x=cfg.SPTK['X2X'], bin=os.path.join(cfg.in_lf0_dir,i), asc=os.path.join(given_lf0_folder, os.path.splitext(i)[0] + '.lf0a')))

    for i in os.listdir(gen_dir):
        if os.path.splitext(i)[1] == '.lf0':
            run_process('{x2x} +fa < {bin} > {asc}'
                        .format(x2x=cfg.SPTK['X2X'], bin=os.path.join(gen_dir, i),
                                asc=os.path.join(predicted_lf0_folder, os.path.splitext(i)[0] + '.lf0a')))

    replace_f0(given_lf0_folder, predicted_lf0_folder, output_lf0_folder)

    f0_label_folder = os.path.join(gen_dir,'f0_label')
    if not os.path.exists(f0_label_folder):
        os.mkdir(f0_label_folder)
    for i in gen_file_id_list:
        given_lf0_file_path = os.path.join(output_lf0_folder, i + '.lf0a')
        f0_label_file_path = os.path.join(f0_label_folder, i + '.lab')
        get_f0_label(cfg.f0_question_set,cfg.f0_level,given_lf0_file_path,f0_label_file_path)
	
    for i in os.listdir(output_lf0_folder):
        if os.path.splitext(i)[1] == '.lf0a':
            run_process('{x2x} +af < {asc} > {bin}'
                        .format(x2x=cfg.SPTK['X2X'], asc=os.path.join(output_lf0_folder, i),
                                bin=os.path.join(gen_dir, os.path.splitext(i)[0] + '.lf0')))

# End

    ### generate wav
    logger.info('reconstructing waveform(s)')
    generate_wav(gen_dir, gen_file_id_list, cfg)     # generated speech

    	
if __name__ == '__main__':

    cfg=configuration.cfg
    logging.setLoggerClass(LoggerPlotter)
    logger = logging.getLogger("main")

    if len(sys.argv) != 2:
        logger.critical('usage: WaveGeneration.py [config file name]')
        sys.exit(1)

    config_file = sys.argv[1]

    config_file = os.path.abspath(config_file)
    cfg.configure(config_file)
    main_function(cfg)

    sys.exit(0)
