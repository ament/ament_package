# Copyright 2014 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re

from .exceptions import InvalidPackage


class Person(object):
    __slots__ = ['name', 'email']

    def __init__(self, name, *, email=None):
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
        email_pattern = '^[a-zA-Z0-9._%\+-]+@[a-zA-Z0-9._%-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, self.email):
            raise InvalidPackage("Invalid email '%s' for person '%s'" %
                                 (self.email, self.name))
