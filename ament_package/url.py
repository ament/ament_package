class Url(object):
    __slots__ = ['url', 'type']

    def __init__(self, url, type_=None):
        self.url = url
        self.type = type_

    def __str__(self):
        return self.url
