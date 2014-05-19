from .exceptions import InvalidPackage
import re


class Person(object):
    __slots__ = ['name', 'email']

    def __init__(self, name, email=None):
        self.name = name
        self.email = email

    def __str__(self):
        name = self.name
        if not isinstance(name, str):
            name = name.encode('utf-8')
        if self.email is not None:
            return '%s <%s>' % (name, self.email)
        else:
            return '%s' % name

    def validate(self):
        if self.email is None:
            return
        email_pattern = '^[a-zA-Z0-9._%\+-]+@[a-zA-Z0-9._%-]+\.[a-zA-Z]{2,6}$'
        if not re.match(email_pattern, self.email):
            raise InvalidPackage("Invalid email '%s' for person '%s'" %
                                 (self.email, self.name))
