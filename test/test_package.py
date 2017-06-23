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

import sys
import unittest

from ament_package.dependency import Dependency
from ament_package.exceptions import InvalidPackage
from ament_package.package import Package
from ament_package.person import Person
from mock import Mock

# Redirect stderr to stdout to suppress output in tests
sys.stderr = sys.stdout


class PackageTest(unittest.TestCase):

    def get_maintainer(self):
        maint = Mock()
        maint.email = 'foo@bar.com'
        maint.name = 'John Doe'
        return maint

    def test_init(self):
        maint = self.get_maintainer()
        pack = Package(name='foo',
                       version='0.0.0',
                       maintainers=[maint],
                       licenses=['BSD'])
        self.assertEqual(None, pack.filename)
        self.assertEqual([], pack.urls)
        self.assertEqual([], pack.authors)
        self.assertEqual([maint], pack.maintainers)
        self.assertEqual(['BSD'], pack.licenses)
        self.assertEqual([], pack.build_depends)
        self.assertEqual([], pack.buildtool_depends)
        self.assertEqual([], pack.test_depends)
        self.assertEqual([], pack.conflicts)
        self.assertEqual([], pack.replaces)
        self.assertEqual([], pack.exports)
        pack = Package(filename='foo',
                       name='bar',
                       version='0.0.0',
                       licenses=['BSD'],
                       maintainers=[self.get_maintainer()])
        self.assertEqual('foo', pack.filename)

        self.assertRaises(TypeError, Package, unknownattribute=42)

    def test_init_dependency(self):
        dep = Dependency('foo',
                         version_lt=1,
                         version_lte=2,
                         version_eq=3,
                         version_gte=4,
                         version_gt=5)
        self.assertEquals('foo', dep.name)
        self.assertEquals(1, dep.version_lt)
        self.assertEquals(2, dep.version_lte)
        self.assertEquals(3, dep.version_eq)
        self.assertEquals(4, dep.version_gte)
        self.assertEquals(5, dep.version_gt)
        self.assertRaises(TypeError, Dependency, 'foo', unknownattribute=42)

    def test_init_kwargs_string(self):
        pack = Package(filename='foo',
                       name='bar',
                       package_format='1',
                       version='0.0.0',
                       description='pdesc',
                       licenses=['BSD'],
                       maintainers=[self.get_maintainer()])
        self.assertEqual('foo', pack.filename)
        self.assertEqual('bar', pack.name)
        self.assertEqual('1', pack.package_format)
        self.assertEqual('0.0.0', pack.version)
        self.assertEqual('pdesc', pack.description)

    def test_init_kwargs_object(self):
        mmain = [self.get_maintainer(), self.get_maintainer()]
        mlis = ['MIT', 'BSD']
        mauth = [self.get_maintainer(), self.get_maintainer()]
        murl = [Mock(), Mock()]
        mbuilddep = [Mock(), Mock()]
        mbuildtooldep = [Mock(), Mock()]
        mtestdep = [Mock(), Mock()]
        mconf = [Mock(), Mock()]
        mrepl = [Mock(), Mock()]
        mexp = [Mock(), Mock()]
        pack = Package(name='bar',
                       version='0.0.0',
                       maintainers=mmain,
                       licenses=mlis,
                       urls=murl,
                       authors=mauth,
                       build_depends=mbuilddep,
                       buildtool_depends=mbuildtooldep,
                       test_depends=mtestdep,
                       conflicts=mconf,
                       replaces=mrepl,
                       exports=mexp)
        self.assertEqual(mmain, pack.maintainers)
        self.assertEqual(mlis, pack.licenses)
        self.assertEqual(murl, pack.urls)
        self.assertEqual(mauth, pack.authors)
        self.assertEqual(mbuilddep, pack.build_depends)
        self.assertEqual(mbuildtooldep, pack.buildtool_depends)
        self.assertEqual(mtestdep, pack.test_depends)
        self.assertEqual(mconf, pack.conflicts)
        self.assertEqual(mrepl, pack.replaces)
        self.assertEqual(mexp, pack.exports)

    def test_validate_package(self):
        maint = self.get_maintainer()
        pack = Package(filename='foo',
                       name='bar_2go',
                       package_format='1',
                       version='0.0.0',
                       description='pdesc',
                       licenses=['BSD'],
                       maintainers=[maint])
        pack.validate()
        # check invalid names
        pack.name = '2bar'
        self.assertRaises(InvalidPackage, Package.validate, pack)
        pack.name = 'bar bza'
        self.assertRaises(InvalidPackage, Package.validate, pack)
        pack.name = 'BAR'
        self.assertRaises(InvalidPackage, Package.validate, pack)
        # dashes should be acceptable in packages other than catkin or
        # ament*.
        # no build_type, so catkin is assumed per REP-140.
        pack.name = 'bar-bza'
        self.assertRaises(InvalidPackage, Package.validate, pack)
        # check explicit catkin and ament_* build_types
        build_type = Mock(tagname='build_type', attributes={}, content='catkin')
        pack.exports = [build_type]
        self.assertRaises(InvalidPackage, Package.validate, pack)
        build_type.content = 'ament_cmake'
        self.assertRaises(InvalidPackage, Package.validate, pack)
        build_type.content = 'ament_python'
        self.assertRaises(InvalidPackage, Package.validate, pack)
        # check non ament/catkin build type is valid
        build_type.content = 'cmake'
        pack.validate()
        # check authors emails
        pack.name = 'bar'
        auth1 = Mock()
        auth2 = Mock()
        auth2.validate.side_effect = InvalidPackage('foo')
        pack.authors = [auth1, auth2]
        self.assertRaises(InvalidPackage, Package.validate, pack)
        pack.authors = []
        pack.validate()
        # check maintainer required with email
        pack.maintainers = []
        self.assertRaises(InvalidPackage, Package.validate, pack)
        pack.maintainers = [maint]
        maint.email = None
        self.assertRaises(InvalidPackage, Package.validate, pack)
        maint.email = 'foo@bar.com'

        for dep_type in [
                pack.build_depends, pack.buildtool_depends,
                pack.build_export_depends, pack.buildtool_export_depends,
                pack.exec_depends, pack.test_depends, pack.doc_depends]:
            pack.validate()
            depend = Dependency(pack.name)
            dep_type.append(depend)
            self.assertRaises(InvalidPackage, Package.validate, pack)
            dep_type.remove(depend)

    def test_validate_person(self):
        auth1 = Person('foo')
        auth1.email = 'foo@bar.com'
        auth1.validate()
        auth1.email = 'foo-bar@bar.com'
        auth1.validate()
        auth1.email = 'foo+bar@bar.com'
        auth1.validate()
        auth1.email = 'foo@bar.longtopleveldomain'
        auth1.validate()

        auth1.email = 'foo[at]bar.com'
        self.assertRaises(InvalidPackage, Person.validate, auth1)
        auth1.email = 'foo bar.com'
        self.assertRaises(InvalidPackage, Person.validate, auth1)
        auth1.email = 'foo<bar.com'
        self.assertRaises(InvalidPackage, Person.validate, auth1)
