class Export(object):
    __slots__ = ['tagname', 'attributes', 'content']

    def __init__(self, tagname, attributes=None, content=None):
        self.tagname = tagname
        self.attributes = dict(attributes) if attributes else {}
        self.content = content

    def __str__(self):
        txt = '<%s' % self.tagname
        for key in sorted(self.attributes.keys()):
            txt += ' %s="%s"' % (key, self.attributes[key])
        if self.content:
            txt += '>%s</%s>' % (self.content, self.tagname)
        else:
            txt += '/>'
        return txt
