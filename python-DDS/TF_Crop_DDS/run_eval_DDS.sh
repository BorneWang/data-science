
#echo DDS :
python3 Eval.py --truth GroundTruth/Results/serverSideResults --ServerSideResults DDS/Results/serverSideResults

totalB=`find DDS/Sendtoserver -name "*jpeg" | xargs du -cb | tail -1`
totalNum=`ls DDS/Sendtoserver | wc -l`
totalBytes=` echo ${totalB%to*}`
echo total : $totalBytes Bytes
#echo frames : $totalNum
#echo fps : 30
#python3 calcu_bd.py --Bytes $totalBytes --frames $totalNum --fps 10

