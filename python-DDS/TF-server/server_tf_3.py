# -*- coding: utf-8 -*-
"""
Created on Sat Sep  1 21:23:07 2018
@author: admin
"""


#import cv2
import numpy as np
import time
from model_tf import Load_RCNN
from model_tf import Run

class Server():
    def __init__(self,srcargs):
        self.graph, self.session = Load_RCNN(srcargs)


    def RUNCNN(self,impath,boxid):
        print("impath is",impath)
        #im = cv2.imread(impath)
        #im_shape = im.shape
        tic = time.time()
        print("in server.py, boxid = ",boxid)
        CnnRawResults = Run(impath,self.graph, self.session, boxid)     
        tic2 = time.time()
        print("Run Cnn time is ",tic2-tic)
        for i in range(len(CnnRawResults['detection_boxes'])):
            print(CnnRawResults['detection_boxes'][i])
            print(CnnRawResults['detection_scores'][i])
        
        CNN_result = []
        if len(CnnRawResults['detection_boxes']) == 0:
            CNN_result.append([0,0,0,0,0.1,'no obj',boxid])
        else:
            for i in len(CnnRawResults['detection_boxes']):
                x1 = float(CnnRawResults['detection_boxes'][i][1])
                y1 = float(CnnRawResults['detection_boxes'][i][0])
                w = (float(CnnRawResults['detection_boxes'][i][3]) - float(CnnRawResults['detection_boxes'][i][1]))
                h = (float(CnnRawResults['detection_boxes'][i][2]) - float(CnnRawResults['detection_boxes'][i][0]))
            
                conf = float(CnnRawResults['detection_scores'][i])
                label = CnnRawResults['detection_classes'][i]
                box_id = CnnRawResults['bbox_id'][i]
                CNN_result.append([x1,y1,w,h,conf,label,box_id])
        return CNN_result
