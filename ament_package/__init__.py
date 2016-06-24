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

"""Library for parsing package.xml and providing an object representation."""

# set version number
try:
    import pkg_resources
    try:
        __version__ = pkg_resources.require('ament_package')[0].version
    except pkg_resources.DistributionNotFound:
        __version__ = 'unset'
    finally:
        del pkg_resources
except ImportError:
    __version__ = 'unset'

PACKAGE_MANIFEST_FILENAME = 'package.xml'


def parse_package(path):
    """
    Parse package manifest.

    :param path: The path of the package.xml file, it may or may not
    include the filename

    :returns: return :class:`Package` instance, populated with parsed fields
    :raises: :exc:`InvalidPackage`
    :raises: :exc:`IOError`
    """
    import os

    from .exceptions import InvalidPackage

    if os.path.isfile(path):
        filename = path
    elif package_exists_at(path):
        filename = os.path.join(path, PACKAGE_MANIFEST_FILENAME)
        if not os.path.isfile(filename):
            raise IOError("Directory '%s' does not contain a '%s'" %
                          (path, PACKAGE_MANIFEST_FILENAME))
    else:
        raise IOError("Path '%s' is neither a directory containing a '%s' "
                      "file nor a file" % (path, PACKAGE_MANIFEST_FILENAME))

    with open(filename, 'r', encoding='utf-8') as f:
        try:
            return parse_package_string(f.read(), filename=filename)
        except InvalidPackage as e:
            e.args = [
                "Invalid package manifest '%s': %s" %
                (filename, e)]
            raise


def package_exists_at(path):
    """
    Check that a package exists at the given path.

    :param path: path to a package
    :type path: str
    :returns: True if package exists in given path, else False
    :rtype: bool
    """
    import os

    return os.path.isdir(path) and os.path.isfile(
        os.path.join(path, PACKAGE_MANIFEST_FILENAME))


def parse_package_string(data, *, filename=None):
    """
    Parse package.xml string contents.

    :param data: package.xml contents, ``str``
    :param filename: full file path for debugging, ``str``
    :returns: return parsed :class:`Package`
    :raises: :exc:`InvalidPackage`
    """
    from copy import deepcopy
    from xml.dom import minidom

    from .exceptions import InvalidPackage
    from .export import Export
    from .package import Package
    from .person import Person
    from .url import Url

    try:
        root = minidom.parseString(data)
    except Exception as ex:
        if filename is not None:
            msg = "The manifest '%s' contains invalid XML:\n" % filename
        else:
            msg = 'The manifest contains invalid XML:\n'
        raise InvalidPackage(msg + str(ex))

    pkg = Package(filename=filename)

    # verify unique root node
    nodes = _get_nodes(root, 'package')
    if len(nodes) != 1:
        raise InvalidPackage("The manifest must contain a single 'package' "
                             "root tag")
    root = nodes[0]

    # format attribute
    value = _get_node_attr(root, 'format', default=1)
    pkg.package_format = int(value)
    assert pkg.package_format > 1, \
        "Unable to handle '%s' format version '%d', please update the " \
        "manifest file to at least format version 2" % \
        (filename, pkg.package_format)
    assert pkg.package_format in [2], \
        "Unable to handle '%s' format version '%d', please update " \
        "'ament_package' (e.g. on Ubuntu/Debian use: sudo apt-get update && " \
        "sudo apt-get install --only-upgrade python-ament-package)" % \
        (filename, pkg.package_format)

    # name
    pkg.name = _get_node_value(_get_node(root, 'name'))

    # version
    version_node = _get_node(root, 'version')
    pkg.version = _get_node_value(version_node)

    # description
    pkg.description = _get_node_value(
        _get_node(root, 'description'), allow_xml=True, apply_str=False)

    # at least one maintainer, all must have email
    maintainers = _get_nodes(root, 'maintainer')
    for node in maintainers:
        pkg.maintainers.append(Person(
            _get_node_value(node, apply_str=False),
            email=_get_node_attr(node, 'email')
        ))

    # urls with optional type
    urls = _get_nodes(root, 'url')
    for node in urls:
        pkg.urls.append(Url(
            _get_node_value(node),
            url_type=_get_node_attr(node, 'type', default='website')
        ))

    # authors with optional email
    authors = _get_nodes(root, 'author')
    for node in authors:
        pkg.authors.append(Person(
            _get_node_value(node, apply_str=False),
            email=_get_node_attr(node, 'email', default=None)
        ))

    # at least one license
    licenses = _get_nodes(root, 'license')
    for node in licenses:
        pkg.licenses.append(_get_node_value(node))

    errors = []
    # dependencies and relationships
    pkg.build_depends = _get_dependencies(root, 'build_depend')
    pkg.buildtool_depends = _get_dependencies(root, 'buildtool_depend')
    pkg.build_export_depends = _get_dependencies(root, 'build_export_depend')
    pkg.buildtool_export_depends = _get_dependencies(root,
                                                     'buildtool_export_depend')
    pkg.exec_depends = _get_dependencies(root, 'exec_depend')
    depends = _get_dependencies(root, 'depend')
    for dep in depends:
        # check for collisions with specific dependencies
        same_build_depends = ['build_depend' for d in pkg.build_depends
                              if d.name == dep.name]
        same_build_export_depends = ['build_export_depend'
                                     for d in pkg.build_export_depends
                                     if d.name == dep.name]
        same_exec_depends = ['exec_depend' for d in pkg.exec_depends
                             if d.name == dep.name]
        if same_build_depends or same_build_export_depends or \
                same_exec_depends:
            errors.append("The generic dependency on '%s' is redundant with: "
                          "%s" % (dep.name,
                                  ', '.join(same_build_depends +
                                            same_build_export_depends +
                                            same_exec_depends)))
            errors.append(
                "The generic dependency on '%s' is redundant with: %s" %
                (dep.name, ', '.join(
                    same_build_depends +
                    same_build_export_depends +
                    same_exec_depends)))
        # only append non-duplicates
        if not same_build_depends:
            pkg.build_depends.append(deepcopy(dep))
        if not same_build_export_depends:
            pkg.build_export_depends.append(deepcopy(dep))
        if not same_exec_depends:
            pkg.exec_depends.append(deepcopy(dep))
    pkg.doc_depends = _get_dependencies(root, 'doc_depend')
    pkg.test_depends = _get_dependencies(root, 'test_depend')
    pkg.conflicts = _get_dependencies(root, 'conflict')
    pkg.replaces = _get_dependencies(root, 'replace')

    # exports
    export_node = _get_optional_node(root, 'export')
    if export_node is not None:
        exports = []
        for node in [n for n in export_node.childNodes
                     if n.nodeType == n.ELEMENT_NODE]:
            export = Export(str(node.tagName),
                            content=_get_node_value(node, allow_xml=True))
            for key, value in node.attributes.items():
                export.attributes[str(key)] = str(value)
            exports.append(export)
        pkg.exports = exports

    # verify that no unsupported tags and attributes are present
    valid_root_attributes = [
        'format',
        'xmlns:xsi',
        'xsi:noNamespaceSchemaLocation'
    ]
    unknown_root_attributes = [attr for attr in root.attributes.keys()
                               if str(attr) not in valid_root_attributes]
    if unknown_root_attributes:
        errors.append("The 'package' tag must not have the following "
                      "attributes: %s" % ', '.join(unknown_root_attributes))
    depend_attributes = [
        'version_lt',
        'version_lte',
        'version_eq',
        'version_gte',
        'version_gt'
    ]
    known = {
        'name': [],
        'version': [],
        'description': [],
        'maintainer': ['email'],
        'license': [],
        'url': ['type'],
        'author': ['email'],
        'build_depend': depend_attributes,
        'buildtool_depend': depend_attributes,
        'build_export_depend': depend_attributes,
        'buildtool_export_depend': depend_attributes,
        'depend': depend_attributes,
        'exec_depend': depend_attributes,
        'doc_depend': depend_attributes,
        'test_depend': depend_attributes,
        'conflict': depend_attributes,
        'replace': depend_attributes,
        'export': [],
    }
    nodes = [n for n in root.childNodes if n.nodeType == n.ELEMENT_NODE]
    unknown_tags = set([n.tagName for n in nodes
                        if n.tagName not in known.keys()])
    if unknown_tags:
        errors.append('The manifest (with format version %d) must not contain '
                      'the following tags: %s' %
                      (pkg.package_format, ', '.join(unknown_tags)))
    for node in [n for n in nodes if n.tagName in known.keys()]:
        unknown_attrs = [str(attr) for attr in node.attributes.keys()
                         if str(attr) not in known[node.tagName]]
        if unknown_attrs:
            errors.append(
                "The '%s' tag must not have the following attributes: %s" %
                (node.tagName, ', '.join(unknown_attrs)))
        if node.tagName not in ['description', 'export']:
            subnodes = [n for n in node.childNodes
                        if n.nodeType == n.ELEMENT_NODE]
            if subnodes:
                errors.append("The '%s' tag must not contain the following "
                              "children: %s" %
                              (node.tagName,
                               ', '.join([n.tagName for n in subnodes])))

    if errors:
        raise InvalidPackage(
            'Error(s) in %s:%s' %
            (filename, ''.join(['\n- %s' % e for e in errors])))

    pkg.validate()

    return pkg


def _get_nodes(parent, tagname):
    return [n for n in parent.childNodes
            if n.nodeType == n.ELEMENT_NODE and n.tagName == tagname]


def _get_node(parent, tagname):
    from .exceptions import InvalidPackage

    nodes = _get_nodes(parent, tagname)
    if len(nodes) != 1:
        raise InvalidPackage(
            "The manifest must contain exactly one '%s' tags" % tagname)
    return nodes[0]


def _get_optional_node(parent, tagname):
    from .exceptions import InvalidPackage

    nodes = _get_nodes(parent, tagname)
    if len(nodes) > 1:
        raise InvalidPackage(
            "The manifest must not contain more than one '%s' tags" % tagname)
    return nodes[0] if nodes else None


def _get_node_value(node, *, allow_xml=False, apply_str=True):
    if allow_xml:
        value = (''.join([n.toxml()
                          for n in node.childNodes])).strip(' \n\r\t')
    else:
        value = (''.join([n.data for n in node.childNodes
                          if n.nodeType == n.TEXT_NODE])).strip(' \n\r\t')
    if apply_str:
        value = str(value)
    return value


def _get_optional_node_value(parent, tagname, *, default=None):
    node = _get_optional_node(parent, tagname)
    if node is None:
        return default
    return _get_node_value(node)


def _get_node_attr(node, attr, *, default=False):
    # default=False means value is required
    from .exceptions import InvalidPackage

    if node.hasAttribute(attr):
        return str(node.getAttribute(attr))
    if default is False:
        raise InvalidPackage(
            "The '%s' tag must have the attribute \"%s\"" %
            (node.tagName, attr))
    return default


def _get_dependencies(parent, tagname):
    from .dependency import Dependency

    depends = []
    for node in _get_nodes(parent, tagname):
        depend = Dependency(_get_node_value(node))
        for attr in [s for s in depend.__slots__ if s != 'name']:
            setattr(depend, attr, _get_node_attr(node, attr, default=None))
        depends.append(depend)
    return depends
