#!/bin/bash

for i in {1..100} ; do
    sleep 1
    cp ../visu-p2p/data.json "data/data$i.json"
done
