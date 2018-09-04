# -*- coding: utf-8 -*-
"""
Created on Sat Sep  1 21:23:17 2018
@author: admin
"""

import glob
import os
import time
from tracker import KCF_tracker

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
        self.src == args.src
        # DDS fields
        self.Maxpick = 4
        self.pick_count = 0
        self.maxThres = 0.8
        self.minThres = 0.3
        self.DiffDic = {}
        self.tracker_last = 0
        # GroundTruth fields
        self.var3 = 0
        # NoScope/Glimpse/Vigil fields
    
    def GetNextRegionToQuery(self, segment, Results):
        regions = []
        frames = segment.GetFrameIdList()
        if self.logic == LOGIC_GROUNDTRUTH:
            for frameId in frames:
                regions.append(Region(frameId,0,0,1,1,1))
            return regions
        if self.logic == LOGIC_DDS:
            #print("Begin DDS logic")
            if len(Results.unitResults) == 0:
                self.DiffDic = {}
                regions.append(Region(frames[0],0,0,1,1,0.25))
                regions.append(Region(frames[len(frames)-1],0,0,1,1,0.25))
                self.DiffDic[(frames[0],frames[len(frames)-1])] = -1
                self.pick_count +=2
                return regions
            else:
                #Croping
                for ret in Results.unitResults:
                    if ret.confidence > self.minThres and ret.confidence < self.maxThres:
                       if ret.res != 1:
                           newResolution = increaseRes(ret.res)
                           regions.append(Region(ret.frameID,
                                                 ret.x,
                                                 ret.y,
                                                 ret.w,
                                                 ret.h,
                                                 newResolution))
                if self.pick_count == self.Maxpick:
                    self.pick_count = 0
                    return regions
                objs = Results.CountObjts()          #type objs is DIC
                #print("objs are", objs)
                #update DiffDic
                #print("my diffDIc are",self.DiffDic)
                maxkey = ()
                maxdiff = -1
                for key in self.DiffDic:
                    #print("key is",key)
                    diff = objs[key[0]] - objs[key[1]]
                    if diff < 0:
                       diff = -diff
                    self.DiffDic[key] = diff
                    if diff > maxdiff:
                        maxkey = key
                        
                #FrameSelection
                #print("maxkey is",maxkey)
                if maxkey[1] - maxkey[0] > 1:
                    midframe = int((maxkey[1] + maxkey[0]) / 2)
                    print("midframe is :",midframe)
                    del self.DiffDic[maxkey]
                    self.DiffDic[(maxkey[0],midframe)] = -1
                    self.DiffDic[(maxkey[1],midframe)] = -1
                    regions.append(Region(midframe,0,0,1,1,0.25))
                    self.pick_count += 1
            return regions
        #if self.logic == Noscope:
        #    return None
       # if self.logic == Vigil:
        #    return None
    
    def updateResults(results):
        for i in range(len(results.unitResults)):
            for j in range(i+1,len(results.unitResults)):
                if results.unitResults[i].frameID == results.unitResults[j].frameID:
                    if results.unitResults[i].boxID == results.unitResults[j].boxID:
                        results.unitResults[i].res = results.unitResults[j].res
                        results.unitResults[i].confidence = results.unitResults[j].confidence
                        results.unitResults.remove(results.unitResults[j])
                
    
    
    
    def Tracking_label(self,frameID,now_boxes,results):
        frameID = str(frameID)
        frameID = frameID.zfill(10)
        OutPath = 'Clienttracking/' + frameID + '.result'
        Out = open(OutPath,'w')
        i = 0
        for result in results.unitResults:
            if result.frameID == self.tracker_last and result.confidence >self.maxThres:
                if i < len(now_boxes):
                    print(result.label,now_boxes[i],file=Out)
                    i += 1
                else:
                    break
        Out.close()
                
    
    
    def Tracking(self,frames,results):
        refe_boxes = []
        for result in results.unitResults:
            if result.frameID == self.tracker_last and result.confidence > self.maxThres:
                one_box = [result.x,result.y,result.w,result.h]
                refe_boxes.append(one_box)
        tracker = KCF_tracker(self.tracker_last,refe_boxes,self.src)
        for frameID in frames.frameIdList:
            now_boxes = tracker.Update(frameID)
            self.Tracking_label(frameID,now_boxes,results)
            
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
        outfile = open('debug_log/result_bug','a')
        for region in inputresult.unitResults:
            print("ret.frameID :",region.frameID,file=outfile)
            print("ret.x :",region.x,file=outfile)
            print("ret.y :",region.y,file=outfile)
            print("ret.w :",region.w,file=outfile)
            print("ret.h :",region.h,file=outfile)
            print("ret.conf :",region.confidence,file=outfile)
            print("ret.label :",region.label,file=outfile)
            print("region.res :",region.res,file=outfile)
        outfile.close()

class Client():
    def __init__(self,args,srv):
        self.src = args.src
        self.logic = DecisionMaker(args)
        self.filtering = Filtering(args)
        self.server = srv
        self.lastupdatetime = 0
        self.tracker_last = 0
        #self.outPath = args.output
       
        
    def getImage(self,region):
        frameID = str(region.frameID)
        frameID = frameID.zfill(10)
        framePath = self.src + '/' + frameID + '.png'
        new_frameID = checkexistInServer(frameID)
        tempPath = 'tempReserve/' + new_frameID + '.png'
        impath = 'Sendtoserver/' + new_frameID + '.png'
        w = region.w
        h = region.h
        x = region.x
        y = region.y
        #print("ffmpeg framepath is",framePath)
        os.system("ffmpeg -loglevel error -i {} -filter:v \"crop=iw*{}:ih*{}:iw*{}:ih*{}\" -y {}".format(framePath,w,h,x,y,tempPath))
        os.system("ffmpeg -loglevel error -i {0} -vf scale=iw*{1}:ih*{1}".format(tempPath,region.res))
        os.system("rm {}".format(tempPath))
        #print("ffmpeg impath is",impath)
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
                x = line[0] 
                y = line[1]
                w = line[2]
                h = line[3]
                conf = line[4]
                label = line[5]
                box_id = line[6]
                uniret = UnitResult(region.frameID,x,y,w,h,conf,label,region.res,box_id)
                Results.unitResults.append(uniret)
        return Results
    
    def getNextSegment(self,now,maxsize=8):
        Allframes = sorted(glob.glob('{}/*.png'.format(self.src)))
        print("src is ",self.src)
        seg = Segment()
        if now == len(Allframes):
            return seg
        print("======================================= from last update: ",time.time()-self.lastupdatetime)
        self.lastupdatetime = time.time()
        count = 0
        for frame in Allframes[now:]:
            now +=1
            #print("frame is ",frame[len(frame)-14:len(frame)-4])
            frameID = int(frame[len(frame)-14:len(frame)-4])
            seg.frameIdList.append(frameID)
            count += 1
            if count == maxsize:
                return seg, now
        return seg,now      
    
    
    
    def UpdateFrameList(self,frames,Results):
        for ret in Results.unitResults:
            #print("ret.frameID is",ret.frameID)
            if ret.frameID in frames.frameIdList:
                frames.frameIdList.remove(ret.frameID)
        return frames
    
    
    def Run(self):
        now = 0
        while True:
            segment,now = self.getNextSegment(now)
            self.logic.tracker_last = segment.frameIdList[0]
            print("the last tracker is ",self.tracker_last)
            if segment.GetFrameIdList == []:
                return None
            FramdIDAfterLoacalFiltering = self.filtering.Run(segment)
            results = Result()
            RegionsToQuery = []
            while True:
                print("Begin to run logic")
                RegionsToQuery = self.logic.GetNextRegionToQuery(FramdIDAfterLoacalFiltering,
                                                                results)
                outputTofile(RegionsToQuery)
                if len(RegionsToQuery) == 0:
                    break
                print("Begin to ask CNN")
                CNNResult = self.QueryCNN(RegionsToQuery)
                results.AddResult(CNNResult)
                outputTofile(results)
                FramdIDAfterLoacalFiltering = self.UpdateFrameList(FramdIDAfterLoacalFiltering,results)
                results = self.logic.updateResults(results)
                
                
            if len(FramdIDAfterLoacalFiltering.frameIdList) != 0:
                self.logic.Tracking(FramdIDAfterLoacalFiltering,results)
