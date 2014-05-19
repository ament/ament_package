class Dependency(object):
    __slots__ = [
        'name',
        'version_lt',
        'version_lte',
        'version_eq',
        'version_gte',
        'version_gt'
    ]

    def __init__(self, name, **kwargs):
        for attr in self.__slots__:
            value = kwargs[attr] if attr in kwargs else None
            setattr(self, attr, value)
        self.name = name
        # verify that no unknown keywords are passed
        unknown = set(kwargs.keys()).difference(self.__slots__)
        if unknown:
            raise TypeError('Unknown properties: %s' % ', '.join(unknown))

    def __eq__(self, other):
        if not isinstance(other, Dependency):
            return False
        return all([getattr(self, attr) == getattr(other, attr)
                    for attr in self.__slots__])

    def __str__(self):
        return self.name
