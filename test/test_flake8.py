# Copyright 2016 Open Source Robotics Foundation, Inc.
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
import pytest

from flake8.api.legacy import get_style_guide


@pytest.mark.flake8
@pytest.mark.linter
def test_flake8():
    # Configuration options adapted from the ament_flake8
    # https://github.com/ament/ament_lint/blob/master/ament_flake8/ament_flake8/configuration/ament_flake8.ini
    style = get_style_guide(
        ignore='C816,D100,D101,D102,D103,D104,D105,D106,D107,D203,D212,D404,I202',
        import_order_style='google',
        max_line_length=99,
        show_source=True,
        statistics=True)
    results = style.check_files()
    assert results.total_errors == 0, 'Found code style errors / warnings'
