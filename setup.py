#!/usr/bin/env python
'''
Setup script for the hep_spt package
'''

__author__ = 'Miguel Ramos Pernas'
__email__  = 'miguel.ramos.pernas@cern.ch'


# Python
import os
from setuptools import setup, find_packages

#
# Version of the package. Before a new release is made
# just the "version_info" must be changed.
#
version_info = (0, 0, 0)
version = '.'.join(map(str, version_info))

# Setup function
setup(

    name = 'hep_spt',

    version = version,

    description = 'Provides statistical and plotting tools using general '\
    'python packages, focused to High Energy Physics.',

    # Read the long description from the README
    long_description = open('README.rst').read(),

    # Keywords to search for the package
    keywords = 'physics hep statistics plotting',

    # Find all the packages in this directory
    packages = find_packages(),

    # Data files
    package_data = {'hep_spt': ['data/*', 'mpl/*']},

    # Requisites
    install_requires = ['matplotlib', 'numpy', 'pytest', 'scipy'],

    # Test requirements
    setup_requires = ['pytest-runner'],

    tests_require = ['pytest'],
    )


# Create a module with the versions
version_file = open('hep_spt/version.py', 'wt')
version_file.write("""\
'''
Auto-generated module holding the version of the hep_spt package
'''

__version__ = "{}"
__version_info__ = {}

__all__ = ['__version__', '__version_info__']
""".format(version, version_info))
version_file.close()