set terminal svg
set output 'resnet.svg'
set xlabel 'inference speed'
set ylabel 'accuracy'
set xrange [0:600]
set yrange [0:1]
set xtics 25
set ytics 0.1
plot 'diff-resnet' using 1:2 with lines lc rgb 'red' lt 1  title 'resnet', \
'diff-resnet' using 1:2 with points pt 7 title 'resnet-point', \
0.82 title 'lowes accuracy' linetype 0, \
'3-speed' using 1:2 with lines linetype 0 title '3xspeed'
set output

