#!/bin/bash

VIDEO=$1
DATABASE=$2

if [ ! -f ~/videos/$VIDEO.mov ]
then
scp bowenw@users.emulab.net:/proj/DeepEdgeVideo/stream-measurement/samples-1k/picks/$VIDEO.mov ~/videos/
fi

mkdir ~/data/$DATABASE-$VIDEO
mkdir ~/data/$DATABASE-$VIDEO/src
ffmpeg -loglevel error -i ~/videos/$VIDEO.mov -crf 1 -vcodec libx264 ~/videos/$VIDEO.mp4
ffmpeg -y -i ~/videos/$VIDEO.mp4 -q:v 1 -vsync 0 -start_number 0 ~/data/$DATABASE-$VIDEO/src/%010d.jpeg

if [ ! -f ~/videos/$VIDEO.mp4 ]
then
echo error !!!
else
./run_crf_res.sh $DATABASE $VIDEO
rm -r ~/data/$DATABASE-$VIDEO
rm ~/videos/$VIDEO.mp4
fi

mkdir ~/data/$DATABASE-$VIDEO
mkdir ~/data/$DATABASE-$VIDEO/src
ffmpeg -loglevel error -i ~/videos/$VIDEO.mov -qp 1 -vcodec libx264 ~/videos/$VIDEO.mp4
ffmpeg -y -i ~/videos/$VIDEO.mp4 -q:v 1 -vsync 0 -start_number 0 ~/data/$DATABASE-$VIDEO/src/%010d.jpeg

if [ ! -f ~/videos/$VIDEO.mp4 ]
then
echo error !!!
else
./run_qp.sh $DATABASE $VIDEO
rm -r ~/data/$DATABASE-$VIDEO
rm ~/videos/$VIDEO.mp4
fi

rm ~/videos/$VIDEO.mov
