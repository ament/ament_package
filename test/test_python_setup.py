# Copyright 2021 PickNik Robotics
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

import pathlib
import unittest

from ament_package.python_setup import generate_setuptools_dict

AMENT_PACKAGE_FOLDER = str(pathlib.Path(__file__).parent.parent.resolve())


class TestBasicInfo(unittest.TestCase):
    def test_basic_info(self):
        result = generate_setuptools_dict(AMENT_PACKAGE_FOLDER)
        self.assertEqual('ament_package', result.get('name'))
        self.assertEqual('Dirk Thomas', result.get('author'))
        self.assertEqual('dthomas@osrfoundation.org', result.get('author_email'))
        self.assertEqual('Mabel Zhang mabel@openrobotics.org, Audrow Nash audrow@openrobotics.org',
                         result.get('maintainer'))
        self.assertEqual(None, result.get('maintainer_email'))
        self.assertEqual('The parser for the manifest files in the ament buildsystem.',
                         result.get('description'))
        self.assertEqual('Apache License 2.0', result.get('license'))

        # Instead of checking the exact value, just make sure it has two periods in it
        # so that we don't have to change the test everytime a new version is released
        version = result.get('version', '')
        self.assertEqual(3, len(version.split('.')))


class TestAdditionalFields(unittest.TestCase):
    def test_additional_fields(self):
        result = generate_setuptools_dict(AMENT_PACKAGE_FOLDER,
                                          zip_safe=True,
                                          url='https://github.com/ament/ament_package/wiki')
        self.assertEqual('ament_package', result.get('name'))
        self.assertEqual('Dirk Thomas', result.get('author'))
        self.assertEqual('dthomas@osrfoundation.org', result.get('author_email'))
        self.assertEqual('Mabel Zhang mabel@openrobotics.org, Audrow Nash audrow@openrobotics.org',
                         result.get('maintainer'))
        self.assertEqual(None, result.get('maintainer_email'))
        self.assertEqual('The parser for the manifest files in the ament buildsystem.',
                         result.get('description'))
        self.assertEqual('Apache License 2.0', result.get('license'))
        self.assertEqual(True, result.get('zip_safe'))
        self.assertEqual('https://github.com/ament/ament_package/wiki', result.get('url'))

        # Instead of checking the exact value, just make sure it has two periods in it
        # so that we don't have to change the test everytime a new version is released
        version = result.get('version', '')
        self.assertEqual(3, len(version.split('.')))


class TestConflictingInfo(unittest.TestCase):
    def test_conflicting_info(self):
        with self.assertRaises(RuntimeError):
            generate_setuptools_dict(AMENT_PACKAGE_FOLDER,
                                     license='2 ill')


if __name__ == '__main__':
    unittest.main()
