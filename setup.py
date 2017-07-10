#!/usr/bin/env python
###############################################################################
#                                                                             #
#   Copyright 2017 - Ben Frankel                                              #
#                                                                             #
#   Licensed under the Apache License, Version 2.0 (the "License");           #
#   you may not use this file except in compliance with the License.          #
#   You may obtain a copy of the License at                                   #
#                                                                             #
#       http://www.apache.org/licenses/LICENSE-2.0                            #
#                                                                             #
#   Unless required by applicable law or agreed to in writing, software       #
#   distributed under the License is distributed on an "AS IS" BASIS,         #
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  #
#   See the License for the specific language governing permissions and       #
#   limitations under the License.                                            #
#                                                                             #
###############################################################################

from setuptools import setup, find_packages


version = '0.2.0'


with open('README.md') as f:
    long_description = f.read()


setup(
        name='hgf',
        version=version,

        description='A framework for building hierarchical GUIs',
        long_description=long_description,
        author='Ben Frankel',
        author_email='ben.frankel7@gmail.com',
        license='Apache 2.0',
        url='https://www.github.com/BenFrankel/hgf',
        download_url='https://www.github.com/BenFrankel/hgf/tarball/' + version,

        keywords='hgf hierarchical gui framework',
        classifiers=[
            'Development Status :: 2 - Pre-Alpha',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: Apache Software License',
            'Natural Language :: English',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 3 :: Only',
            'Topic :: Software Development :: Libraries :: Application Frameworks',
            'Topic :: Software Development :: Libraries :: pygame',
        ],

        packages=find_packages(),
        install_requires=[
            'pygame (>=1.9.1)',
            'pyperclip'
        ],
        provides=['hgf']
)
