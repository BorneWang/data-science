# -*- coding: utf-8 -*-
"""
Created on Sat Sep  1 21:23:07 2018
@author: admin
"""


import cv2
import os
import numpy as np
import time

class Server():
    def RUNCNN(self,impath):
        print("impath is",impath)
        im = cv2.imread(impath)
        im_shape = im.shape
        im_size_min = np.min(im_shape[0:2])
        im_size_max = np.max(im_shape[0:2])
        outfile = impath + 'serverresult'
        tic = time.time()
        os.system("python3 /home/bowen/python-DDS/rcnn/demo2.py --gpu 0 --dataset voc --network resnet101 --params rcnn/resnet_voc0712-0010.params --img-short-side {} --img-long-side {} --image {} --out {}".format(im_size_min,im_size_max,impath,outfile))
        tic2 = time.time()
        print("Run Cnn time is ",tic2-tic)
        CNN_result = []
        with open(outfile) as f:
            for line in f:
                CNN_result.append(line)
        return CNN_result
