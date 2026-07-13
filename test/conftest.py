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

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]


def _load(name: str, relpath: str) -> ModuleType:
    # Load a module directly from its file so the tests run without the
    # package being installed, and so the standalone prefix-level template is
    # exercised exactly as it is when shipped into an install prefix.
    path = _REPO_ROOT / relpath
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def templates() -> ModuleType:
    return _load(
        'ament_templates_under_test',
        'ament_package/templates.py')


@pytest.fixture
def util() -> ModuleType:
    return _load(
        'local_setup_util_under_test',
        'ament_package/template/prefix_level/_local_setup_util.py')


@pytest.fixture
def util_sh(util: ModuleType) -> ModuleType:
    # Initialize the module globals to the values the 'sh' branch of main()
    # would set, so the command-emitting helpers can be unit tested directly.
    util.PRIMARY_EXTENSION = 'sh'
    util.FORMAT_STR_COMMENT_LINE = '# {comment}'
    util.FORMAT_STR_SET_ENV_VAR = 'export {name}="{value}"'
    util.FORMAT_STR_USE_ENV_VAR = '${name}'
    util.FORMAT_STR_REMOVE_LEADING_SEPARATOR = 'export {name}=${{{name}#:}}'
    util.FORMAT_STR_REMOVE_TRAILING_SEPARATOR = 'export {name}=${{{name}%:}}'
    return util
