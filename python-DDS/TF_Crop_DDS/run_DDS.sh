Database=$1

python3 main.py --src /home/bowen/data/$Database/src --logic GroundTruth
python3 main.py --src /home/bowen/data/$Database/src --logic DDS
./run_eval_DDS.sh >> Ten_videos_results/Five_videos_DDS.log
rm -r DDS
rm -r GroundTruth
