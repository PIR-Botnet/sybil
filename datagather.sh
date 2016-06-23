#!/bin/bash

gnome-terminal --geometry=70x18 -e "bash -c \"python3 /home/pierre/Projects/p2p/src/main.py\""

for i in {1..5} ; do
    sleep 0.5
    cp ../visu-p2p/data.json "data/data$i.json"
done

gnome-terminal --geometry=70x18+770+50 -e "bash -c \"python3 /home/pierre/Projects/PTIR/pybil/pybil.py\""

for i in {6..60} ; do
    sleep 0.5
    cp ../visu-p2p/data.json "data/data$i.json"
done

python3 dataextraction.py 60

mv data datanew
mv out.csv datanew/
mkdir data
