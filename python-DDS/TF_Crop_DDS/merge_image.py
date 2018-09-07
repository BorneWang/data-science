# -*- coding: utf-8 -*-
"""
Created on Thu Sep  6 14:58:01 2018

@author: admin
"""

import cv2
import numpy as np

class Imageprocesor():
    def __init__(self,args):
        self.imagelist = {}
        self.logic = args.logic
        
    def merge_image(self,impath,region):
        if self.logic == 'DDS':
            frameID = impath[len(impath)-15:len(impath)-5]
            self.imagelist[frameID].append(impath)
            if region.res == 0.25:
                self.imagelist[frameID] = []
                self.imagelist[frameID].append(impath)
                img = cv2.imread(impath)
                return img.astype(np.uint8)
            else:
                im_list = self.imagelist[frameID]
                if region.num <= len(im_list):
                    im_back = cv2.imread(im_list[0])
                    scale = float(1/region.res)
                    im_back = cv2.resize(im_back,None,fx=scale, fy=scale, interpolation = cv2.INTER_CUBIC)
                    for imfpath in im_list:
                        im_front = cv2.imread(imfpath)
                        w_begin = im_back.shape[0]*region.x
                        h_begin = im_back.shape[1]*region.y
                        w_end = w_begin + im_back.shape[0]*region.w
                        h_end = h_begin + im_back.shape[1]*region.h
                        for i in range(w_begin,w_end):
                            for j in range(h_begin,h_end):
                                im_back[i][j][0] = im_front[i-w_begin][j-h_begin][0]
                                im_back[i][j][0] = im_front[i-w_begin][j-h_begin][1]
                                im_back[i][j][0] = im_front[i-w_begin][j-h_begin][2]
                    return im_back.astype(np.uint8)
                else:
                    return None
        if self.logic == 'GroundTruth':
            img = cv2.imread(impath)
            return img.astype(np.uint8)
