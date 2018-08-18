set terminal svg
set output 'resnet-101-2.svg'
set xlabel 'inference speed'
set ylabel 'accuracy'
set xrange [0:600]
set yrange [0:1]
set xtics 25
set ytics 0.1
plot 'resnet-101' using 6:1 with lines lc rgb 'dark-green' lt 0  title 'resnet-101', \
'resnet-101-2' using 6:1 with lines lc rgb 'red' lt 1 title 'resnet-101-2', \
0.82 title 'lowes accuracy' linetype 0, \
'3-speed' using 1:2 with lines linetype 0 title '3xspeed'
set output

