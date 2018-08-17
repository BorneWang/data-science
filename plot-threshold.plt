set terminal svg
set output 'resnet-18-2.svg'
set xlabel 'inference speed'
set ylabel 'accuracy'
set xrange [0:500]
set yrange [0:1]
set xtics 25
set ytics 0.25
plot 'resnet-18-2' using 6:1 with lines lc rgb 'red' lt 0 lw 2 title 'resnet-18', 0.82 title 'lowes accuracy' linetype 0, '3-speed' using 1:2 with lines linetype 0 title '3xspeed'
set output

