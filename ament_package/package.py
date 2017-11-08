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

from copy import deepcopy
import re

from .exceptions import InvalidPackage


class Package:
    """Object representation of a package manifest file."""

    __slots__ = [
        'package_format',
        'name',
        'version',
        'version_compatibility',
        'description',
        'maintainers',
        'licenses',
        'urls',
        'authors',
        'build_depends',
        'buildtool_depends',
        'build_export_depends',
        'buildtool_export_depends',
        'exec_depends',
        'test_depends',
        'doc_depends',
        'conflicts',
        'replaces',
        'group_depends',
        'member_of_groups',
        'exports',
        'filename',
    ]

    def __init__(self, *, filename=None, **kwargs):
        """
        Constructor.

        :param filename: location of package.xml.  Necessary if
          converting ``${prefix}`` in ``<export>`` values, ``str``.
        """
        # initialize all slots ending with "s" with lists
        # all other with plain values
        for attr in self.__slots__:
            if attr.endswith('s'):
                value = list(kwargs[attr]) if attr in kwargs else []
                setattr(self, attr, value)
            else:
                value = kwargs[attr] if attr in kwargs else None
                setattr(self, attr, value)
        if 'depends' in kwargs:
            for d in kwargs['depends']:
                for slot in [self.build_depends,
                             self.build_export_depends,
                             self.exec_depends]:
                    if d not in slot:
                        slot.append(deepcopy(d))
            del kwargs['depends']
        self.filename = filename
        # verify that no unknown keywords are passed
        unknown = set(kwargs.keys()).difference(self.__slots__)
        if unknown:
            raise TypeError('Unknown properties: %s' % ', '.join(unknown))

    def __iter__(self):
        for slot in self.__slots__:
            yield slot

    def __str__(self):
        data = {}
        for attr in self.__slots__:
            data[attr] = getattr(self, attr)
        return str(data)

    def get_build_type(self):
        """
        Return value of export/build_type element, or 'catkin' if unspecified.

        :returns: package build type
        :rtype: str
        :raises: :exc:`InvalidPackage`
        """
        build_type_exports = [ex.content for ex in self.exports if ex.tagname == 'build_type']
        if not build_type_exports:
            return 'catkin'
        if len(build_type_exports) == 1:
            return build_type_exports[0]
        raise InvalidPackage('Only one <build_type> element is permitted.')

    def evaluate_conditions(self, context):
        """
        Evaluate the conditions of all dependencies and memberships.

        :param context: A dictionary with key value pairs to replace variables
          starting with $ in the condition.

        :raises: :exc:`ValueError` if any condition fails to parse
        """
        for attr in (
            'build_depends',
            'buildtool_depends',
            'build_export_depends',
            'buildtool_export_depends',
            'exec_depends',
            'test_depends',
            'doc_depends',
            'conflicts',
            'replaces',
            'group_depends',
            'member_of_groups',
        ):
            conditionals = getattr(self, attr)
            for conditional in conditionals:
                conditional.evaluate_condition(context)

    def validate(self):
        """
        Ensure that all standards for packages are met.

        :raises InvalidPackage: in case validation fails
        """
        errors = []
        if self.package_format:
            if not re.match('^[1-9][0-9]*$', str(self.package_format)):
                errors.append("The 'format' attribute of the package must "
                              'contain a positive integer if present')

        if not self.name:
            errors.append('Package name must not be empty')
        # Must start with a lower case alphabetic character.
        # Allow lower case alphanummeric characters and underscores in
        # catkin or ament packages.
        valid_package_name_regexp = '^[a-z][a-z0-9_]*$'
        build_type = self.get_build_type()
        if build_type != 'catkin' and not build_type.startswith('ament'):
            # Dashes are allowed for other build_types.
            valid_package_name_regexp = '^[a-z][a-z0-9_-]*$'
        if not re.match(valid_package_name_regexp, self.name):
            errors.append("Package name '%s' does not follow naming "
                          'conventions' % self.name)

        version_regexp = '^[0-9]+\.[0-9_]+\.[0-9_]+$'
        if not self.version:
            errors.append('Package version must not be empty')
        elif not re.match(version_regexp, self.version):
            errors.append("Package version '%s' does not follow version "
                          'conventions' % self.version)
        if self.version_compatibility:
            if not re.match(version_regexp, self.version_compatibility):
                errors.append(
                    "Package compatibility version '%s' does not follow "
                    'version conventions' % self.version_compatibility)

        if not self.description:
            errors.append('Package description must not be empty')

        if not self.maintainers:
            errors.append('Package must declare at least one maintainer')
        for maintainer in self.maintainers:
            try:
                maintainer.validate()
            except InvalidPackage as e:
                errors.append(str(e))
            if not maintainer.email:
                errors.append('Maintainers must have an email address')

        if not self.licenses:
            errors.append('The package node must contain at least one '
                          "'license' tag")

        if self.authors is not None:
            for author in self.authors:
                try:
                    author.validate()
                except InvalidPackage as e:
                    errors.append(str(e))

        dep_types = {
            'build': self.build_depends,
            'buildtool': self.buildtool_depends,
            'build_export': self.build_export_depends,
            'buildtool_export': self.buildtool_export_depends,
            'exec': self.exec_depends,
            'test': self.test_depends,
            'doc': self.doc_depends,
        }
        for dep_type, depends in dep_types.items():
            for depend in depends:
                if depend.name == self.name:
                    errors.append(
                        "The package must not '%s_depend' on a package with "
                        'the same name as this package' % dep_type)

        if (
            {d.name for d in self.group_depends} &
            {g.name for g in self.member_of_groups}
        ):
            errors.append(
                "The package must not 'group_depend' on a package which it "
                'also declares to be a member of')

        if errors:
            raise InvalidPackage('\n'.join(errors))
