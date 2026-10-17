# Copyright 2026 Wesley
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

import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest


_PREFIX_TEMPLATES = Path(__file__).resolve().parents[1] / \
    'ament_package/template/prefix_level'
_PACKAGE_TEMPLATES = Path(__file__).resolve().parents[1] / \
    'ament_package/template/package_level'


@pytest.mark.parametrize(('shell', 'script'), [
    ('bash', 'setup.bash'),
    ('sh', 'setup.sh'),
])
def test_setup_with_nounset_and_unset_path(
    tmp_path: Path, shell: str, script: str,
) -> None:
    """Sourcing a prefix must tolerate absent optional and generated variables."""
    index = tmp_path / 'share/ament_index/resource_index/packages'
    index.mkdir(parents=True)
    (index / 'foo').write_text('', encoding='utf-8')
    package = tmp_path / 'share/foo'
    package.mkdir()
    (package / 'package.dsv').write_text(
        'set;FOO_VAR;ok\n'
        'prepend-non-duplicate;MY_PATH;share/foo\n', encoding='utf-8')

    for name in ('setup.bash', 'local_setup.bash', '_local_setup_util.py'):
        shutil.copyfile(_PREFIX_TEMPLATES / name, tmp_path / name)
    for source, destination in (
        ('setup.sh.in', 'setup.sh'),
        ('local_setup.sh.in', 'local_setup.sh'),
    ):
        content = (_PREFIX_TEMPLATES / source).read_text(encoding='utf-8')
        content = content.replace('@CMAKE_INSTALL_PREFIX@', str(tmp_path))
        content = content.replace('@ament_package_PYTHON_EXECUTABLE@', sys.executable)
        content = content.replace('@SKIP_PARENT_PREFIX_PATH@', '')
        (tmp_path / destination).write_text(content, encoding='utf-8')

    env = {
        key: value for key, value in os.environ.items()
        if not key.startswith('AMENT_') and key not in ('FOO_VAR', 'MY_PATH')
    }
    result = subprocess.run(
        [shell, '-euc',
         f'. "{tmp_path}/{script}"; '
         'printf "%s\\n%s\\n" "$FOO_VAR" "$MY_PATH"'],
        capture_output=True, text=True, env=env)
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == ['ok', str(package)]


@pytest.mark.parametrize(('shell', 'script'), [
    ('bash', 'local_setup.bash'),
    ('sh', 'local_setup.sh'),
])
def test_package_local_setup_with_nounset(
    tmp_path: Path, shell: str, script: str,
) -> None:
    """Package hooks can extend an initially unset list under nounset."""
    package = tmp_path / 'share/foo'
    package.mkdir(parents=True)
    (package / 'hook.sh').write_text(
        'ament_prepend_unique_value MY_PATH "$AMENT_CURRENT_PREFIX/share/foo"\n',
        encoding='utf-8')
    for source, destination in (
        ('local_setup.bash.in', 'local_setup.bash'),
        ('local_setup.sh.in', 'local_setup.sh'),
    ):
        content = (_PACKAGE_TEMPLATES / source).read_text(encoding='utf-8')
        content = content.replace('@CMAKE_INSTALL_PREFIX@', str(tmp_path))
        hooks = ('AMENT_ENVIRONMENT_HOOKS="$AMENT_CURRENT_PREFIX/share/foo/hook.sh"'
                 if destination == 'local_setup.sh' else '')
        content = content.replace('@ENVIRONMENT_HOOKS@', hooks)
        (package / destination).write_text(content, encoding='utf-8')

    env = {key: value for key, value in os.environ.items()
           if not key.startswith(('AMENT_', 'COLCON_'))}
    result = subprocess.run(
        [shell, '-euc',
         f'. "{package}/{script}"; printf "%s\\n" "$MY_PATH"'],
        capture_output=True, text=True, env=env)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == str(package)
