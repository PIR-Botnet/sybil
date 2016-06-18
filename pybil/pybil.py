#!/usr/bin/env python3

import socket
import sys
import threading
import time

from message import Message
from peer import Peer

HOST = 'localhost'
port = int(sys.argv[1])
ADDR = (HOST, port)
TIMEOUT = 1000
BUFSIZE = 1024
TTL = 30

buf = []
sent = []
neighborfile = sys.argv[2]
neighbors = []

lock = threading.RLock()


def loadneighbors(filename):
    with open(filename) as f:
        data = f.read(4096)

    data = data.replace("\n", "").split(';')

    for neighbor in data:
        if neighbor:
            neighbor = neighbor.split(',')
            nip = neighbor[0]
            nport = int(neighbor[1])

            if int(neighbor[2]) == 1:
                sybil = True
            else:
                sybil = False

            addneighbor((nip, nport), sybil)


def addneighbor(addr, sybil):
    newneighb = Peer(addr[0], addr[1], sybil)
    neighbors.append(newneighb)


def updateneighbors(addr, sybil):
    for neighbor in neighbors:
        if addr[0] == neighbor.host and addr[1] == neighbor.port:
            addneighbor(addr, sybil)
            print("Added neighbor %s:%s" % (addr[0], addr[1]))


def listneighbors():
    nlist = []

    for neighbor in neighbors:
        nlist.append(str(neighbor))

    return nlist


def addmsg(msg, addr, ttl):
    buf.append((msg, addr, ttl))


def delmsg():
    buf.pop(0)


def validatemsg(msg):
    valid = True
    msg = msg.split(";")

    if len(msg) < 2:
        valid = False
    else:
        if not msg[0].isnumeric and not len(msg[0]) == 5:
            valid = False
        if not msg[1].isnumeric:
            valid = False

    return valid


def processmsg(msg, addr):
    splitmsg = msg.split(';')
    idmsg = splitmsg[0]
    ttl = float(splitmsg[1])
    order = splitmsg[2]
    data = splitmsg[3]
    data = data.split(',')

    if order == "PING":
        ping(data)
    elif order == "ALIVE":
        alive(data)
    elif order == "HELLO":
        hello(data)
    elif order == "PEERS":
        peers(data)

    if ttl < 1:
        addmsg(msg, addr, ttl)

    print("Received id: %s, ttl: %s, order: %s" % (idmsg, ttl, order))


def ping(data):
    host = data[0]
    port = int(data[1])
    ttl = 1
    msg = Message(ttl, 'ALIVE', [HOST, port])
    addmsg(msg, ADDR, ttl)
    print("-> Processed PING.")


def alive(data):
    host = data[0]
    port = int(data[1])
    bid = str(host) + ':' + str(port)
    for neighbor in neighbors:
        if neighbor.host == host and neighbor.port == port:
            neighbor.alive = True
    print("-> Processed ALIVE.")


def hello(data):
    host = data[0]
    port = int(data[1])
    updateneighbors((host, port), False)
    ttl = 1
    msg = Message(ttl, 'PEERS', listneighbors())
    addmsg(msg, ADDR, ttl)
    print("-> Processed HELLO.")


def peers(data):
    for peer in data:
        host, port = peer.split(':')
        updateneighbors((host, port), False)
    print("-> Processed PEERS.")


class MsgCleaner(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.running = True

    def run(self):
        while self.running is True:
            with lock:
                for msg in sent:
                    if msg[2] > 0:
                        sent.remove(msg)

            time.sleep(0.0001)

    def kill(self):
        self.running = False


class Server(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.running = True

    def run(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server.bind(ADDR)

        while self.running is True:
            msg, addr = server.recvfrom(BUFSIZE)
            print(msg)
            if msg and addr:
                with lock:
                    if validatemsg(msg.decode()):
                        processmsg(msg.decode(), addr)

            time.sleep(0.0001)

    def kill(self):
        self.running = False


class Client(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.running = True

    def run(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        msg = Message(1, "HELLO", [HOST, port])
        for neighbor in neighbors:
            if neighbor.sybil is False:
                client.sendto(str(msg).encode(), (neighbor.host, neighbor.port))

        while self.running is True:
            with lock:
                if buf:
                    msg, addr, ttl = buf[0]
                    if buf[0] not in sent:
                        for neighbor in neighbors:
                            if not (neighbor.host, neighbor.port) == addr:
                                client.sendto(str(msg).encode(), (neighbor.host, int(neighbor.port)))
                                sent.append(buf[0])
                                print("Sent: %s to %s" % (msg, (neighbor.host, neighbor.port)))
                    delmsg()

            time.sleep(0.0001)


if __name__ == "__main__":
    loadneighbors(neighborfile)
    msgcleaner = MsgCleaner()
    server = Server()
    client = Client()
    msgcleaner.start()
    server.start()
    client.start()
