import uuid


class Message:
    def __init__(self, ttl, order, data=None, msg_id=None):
        self.id = msg_id or str(uuid.uuid4())
        self.ttl = ttl
        self.order = order.upper()
        self.data = data

    def __str__(self):
        m = '{id};{ttl};{order};'.format(id=self.id, ttl=self.ttl, order=self.order)

        if len(self.data) > 1:
            for i, d in enumerate(self.data):
                if i > 0:
                    m += ','
                m += str(d)
        else:
            m += self.data[0]

        return m

    @classmethod
    def fromstring(cls, strrep):
        c = strrep.count(';')
        data = None
        if count == 2:
            uid, ttl, order = strrep.split(';')
        elif count == 3:
            uid, ttl, order, data = strrep.split(';')
        else:
            uid = 0
            ttl = 0
            order = ''

        ttl = int(ttl)

        if data is not None:
            data = data.split(',')

        return cls(ttl, order.upper(), data, msg_id=uid)

    def isvalid(self):
        return self.order is not None and self.order != ''

    def is_expired(self):
        return self.ttl > 0
