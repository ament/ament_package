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

from ament_package.generate_setuptools_dict import generate_setuptools_dict
import pytest

AMENT_PACKAGE_FOLDER = str(pathlib.Path(__file__).parent.parent.resolve())


def common_info_check(result):
    assert result.get('name') == 'ament_package'
    assert result.get('author') == 'Dirk Thomas'
    assert result.get('author_email') == 'dthomas@osrfoundation.org'
    assert result.get('maintainer') == 'Mabel Zhang mabel@openrobotics.org, ' + \
                                       'Audrow Nash audrow@openrobotics.org'
    assert result.get('maintainer_email') is None
    assert result.get('description') == \
        'The parser for the manifest files in the ament buildsystem.'
    assert result.get('license') == 'Apache License 2.0'

    # Instead of checking the exact value, just make sure it has two periods in it
    # so that we don't have to change the test everytime a new version is released
    version = result.get('version', '')
    assert len(version.split('.')) == 3


def test_basic_info():
    common_info_check(generate_setuptools_dict(AMENT_PACKAGE_FOLDER))


def test_additional_fields():
    url_value = 'https://github.com/ament/ament_package/wiki'
    result = generate_setuptools_dict(AMENT_PACKAGE_FOLDER,
                                      zip_safe=True,
                                      url=url_value)
    common_info_check(result)
    assert result.get('zip_safe') is True
    assert result.get('url') == url_value


def test_conflicting_info():
    # We should not be able to override an existing value
    with pytest.raises(RuntimeError):
        generate_setuptools_dict(AMENT_PACKAGE_FOLDER,
                                 license='conflicting license')
