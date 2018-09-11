Database=$1
Video=$2

python3 main.py --src /home/bowen/data/$Database/src --logic MPEG --video /home/bowen/videos/$Video.mov --crf 1
mv MPEG GroundTruth
rm -r GroundTruth/tempReserve

for crf in 1 10 23 30 40 46 51
do
python3 main.py --src /home/bowen/data/$Database/src --logic MPEG --video /home/bowen/videos/$Video.mov --crf $crf
./run_eval_MPEG.sh >> Ten_videos_results/new_Ten_videos_crf_$crf.log
rm -r MPEG/tempReserve
mv MPEG Results/MPEG_${Database}_crf_$crf
done

'''
for res in 1 0.9 0.8 0.6 0.4 0.2 0.1
do
python3 main.py --src /home/bowen/data/$Database/src --logic MPEG --video /home/bowen/videos/$Video.mov --res $res --crf 18
./run_eval_MPEG.sh >> Ten_videos_results/new_Ten_videos_res_$res.log
rm MPEG -r
done
'''

mv GroundTruth Results/MPEG_${Database}_qp_truth
