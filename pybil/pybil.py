#!/usr/bin/env python3

import socket
import sys
import threading
import time

HOST = ''
port = int(sys.argv[1])
ADDR = (HOST, port)
TIMEOUT = 1000
BUFSIZE = 1024

buf = []
neighborfile = sys.argv[2]
neighbors = []


def loadneighbors(filename):
    with open(filename) as f:
        data = f.read(4096)

    data = data.replace("\n", "")
    dsplit = data.split(';')

    for neighbor in dsplit:
        if neighbor:
            nsplit = neighbor.split(',')
            nip = nsplit[0]
            nport = int(nsplit[1])
            neighbors.append((nip, nport))


def addneighbor(addr):
    neighbors.append(addr)


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

    addmsg(msg, addr, ttl)
    print("id: %s, ttl: %s, order: %s, data: %s" % (idmsg, time.strftime("%d %b %Y %H:%M:%S", time.localtime(ttl)), order, data))


class Server(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.running = True

    def run(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server.bind(ADDR)

        while self.running is True:
            msg, addr = server.recvfrom(BUFSIZE)
            if validatemsg(msg.decode()):
                processmsg(msg.decode(), addr)
            if addr not in neighbors:
                addneighbor(addr)
            # msg.decode()
            # print("Received: %s from %s" % (msg, addr))
            # addmsg("msg received", addr)

    def kill(self):
        self.running = False


class Client(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.running = True

    def run(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        while self.running is True:
            if buf:
                msg, addr, ttl = buf[0]
                if ttl - time.time() > 0:
                    for neighbor in neighbors:
                        if not (neighbor[0], neighbor[1]) == addr:
                            client.sendto(msg.encode(), (neighbor[0], neighbor[1]))
                            print("Sent: %s to %s" % (msg, (neighbor[0], neighbor[1])))
                # else:
                    # print("TTL expired")
                delmsg()


if __name__ == "__main__":
    loadneighbors(neighborfile)
    server = Server()
    client = Client()
    server.start()
    client.start()
