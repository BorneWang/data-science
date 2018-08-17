set terminal svg
set output 'resnet-18-34-50-101.svg'
set xlabel 'inference speed'
set ylabel 'accuracy'
set xrange [0:500]
set yrange [0:1]
set xtics 25
set ytics 0.25
plot 'resnet-34' using 6:1 with lines lc rgb "red" lt 0 title "{/Times=10 resnet-34}", \
'resnet-18' using 6:1 with lines lc rgb "dark-green" lt 0 title "{/Times=10 resnet-18}", \
'resnet-50' using 6:1 with lines lc rgb "black" lt 0 title "{/Times=10 resnet-50}", \
'resnet-101' using 6:1 with lines lc rgb "blue" lt 0 title "{/Times=10 resnet-101}", \
'resnet-18-2' using 6:1 with lines lc rgb 'dark-green' lt 1 title "{/Times=10 resnet-18-2}", \
0.82 title "{/Times=10 low accuracy}" linetype 0, \
'3-speed' using 1:2 with lines linetype 0 title "{/Times=10 3xspeed}"
set output

