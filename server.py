# -*- coding: utf-8 -*-
"""
Created on Sat Sep  1 21:23:07 2018

@author: admin
"""


import argparse
import ast
import pprint
import cv2
import os
import np

import mxnet as mx
from mxnet.module import Module

from symdata.bbox import im_detect
from symdata.loader import load_test, generate_batch
from symdata.vis import vis_detection
from symnet.model import load_param, check_shape
from model import ModelRUN
from client import UnitResult

class server():
        
    def RUNCNN(self,impath):
        im = cv2.imread(impath)
        im_shape = im.shape
        im_size_min = np.min(im_shape[0:2])
        im_size_max = np.max(im_shape[0:2])
        outfile = impath + 'serverresult'
        os.system("python3 demo.py --dataset voc --network resnet101 --params resnet101_voc0010.params --img-short-side {} --img-long-side {} --image {} --out {}".format(im_size_min,im_size_max,impath,outfile))
        CNN_result = []
        with open(outfile) as f:
            for line in f:
                CNN_result.append(line) 
        os.system("rm {}".format(outfile))
        return CNN_result
        
