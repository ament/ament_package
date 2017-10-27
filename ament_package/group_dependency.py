# Copyright 2017 Open Source Robotics Foundation, Inc.
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


class GroupDependency:
    __slots__ = [
        'name',
        'members',
    ]

    def __init__(self, name, members=None):
        self.name = name
        self.members = members

    def __eq__(self, other):
        if not isinstance(other, GroupDependency):
            return False
        return all(getattr(self, attr) == getattr(other, attr)
                   for attr in self.__slots__)

    def __str__(self):
        return self.name

    def extract_group_members(self, packages):
        self.members = set()
        for pkg in packages:
            if self.name in pkg.member_of_groups:
                self.members.add(pkg.name)
