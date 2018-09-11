#echo MPEG :

python3 Eval.py --logic MPEG --truth GroundTruth/Results/serverSideResults --ServerSideResults MPEG/Results/serverSideResults

totalB=`find MPEG/Sendtoserver -name "*jpeg" | xargs du -cb | tail -1`
totalNum=`ls MPEG/Sendtoserver | wc -l`
totalBytes=` echo ${totalB%to*}`
#echo total : $totalBytes Bytes
#echo frames : $totalNum
#echo fps : 30
python3 calcu_bd.py --Bytes $totalBytes --frames $totalNum --fps 30


