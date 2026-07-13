# Copyright 2026 Open Source Robotics Foundation, Inc.
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

from pathlib import Path
from types import ModuleType

import pytest


def test_configure_string_substitutes_known_variable(templates: ModuleType) -> None:
    assert templates.configure_string('a=@FOO@', {'FOO': 'x'}) == 'a=x'


def test_configure_string_unknown_variable_becomes_empty(templates: ModuleType) -> None:
    assert templates.configure_string(
        'a=@FOO@;b=@BAR@', {'FOO': 'x'}) == 'a=x;b='


def test_configure_string_without_placeholder_is_passthrough(templates: ModuleType) -> None:
    assert templates.configure_string('no vars here', {}) == 'no vars here'


def test_configure_string_repeated_placeholder(templates: ModuleType) -> None:
    assert templates.configure_string('@A@-@B@-@A@', {'A': '1', 'B': '2'}) \
        == '1-2-1'


def test_configure_file_round_trip(templates: ModuleType, tmp_path: Path) -> None:
    template = tmp_path / 'template.in'
    template.write_text('prefix=@P@\n', encoding='utf-8')
    assert templates.configure_file(str(template), {'P': '/opt'}) \
        == 'prefix=/opt\n'


def test_get_package_level_template_names_all_platforms(templates: ModuleType) -> None:
    assert templates.get_package_level_template_names(all_platforms=True) == [
        'local_setup.bash.in',
        'local_setup.bat.in',
        'local_setup.fish.in',
        'local_setup.sh.in',
        'local_setup.zsh.in',
    ]


def test_get_prefix_level_template_names_all_platforms(templates: ModuleType) -> None:
    assert templates.get_prefix_level_template_names(all_platforms=True) == [
        'local_setup.bash',
        'local_setup.bat.in',
        'local_setup.sh.in',
        'local_setup.zsh',
        'setup.bash',
        'setup.bat.in',
        'setup.sh.in',
        'setup.zsh',
        'local_setup.fish.in',
        'setup.fish',
        '_local_setup_util.py',
    ]


def test_platform_filtering_excludes_bat_on_posix(templates: ModuleType) -> None:
    if templates.IS_WINDOWS:
        pytest.skip('POSIX-only behavior')
    names = templates.get_package_level_template_names(all_platforms=False)
    assert 'local_setup.bat.in' not in names
    assert 'local_setup.sh.in' in names
