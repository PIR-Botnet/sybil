import uuid

class Message:
    def __init__(self, ttl, order, data=None, msg_id=None):
        self.id = msg_id or str(uuid.uuid4())
        self.ttl = ttl
        self.order = order.upper()
        self.data = data

    def __str__(self):
        m = '{id};{ttl};{order};'.format(id=self.id, ttl=self.ttl, order=self.order)

        for i, d in enumerate(self.data):
            if i > 0:
                m += ','
            m += str(d)

        return m

    
