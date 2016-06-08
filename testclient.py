#!/usr/bin/env python3

import socket
import sys
import threading
import time

HOST = ''
PORT = 2400
ADDR = (HOST, PORT)
TIMEOUT = 1000
BUFSIZE = 1024

buf = []


def addmsg(msg, addr, ttl):
    buf.append((msg, addr, ttl))


def delmsg():
    buf.pop(0)


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
                    client.sendto(msg.encode(), addr)
                    print("Sent: %s to %s" % (msg, addr))
                # else:
                    # print("TTL expired")
                delmsg()


class Text_Input(threading.Thread):

        def __init__(self):
            threading.Thread.__init__(self)
            self.running = True

        def run(self):
            while self.running is True:
                msgid = input("ID: ")
                order = input("Order: ")
                data = input("Data: ")
                port = int(input("Port: "))
                ttl = (time.time() + 10)

                msg = "" + msgid + ";" + str(ttl) + ";" + order + ";" + data

                addmsg(msg, ("localhost", port), ttl)
                time.sleep(0)

        def kill(self):
            self.running = False

if __name__ == "__main__":
    textinput = Text_Input()
    textinput.start()
    client = Client()
    client.start()
