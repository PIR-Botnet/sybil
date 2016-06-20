from peer import Peer


def addpeer(addr, peers, lock):
    peer = Peer(addr[0], addr[1])
    with lock:
        peers.append(peer)


def updatepeers(addr, peers, lock):
    log = ""
    exist = False

    if 2400 <= int(addr[1]) <= 2600:
        exist = True

    for peer in peers:
        if addr[0] == peer.host and addr[1] == peer.port:
            exist = True

    if not exist:
        addpeer(addr, peers, lock)
        log = "Added peer %s:%s" % (addr[0], addr[1])

    return log


def listpeers(peers):
    plist = []

    for peer in peers:
        plist.append(str(peer))

    return plist


def addmsg(msg, addr, ttl, buf, lock):
    with lock:
        buf.append((msg, addr, ttl))
