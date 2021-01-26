import collections
import os.path
import xml.dom.minidom as dom


Person = collections.namedtuple('Person', ['name', 'email'])


def get_single_element(document, tag_name):
    """Return the text contained with the first tag with the specified tag_name."""
    return document.getElementsByTagName(tag_name)[0].firstChild.nodeValue


def get_elements(document, tag_name):
    """Return the text contained with the tags with the specified tag_name."""
    for tag in document.getElementsByTagName(tag_name):
        yield tag.firstChild.nodeValue


def get_elements_and_attributes(document, tag_name, attribute_name):
    """Return the text contained with the matching tags and the value of an attribute."""
    for tag in document.getElementsByTagName(tag_name):
        yield tag.firstChild.nodeValue, tag.getAttribute(attribute_name)


def update_people_info(document, tag_name, data):
    """Set the author or maintainer field in data."""
    people = [Person(*ea) for ea in get_elements_and_attributes(document, tag_name, 'email')]

    # either set one person with one email or join all in a single field
    if len(people) == 1 and people[0].email:
        data[tag_name] = people[0].name
        data[f'{tag_name}_email'] = people[0].email
    else:
        arr = [(f'{p.name} {p.email}' if p.email else p.name) for p in people]
        data[tag_name] = ', '.join(arr)


def generate_setuptools_dict(package_xml_path=os.path.curdir, **kwargs):
    """
    Extract the information relevant for setuptools from the package manifest.

    The following keys will be set:
    The "name" and "version" are taken from the eponymous tags.
    A single maintainer will set the keys "maintainer" and
    "maintainer_email" while multiple maintainers are merged into the
    "maintainer" fields (including their emails). Authors are handled
    likewise.
    The first URL of type "website" (or without a type) is used for
    the "url" field.
    The "description" is taken from the eponymous tag if it does not
    exceed 200 characters. If it does "description" contains the
    truncated text while "description_long" contains the complete.
    All licenses are merged into the "license" field.
    :param kwargs: All keyword arguments are passed through. The above
        mentioned keys are verified to be identical if passed as a
        keyword argument
    :returns: return dict populated with parsed fields and passed
        keyword arguments
    :raises: :exc:`RuntimeError`
    :raises: :exc:`IOError`
    """
    filename = os.path.join(package_xml_path, 'package.xml')
    package_xml = dom.parse(open(filename))

    data = {}
    data['name'] = get_single_element(package_xml, 'name')
    data['version'] = get_single_element(package_xml, 'version')

    update_people_info(package_xml, 'author', data)
    update_people_info(package_xml, 'maintainer', data)

    # either set the first URL with the type 'website' or the first URL of any type
    urls = list(get_elements_and_attributes(package_xml, 'url', 'type'))
    websites = [url[0] for url in urls if url[1] == 'website']
    if websites:
        data['url'] = websites[0]
    elif urls:
        data['url'] = list(urls)[0][0]

    description = get_single_element(package_xml, 'description')
    if len(description) <= 200:
        data['description'] = description
    else:
        data['description'] = description[:197] + '...'
        data['long_description'] = description

    data['license'] = ', '.join(get_elements(package_xml, 'license'))

    # pass keyword arguments and verify equality if generated and passed in
    for k, v in kwargs.items():
        if k in data:
            if v != data[k]:
                raise RuntimeError(f'The keyword argument "{k}" does not match the information '
                                   f'from package.xml in {package_xml_path}: "{v}" != "{data[k]}"')
        else:
            data[k] = v

    return data
