python3 Eval.py --truth truth/Results/serverSideResults --ServerSideResults DDS/Results/serverSideResults --ClientSideResults DDS/Results/tracking
Results

echo -n "Bandwidth is :"
find DDS/Sendtoserver -name "*png" | xargs du -ck | tail -1
