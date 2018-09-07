9# -*- coding: utf-8 -*-
"""
Created on Sat Sep  1 21:23:07 2018
@author: admin
"""

from model_tf import Load_RCNN
from model_tf import Run
from merge_image import Imageprocesor

class Server():
    def __init__(self,srcargs):
        self.graph, self.session = Load_RCNN(srcargs)
        self.logic = Imageprocesor(srcargs)


    def RUNCNN(self,impath,region):
        print("impath is",impath)
        image_np = self.logic.merge_image(impath,region)
        if image_np == None:
            return None,-1
        
        print("in server.py, boxid = ",region.boxid)
        CnnRawResults = Run(image_np,self.graph, self.session)     
        
        for i in range(len(CnnRawResults['detection_boxes'])):
            print(CnnRawResults['detection_boxes'][i])
            print(CnnRawResults['detection_scores'][i])
        CNN_result = []
        if len(CnnRawResults['detection_boxes']) == 0:
            CNN_result.append([0,0,0,0,0.1,'no obj',region.boxid])
        else:
            num_low_conf = 0
            for i in range(len(CnnRawResults['detection_boxes'])):
                x1 = float(CnnRawResults['detection_boxes'][i][1])
                y1 = float(CnnRawResults['detection_boxes'][i][0])
                w = (float(CnnRawResults['detection_boxes'][i][3]) - float(CnnRawResults['detection_boxes'][i][1]))
                h = (float(CnnRawResults['detection_boxes'][i][2]) - float(CnnRawResults['detection_boxes'][i][0]))
            
                conf = float(CnnRawResults['detection_scores'][i])
                if conf < 0.8:
                    num_low_conf += 1
                label = CnnRawResults['detection_classes'][i]
                box_id = CnnRawResults['bbox_id'][i]
                CNN_result.append([x1,y1,w,h,conf,label,box_id])
        return CNN_result,num_low_conf
