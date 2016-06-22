#!/usr/bin/env python3

import json
import sys

no_files = sys.argv[1]
count = [0]*int(no_files)

def extract(i):
    nodes = []
    edges = []
    datafile = "data/data{i}.json".format(i=i)
    with open(datafile) as jsondata:
        data = json.loads(jsondata.read())

    for node in data['nodes']:
        nodes.append([node['label'], 0])

    for edge in data['edges']:
        src, dst = edge['id'].split(':')
        edges.append((src, dst))

    for node in nodes:
        for edge in edges:
            if node[0] == int(edge[0]) or node[0] == int(edge[1]):
                node[1] += 1

    for node in nodes:
        if node[1] > 0:
            count[i] += 1

    print("Number of connected nodes : ", count[i])

for i in range(1,int(no_files)):
    extract(i)

print(count)
