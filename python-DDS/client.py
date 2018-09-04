# -*- coding: utf-8 -*-
"""
Created on Sat Sep  1 21:23:17 2018
@author: admin
"""

import glob
import os
import time
from logic import DecisionMaker, Filtering
from util import checkexistInServer, outputTofile, Segment, UnitResult, Result


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
        os.system("ffmpeg -loglevel error -i {0} -vf scale=iw*{1}:ih*{1} {2}".format(tempPath,region.res,impath))
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
            print("the box id is :",region.boxID)
            infresult = self.server.RUNCNN(impath,region.boxID)
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
                #outputTofile(RegionsToQuery)
                if len(RegionsToQuery) == 0:
                    break
                print("Begin to ask CNN")
                CNNResult = self.QueryCNN(RegionsToQuery)
                results.AddResult(CNNResult)
                #outputTofile(results)
                FramdIDAfterLoacalFiltering = self.UpdateFrameList(FramdIDAfterLoacalFiltering,results)
                results = self.logic.updateResults(results)
               
                
            if len(FramdIDAfterLoacalFiltering.frameIdList) != 0:
                self.logic.Tracking(FramdIDAfterLoacalFiltering,results)
