#!/usr/bin/env python3

import socket
import sys
import threading
import time

from message import Message

HOST = ''
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

            neighbors.append((nip, nport, sybil))


def addneighbor(addr, sybil):
    neighbors.append((addr[0], addr[1], sybil))


def updateneighbors(addr, sybil):
    addneighbor(addr, sybil)


def listneighbors():
    nlist = []

    for neighbor in neighbors:
        nlist.append(str(neighbor[0]) + ":" + str(neighbor[1]))

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
    data = splitmsg[3::]
    data = data.split(',')

    if order == "PING":
        ping(data)
    elif order == "ALIVE":
        alive(data)
    elif order == "HELLO":
        hello(data)
    elif order == "PEERS":
        peers(data)

    addmsg(msg, addr, ttl)
    print("id: %s, ttl: %s, order: %s, data: %s" % (idmsg, time.strftime("%d %b %Y %H:%M:%S", time.localtime(ttl)), order, data))


def ping(data):
    host = data[0]
    port = int(data[0])
    ttl = 1
    msg = Message(ttl, 'ALIVE', [HOST, PORT])
    addmsg(msg, ADDR, ttl)


def alive(data):
    host = data[0]
    port = int(data[0])
    id = host + ':' + port
    neighbors[id][2] = True


def hello(data):
    host = data[0]
    port = int(data[1])
    if (host, port, False) not in neighbors:
        updateneighbors((host, port), False)
    ttl = 1
    msg = Message(ttl, 'PEERS', listneighbors())
    addmsg(msg, ADDR, ttl)


class MsgCleaner(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.running = True

    def run(self):
        while self.running is True:
            with lock:
                for msg in sent:
                    if time.time() - msg[2] > TTL:
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
            if msg and addr:
                print("Received: %s from %s" % (msg, addr))
                print("")
                with lock:
                    if validatemsg(msg.decode()):
                        processmsg(msg.decode(), addr)
                    if addr not in neighbors:
                        updateneighbors(addr)
                # msg.decode()
                # print("Received: %s from %s" % (msg, addr))
                # addmsg("msg received", addr)

            time.sleep(0.0001)

    def kill(self):
        self.running = False


class Client(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.running = True

    def run(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        while self.running is True:
            with lock:
                if buf:
                    msg, addr, ttl = buf[0]
                    if ttl - time.time() > 0:
                        if buf[0] not in sent:
                            for neighbor in neighbors:
                                if not (neighbor[0], neighbor[1]) == addr:
                                    client.sendto(msg.encode(), (neighbor[0], neighbor[1]))
                                    sent.append(buf[0])
                                    print("Sent: %s to %s" % (msg, (neighbor[0], neighbor[1])))
                    # else:
                        # print("TTL expired")
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
