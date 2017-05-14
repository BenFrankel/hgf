#!/usr/bin/env python

from setuptools import setup, find_packages


with open('README.rst') as f:
    long_description = f.read()


setup(
        name='hgf',
        version='0.1.0',

        # Meta info for PyPI
        description='Pygame-based framework for building hierarchical GUIs.',
        long_description=long_description,
        author='Ben Frankel',
        author_email='ben.frankel7@gmail.com',
        url='https://www.github.com/',
        keywords='pygame hierarchical gui framework',
        # TODO: license, change url (put docs on github.io)

        packages=find_packages(),
        requires=['pygame (>=1.9.2, <2.0)'],
)
