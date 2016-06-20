import datetime


class Peer:

    def __init__(self, host, port):
        self.host = host
        self.port = int(port)
        self.alive = True
        self.added = datetime.datetime.now()
        self.id = "{host}:{port}".format(host=self.host, port=self.port)

    def __str__(self):
        return self.id
