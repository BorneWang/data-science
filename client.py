# -*- coding: utf-8 -*-
"""
Created on Sat Sep  1 21:23:17 2018
@author: admin
"""

import glob
import os
import time

LOGIC_DDS = "DDS"
LOGIC_GROUNDTRUTH = "GroundTruth"
LOGIC_NOSCOPE = "NoScope"

RES_LOW = 0.25
RES_MEDIUM = 0.5
RES_HIGH = 0.75
RES_LIST = [RES_LOW, RES_MEDIUM, RES_HIGH]

class Region():
    def __init__(self,frameID,x,y,w,h,res):
        self.frameID = frameID
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.res = res

class Segment():
    def __init__(self):
        self.frameIdList = []
    def GetFrameIdList(self):
        return self.frameIdList

class UnitResult():
    def __init__(self,frameID,x,y,w,h,confidence,label,res):
        self.frameID = frameID
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.confidence = confidence
        self.label = label
        self.res = res

class Result():
    def __init__(self):
        self.unitResults = []
    def AddResult(self, other):
        for unit in other.unitResults:
            self.unitResults.append(unit)
    def CountObjts(self):
        objs = []
        for oneresult in self.unitResult:
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

            

class Filtering():
    def __init__(self,args):
        self.logic = args.logic
        
    def Run(self,segment):
        if self.logic == LOGIC_DDS:
            return segment
        else:
            return segment
 
class DecisionMaker():
    def __init__(self,args):
        self.logic = args.logic
        # DDS fields
        self.maxThres = 0.8
        self.minThres = 0.3
        self.DiffDic = {}
        # GroundTruth fields
        self.var3 = 0
        # NoScope/Glimpse/Vigil fields
    
    def GetNextRegionToQuery(self, segment, Results):
        regions = []
        frames = segment.GetFrameIdList()
        if self.logic == LOGIC_GROUNDTRUTH:
            for frameId in frames:
                regions.append(Region(frameId,0,0,1280,720,1))
            return regions
        if self.logic == LOGIC_DDS:
            if Results == []:
                regions.append(Region(frames[0],0,0,1280,720,0.25))
                regions.append(Region(frames[len(frames)-1],0,0,1280,720,0.25))
                self.DiffDic[(frames[0],frames[len(frames)-1])] = -1
                return regions
            else:
                objs = Results.CountObjs()          #type objs is DIC
                #update DiffDic
                maxkey = ()
                maxdiff = -1
                for key in self.DiffDic:
                    diff = objs[key[0]] - objs[key[1]]
                    self.DiffDic[key] = abs(diff)
                    if diff > maxdiff:
                        maxkey = key
                        
                        #FrameSelection
                        if maxkey[1] - maxkey[0] > 1:
                            midframe = int(maxkey[1] - maxkey[0] / 2)
                            del self.DiffDic[maxkey]
                            self.DiffDic[(maxkey[0],midframe)] = -1
                            self.DiffDic[(maxkey[1],midframe)] = -1
                            regions.append(Region(midframe,0,0,1,1,0.25))
            
                        #Croping
                        for ret in Results:
                            if ret.confidence > self.minThres and ret.confidence < self.maxThres:
                                if ret.res != 1:
                                    newResolution = increaseRes(ret.res)
                                    regions.append(Region(ret.frameID,
                                                              ret.x,
                                                              ret.y,
                                                              ret.w,
                                                              ret.h,
                                                              newResolution))
            return regions
        #if self.logic == Noscope:
        #    return None
       # if self.logic == Vigil:
        #    return None
            
            

class Client():
    def __init__(self,args,srv):
        self.src = args.src
        self.logic = DecisionMaker(args)
        self.filtering = Filtering(args)
        self.server = srv
        self.lastupdatetime = 0
       
        
    def getImage(self,region):
        frameID = str(region.frameID)
        frameID = frameID.zfill(10)
        framePath = self.src + '/' + frameID + '.png'
        impath = 'Sendtoserver/' + frameID + '.png'
        w = region.w
        h = region.h
        x = region.x
        y = region.y
        print("ffmpeg framepath is",framePath)
        os.system("ffmpeg -loglevel error -i {0} -vf scale=iw*{1}:ih*{1} -filter:v \"crop={2}:{3}:{4}:{5}\" -y {6}".format(framePath,
                                                                                                   region.res,
                                                                                                   w,
                                                                                                   h,
                                                                                                   x,
                                                                                                   y,
                                                                                                   impath))
        print("ffmpeg impath is",impath)
        return impath
 
              
    def QueryCNN(self, Regions):
        Results = Result()
        for region in Regions:
            tic = time.time()
            impath = self.getImage(region)
            tic2 = time.time()
            print("**********************the time of get image is ************************************",tic2-tic)
            infresult = self.server.RUNCNN(impath)
            for line in infresult:
                lineresult = line.split(' ')
                x = float(lineresult[2]) 
                y = float(lineresult[3])
                w = float(lineresult[4]) - x
                h = float(lineresult[5]) - y
                conf = float(lineresult[1])
                label = lineresult[0]
                uniret = UnitResult(region.frameID,x,y,w,h,conf,label,region.res)
                Results.unitResults.append(uniret)
        return Results
    
    def getNextSegment(self,now,maxsize=4):
        Allframes = sorted(glob.glob('{}/*.png'.format(self.src)))
        print("src is ",self.src)
        print("======================================= from last update: ",time.time()-self.lastupdatetime)
        self.lastupdatetime = time.time()
        seg = Segment()
        now += 1
        if now == len(Allframes):
            return seg
        count = 0
        for frame in Allframes[now:]:
            now +=1
            print("frame is ",frame[len(frame)-14:len(frame)-4])
            frameID = int(frame[len(frame)-14:len(frame)-4])
           seg.frameIdList.append(frameID)
            count += 1
            if count == maxsize:
                return seg, now
        return seg,now      
        

    
            
    def UpdateResult(self,frames,Results):
        for ret in Results.unitResults:
             print("ret.frameID is",ret.frameID)
             if ret.frameID in frames.frameIdList:
                 frames.frameIdList.remove(ret.frameID)
        return frames
    
    #def Track(frames):
    
    
    def Run(self):
        now = -1
        while True:
            segment,now = self.getNextSegment(now)
            #print("segment is",segment.frameIdList[0])
            if segment.GetFrameIdList == []:
                return None
            FramdIDAfterLoacalFiltering = self.filtering.Run(segment)
            results = Result()
            RegionsToQuery = []
            while True:
                RegionsToQuery = self.logic.GetNextRegionToQuery(FramdIDAfterLoacalFiltering,
                                                                results)
                if len(RegionsToQuery) == 0:
                    break
                CNNResult = self.QueryCNN(RegionsToQuery)
                results.AddResult(CNNResult)
                FramdIDAfterLoacalFiltering = self.UpdateResult(FramdIDAfterLoacalFiltering,results)
