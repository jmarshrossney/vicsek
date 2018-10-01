#!/bin/bash

trap "echo ' Aborting...'; exit;" SIGINT

# Number of processors
Np=$(grep "Np = " params.py | awk '{print $3}')
pmax=$(expr $Np - 1)
plist=$(seq 0 $pmax)

# Get save file name and remove double quotes
save_name=$(grep "save_name = " params.py | awk '{print $3}')
save_name="${save_name%\"}"
save_name="${save_name#\"}"

# Run simulations
echo "-----> main.py"; parallel python main.py ::: $plist || exit 1

# Combine output files into one
for p in $plist
do
    this_file=${save_name}_p$p.out
    WC=($(wc -l $this_file))
    lines=${WC[0]}
    echo "Adding $lines lines from $this_file to $save_name.out"
    
    cat ${save_name}_p$p.out >> $save_name.out

done


