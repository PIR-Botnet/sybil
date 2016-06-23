#!/usr/bin/env python3

import json
import select
import socket
import sys
import threading
import time

from functions import *
from message import Message
from node import Node
from peer import Peer

LOG_DIR = "/home/pierre/Projects/PTIR/logs/"

TTL = 30
NODE_AMOUNT = 200
KNOWN_PEERS = [4567, 4580, 4600, 4620, 4650]

clilock = threading.RLock()
loglock = threading.RLock()

host = ''
port = 2400

nodes = []
peers = []

outputbuf = []
logs = []


class Logger(threading.Thread):

    def __init__(self, filename):
        threading.Thread.__init__(self)
        self.running = True
        self.logfile = filename
        self.logs = []

    def run(self):
        while self.running is True:
            with open(self.logfile, "a") as logfile:
                with loglock:
                    for msg in logs:
                        log = "" + time.strftime("%d %b %Y %H:%M:%S", time.localtime(time.time())) + " [" + msg[0] + "] " + msg[1]
                        logfile.write(log + "\n")
                        print(log)
                        logs.remove(msg)
            time.sleep(0.0001)

    def kill(self):
        self.running = False


class Client(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.running = True

    def run(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Retrieving some peers
        msg = Message(1, "HELLO", [host, port])
        for peer in peers:
            s.sendto(str(msg).encode(), (peer.host, peer.port))
            logs.append(("MSG" + str(port), "Sent: %s to %s:%s" % (msg, peer.host, peer.port)))

        # Main loop
        while self.running is True:
            with clilock:
                if outputbuf:
                    msg, addr, ttl = outputbuf[0]
                    for peer in peers:
                        client.sendto(str(msg).encode(), (peer.host, int(peer.port)))
                        with loglock:
                            logs.append(("MSG" + str(addr[1]), "Sent: %s to %s" % (msg, (peer.host, peer.port))))
                            # logs.append(("LEL", "BITE BITE BITE\n\n\n"))
                    outputbuf.pop(0)

            time.sleep(0.2)

    def kill(self):
        self.running = False


if __name__ == '__main__':
        # Starting logger
        logger = Logger(LOG_DIR + time.strftime("%d-%b_%H%M%S", time.localtime(time.time())))
        logger.start()
        logs.append(("INFO", "Started logging."))

        # Retrieving local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("www.google.com", 80))
        host = s.getsockname()[0]
        s.close()
        logs.append(("INFO", "Retrieved local IP."))

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Setting up sybil nodes
        for p in range(port, port + NODE_AMOUNT):
            node = Node(host, p, peers, nodes, outputbuf, logs, clilock, loglock)
            nodes.append(node)
            node.start()
            logs.append(("NODE", "Instantiated new node on port %s." % (p)))

        # Creating known peers
        for p in KNOWN_PEERS:
            peer = Peer(host, p)
            peers.append(peer)
            logs.append(("PEER", "Added new peer %s:%s" % (host, p)))

        client = Client()
        client.start()

        for node in nodes:
            msg = Message(1, "HELLO", [node.host, node.port])
            addmsg(msg, (node.host, node.port), 1, outputbuf, clilock)

        for node in nodes:
            msg = Message(1, "GET", ["http://pcksr.net/ptir.php?sybil"])
            addmsg(msg, (node.host, node.port), 1, outputbuf, clilock)
