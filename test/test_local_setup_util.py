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

import os
from pathlib import Path
import subprocess
import sys
from types import ModuleType

import pytest


# --- topological ordering ---------------------------------------------------

def test_order_packages_linear_chain(util: ModuleType) -> None:
    # c -> b -> a
    packages = {'a': set(), 'b': {'a'}, 'c': {'b'}}
    assert util.order_packages(packages) == ['a', 'b', 'c']


def test_order_packages_independent_are_alphabetical(util: ModuleType) -> None:
    packages = {'c': set(), 'a': set(), 'b': set()}
    assert util.order_packages(packages) == ['a', 'b', 'c']


def test_order_packages_diamond(util: ModuleType) -> None:
    # d -> {b, c}, both -> a
    packages = {'a': set(), 'b': {'a'}, 'c': {'a'}, 'd': {'b', 'c'}}
    assert util.order_packages(packages) == ['a', 'b', 'c', 'd']


def test_order_packages_detects_cycle(util: ModuleType) -> None:
    with pytest.raises(RuntimeError, match='Circular dependency'):
        util.order_packages({'a': {'b'}, 'b': {'a'}})


def test_reduce_cycle_set_keeps_only_cycle_members(util: ModuleType) -> None:
    # 'x' is not part of the a <-> b cycle and should be dropped.
    packages = {'a': {'b'}, 'b': {'a'}, 'x': {'a'}}
    util.reduce_cycle_set(packages)
    assert set(packages) == {'a', 'b'}


# --- package discovery ------------------------------------------------------

def _make_resource_index(prefix: Path) -> Path:
    index = prefix / 'share/ament_index/resource_index'
    (index / 'packages').mkdir(parents=True)
    (index / 'package_run_dependencies').mkdir(parents=True)
    return index


def _add_package(index: Path, name: str, deps: str = '') -> None:
    (index / 'packages' / name).write_text('', encoding='utf-8')
    (index / 'package_run_dependencies' / name).write_text(
        deps, encoding='utf-8')


def test_get_packages_reads_runtime_dependencies(util: ModuleType, tmp_path: Path) -> None:
    index = _make_resource_index(tmp_path)
    _add_package(index, 'foo')
    _add_package(index, 'bar', deps='foo')
    assert util.get_packages(tmp_path) == {'foo': set(), 'bar': {'foo'}}


def test_get_packages_strips_unknown_dependencies(util: ModuleType, tmp_path: Path) -> None:
    index = _make_resource_index(tmp_path)
    # 'ghost' has no resource marker, so it must be filtered out.
    _add_package(index, 'bar', deps='ghost')
    assert util.get_packages(tmp_path) == {'bar': set()}


def test_get_packages_empty_prefix(util: ModuleType, tmp_path: Path) -> None:
    assert util.get_packages(tmp_path) == {}


# --- command emitting helpers (sh) ------------------------------------------

def test_set_emits_export(util_sh: ModuleType) -> None:
    assert util_sh._set('X', '/a') == ['export X="/a"']


def test_append_unique_value_dedups(util_sh: ModuleType, monkeypatch: pytest.MonkeyPatch) -> None:
    sep = os.pathsep
    monkeypatch.delenv('MY_LIST', raising=False)
    assert util_sh._append_unique_value('MY_LIST', '/a') == \
        [f'export MY_LIST="$MY_LIST{sep}/a"']
    # a second identical append is suppressed
    assert util_sh._append_unique_value('MY_LIST', '/a') == []


def test_prepend_unique_value_dedups(util_sh: ModuleType, monkeypatch: pytest.MonkeyPatch) -> None:
    sep = os.pathsep
    monkeypatch.delenv('MY_LIST', raising=False)
    assert util_sh._prepend_unique_value('MY_LIST', '/a') == \
        [f'export MY_LIST="/a{sep}$MY_LIST"']
    assert util_sh._prepend_unique_value('MY_LIST', '/a') == []


def test_set_if_unset_sets_when_absent(
    util_sh: ModuleType, monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv('MY_MODE', raising=False)
    assert util_sh._set_if_unset('MY_MODE', 'release') == \
        ['export MY_MODE="release"']


def test_set_if_unset_comments_when_already_set(
    util_sh: ModuleType, monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv('MY_MODE', 'debug')
    assert util_sh._set_if_unset('MY_MODE', 'release') == \
        ['# export MY_MODE="release"']


def test_handle_set_type(util_sh: ModuleType, tmp_path: Path) -> None:
    assert util_sh.handle_dsv_types_except_source(
        util_sh.DSV_TYPE_SET, 'NAME;value', prefix=str(tmp_path)) == \
        ['export NAME="value"']


def test_handle_unknown_type_raises(util_sh: ModuleType, tmp_path: Path) -> None:
    with pytest.raises(RuntimeError, match='unknown environment hook type'):
        util_sh.handle_dsv_types_except_source(
            'bogus', 'x', prefix=str(tmp_path))


# --- end to end (run the shipped script standalone) -------------------------

def _write_prefix_with_foo(tmp_path: Path) -> None:
    index = _make_resource_index(tmp_path)
    _add_package(index, 'foo')
    (tmp_path / 'share/foo/bin').mkdir(parents=True)
    (tmp_path / 'share/foo/package.dsv').write_text(
        'set;FOO_VAR;share/foo\n'
        'prepend-non-duplicate;MY_PATH;share/foo/bin\n',
        encoding='utf-8')


def _copy_script(util: ModuleType, tmp_path: Path) -> Path:
    script = tmp_path / '_local_setup_util.py'
    script.write_text(
        Path(util.__file__).read_text(encoding='utf-8'), encoding='utf-8')
    return script


def test_end_to_end_sh(util: ModuleType, tmp_path: Path) -> None:
    _write_prefix_with_foo(tmp_path)
    script = _copy_script(util, tmp_path)
    env = {**os.environ, 'AMENT_TRACE_SETUP_FILES': '1'}
    result = subprocess.run(
        [sys.executable, str(script), 'sh'],
        capture_output=True, text=True, env=env, check=True)
    assert '# Package: foo' in result.stdout
    assert 'export FOO_VAR=' in result.stdout
    assert 'MY_PATH' in result.stdout


def test_end_to_end_unknown_extension_exits_nonzero(util: ModuleType, tmp_path: Path) -> None:
    script = _copy_script(util, tmp_path)
    result = subprocess.run(
        [sys.executable, str(script), 'zzz'],
        capture_output=True, text=True)
    assert result.returncode == 1
    assert 'Unknown primary extension: zzz' in result.stderr
