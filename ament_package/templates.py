# Copyright 2014 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import re

TEMPLATE_DIRECTORY = os.path.join(os.path.dirname(__file__), 'template')


def get_environment_hook_template_path(name):
    return os.path.join(TEMPLATE_DIRECTORY, 'environment_hook', name)


def get_package_level_template_names():
    return ['local_setup.%s.in' % ext for ext in ['bash', 'sh', 'zsh']]


def get_package_level_template_path(name):
    return os.path.join(TEMPLATE_DIRECTORY, 'package_level', name)


def get_prefix_level_template_names():
    extensions = ['bash', 'sh.in', 'zsh']
    return ['local_setup.%s' % ext for ext in extensions] + \
        ['setup.%s' % ext for ext in extensions]


def get_prefix_level_template_path(name):
    return os.path.join(TEMPLATE_DIRECTORY, 'prefix_level', name)


def configure_file(template_file, environment):
    '''
    Evaluate a .in template file used in CMake with configure_file().

    :param template_file: path to the template, ``str``
    :param environment: dictionary of placeholders to substitute,
      ``dict``
    :returns: string with evaluates template
    :raises: KeyError for placeholders in the template which are not
      in the environment
    '''
    with open(template_file, 'r') as f:
        template = f.read()
        return configure_string(template, environment)


def configure_string(template, environment):
    '''
    Substitute variables enclosed by @ characters.

    :param template: the template, ``str``
    :param environment: dictionary of placeholders to substitute,
      ``dict``
    :returns: string with evaluates template
    :raises: KeyError for placeholders in the template which are not
      in the environment
    '''
    def substitute(match):
        var = match.group(0)[1:-1]
        return environment[var]
    return re.sub('\@[a-zA-Z0-9_]+\@', substitute, template)
