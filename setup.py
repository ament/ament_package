from setuptools import find_packages
from setuptools import setup

setup(
    name='ament_package',
    version='0.6.0',
    packages=find_packages(exclude=['test']),
    zip_safe=True,
    author='Dirk Thomas',
    author_email='dthomas@osrfoundation.org',
    maintainer='Dirk Thomas',
    maintainer_email='dthomas@osrfoundation.org',
    url='https://github.com/ament/ament_package/wiki',
    download_url='https://github.com/ament/ament_package/releases',
    keywords=['ROS'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Topic :: Software Development',
    ],
    description='Ament is a build system for federated packages.',
    long_description="""\
Ament defines metainformation for packages, their dependencies,
and provides tooling to build these federated packages together.""",
    license='Apache License, Version 2.0',
    tests_require=['flake8', 'pytest'],
    package_data={
        'ament_package': [
            'template/environment_hook/*',
            'template/isolated_prefix_level/*',
            'template/package_level/*',
            'template/prefix_level/*',
        ],
    },
)
