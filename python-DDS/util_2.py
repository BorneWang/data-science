# -*- coding: utf-8 -*-
"""
Created on Tue Sep  4 00:40:49 2018

@author: admin
"""

import os

class Region():
    def __init__(self,frameID,x,y,w,h,res,box_id=0):
        self.frameID = frameID
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.res = res
        self.boxID = box_id

class Segment():
    def __init__(self):
        self.frameIdList = []
    def GetFrameIdList(self):
        return self.frameIdList

class UnitResult():
    def __init__(self,frameID,x,y,w,h,confidence,label,res,box_id=0):
        self.frameID = frameID
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.confidence = confidence
        self.label = label
        self.res = res
        self.boxID = box_id

class Result():
    def __init__(self):
        self.unitResults = []
    def AddResult(self, other):
        for unit in other.unitResults:
            if unit in self.unitResults:
                continue
            else:
                self.unitResults.append(unit)
    def CountObjts(self):
        objs = {}
        for oneresult in self.unitResults:
            frameID = oneresult.frameID
            if frameID in objs:
                objs[frameID] += 1
            else:
                objs[frameID] = 1
        return objs


def increaseRes(oldres):
    if oldres == 0.25:
        newres = 0.5
    elif oldres == 0.5:
        newres = 0.75
    else:
        newres = 1
    return newres
 
            
def checkexistInServer(frameID):
    count = -1
    while True:
        path = 'Sendtoserver/' + frameID + '.png'
        if os.path.exists(path):
            frameID += str(count)
            count -= 1
        else:
            break
    return frameID


def outputTofile(inputresult):
    if type(inputresult) == list:
        outfile = open('debug_log/regions_bug','a')
        for region in inputresult:
            print("region.frameID :",region.frameID,file=outfile)
            print("region.x :",region.x,file=outfile)
            print("region.y :",region.y,file=outfile)
            print("region.w :",region.w,file=outfile)
            print("region.h :",region.h,file=outfile)
            print("region.res :",region.res,file=outfile)
        outfile.close()
    else:
        outfile = open('Results/serverSideResults','a')
        for region in inputresult.unitResults:
            print(region.frameID,region.x,region.y,region.w,region.h,
                  region.label,region.confidence,region.res,sep=',',file=outfile)
        outfile.close()
