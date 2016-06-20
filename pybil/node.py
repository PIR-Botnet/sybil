import socket
import threading
import time

from functions import *
from message import Message

BUFSIZE = 1024


class Node(threading.Thread):

    def __init__(self, host, port, peers, nodes, buf, logs, lock, loglock):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind((host, port))
        self.buf = []
        self.peerlist = peers
        self.nodes = nodes
        self.outputbuf = buf
        self.logs = logs
        self.lock = lock
        self.loglock = loglock
        self.running = True

    def __str__(self):
        return "{host}:{port}".format(host=self.host, port=self.port)

    def run(self):
        while self.running is True:
            msg, addr = self.s.recvfrom(BUFSIZE)

            if msg:
                with self.loglock:
                    self.logs.append((str(self.port), "Received: %s from %s:%s" % (msg, addr[0], addr[1])))
                self.processmsg(msg)

            time.sleep(0.2)

    def processmsg(self, msg):
        splitmsg = msg.decode().split(';')
        idmsg = splitmsg[0]
        ttl = int(splitmsg[1])
        order = splitmsg[2]
        data = splitmsg[3].split(',')

        if order == "PING":
            self.ping(data)
        elif order == "ALIVE":
            self.alive(data)
        elif order == "HELLO":
            self.hello(data)
        elif order == "PEERS":
            self.peers(data)
        elif order == "GET":
            self.get()

    def ping(self, data):
        host = data[0]
        port = int(data[1])
        ttl = 1
        msg = Message(ttl, 'ALIVE', [self.host, self.port])
        with self.lock:
            addmsg(msg, (self.host, self.port), ttl, self.outputbuf, self.lock)
        with self.loglock:
            self.logs.append(("CMD", "Processed PING."))

    def alive(self, data):
        host = data[0]
        port = int(data[1])
        bid = str(host) + ':' + str(port)
        for peer in self.peerlist:
            if peer.host == host and peer.port == port:
                peer.alive = True

        with self.loglock:
            self.logs.append(("CMD", "Processed ALIVE."))

    def hello(self, data):
        host = data[0]
        port = int(data[1])
        log = updatepeers((host, port), self.peerlist, self.lock)

        if log:
            with self.loglock:
                self.logs.append(("INFO", log))

        ttl = 1
        msg = Message(ttl, 'PEERS', listpeers(self.nodes))
        addmsg(msg, (self.host, self.port), ttl, self.outputbuf, self.lock)
        with self.loglock:
            self.logs.append(("CMD", "Processed HELLO."))

    def peers(self, data):
        for peer in data:
            host, port = peer.split(':')
            updatepeers((host, port), self.peerlist, self.lock)
        with self.loglock:
            self.logs.append(("CMD", "Processed PEERS."))

    def get(self):
        ttl = -10
        msg = Message(ttl, "GET", "http://pcksr.net/ptir.php?sybil")
        addmsg(msg, (self.host, self.port), ttl, self.outputbuf, self.lock)
        with self.loglock:
            self.logs.append(("CMD", "Processed GET."))
