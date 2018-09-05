# -*- coding: utf-8 -*-
"""
Created on Sat Sep  1 21:23:07 2018
@author: admin
"""


#import cv2
import numpy as np
import time
from tf_model import Load_RCNN
from tf_model import Run

class Server():
    def __init__(self,srcargs):
        self.model = Load_RCNN(srcargs)


    def RUNCNN(self,impath,boxid):
        print("impath is",impath)
        #im = cv2.imread(impath)
        #im_shape = im.shape
        tic = time.time()
        print("in server.py, boxid = ",boxid)
        CnnRawResults = Run(impath,self.model,boxid)     
        tic2 = time.time()
        print("Run Cnn time is ",tic2-tic)
        print("the length of the result",len(CnnRawResults['detection_boxes']))
        '''
        CNN_result = []
        if len(CnnRawResults) == 0:
            CNN_result.append([0,0,0,0,0.1,'no obj',boxid])
        else:
            for lineresult in CnnRawResults:
                x = float(lineresult[2]) / im_shape[1]
                y = float(lineresult[3]) / im_shape[0]
                w = (float(lineresult[4]) - float(lineresult[2])) / im_shape[1]
                h = (float(lineresult[5]) - float(lineresult[3])) / im_shape[0]
                conf = float(lineresult[1])
                label = lineresult[0]
                box_id = lineresult[6]
                CNN_result.append([x,y,w,h,conf,label,box_id])
        return CNN_result
        '''
