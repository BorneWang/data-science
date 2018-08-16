set terminal svg
set output 'resnet-50.svg'
set xlabel 'inference speed'
set ylabel 'accuracy'
set xrange [0:400]
set yrange [0:1]
set xtics 25
set ytics 0.25
set label 1 "(69.522,0.840)" at 69.522,0.840
plot 'resnet-50' using 6:1 with lines linetype 2 title 'resnet-50',  0.82 title '0.82' linetype 0, '3-speed' using 1:2 with lines linetype 0 title '3xspeed'
set output

