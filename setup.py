# Copyright 2011 Terena. All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#    1. Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#
#    2. Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY TERENA ``AS IS'' AND ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
# EVENT SHALL TERENA OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and documentation are
# those of the authors and should not be interpreted as representing official
# policies, either expressed or implied, of Terena.

import fnmatch
import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


def recursive_include(directory, patterns):
    result = []
    for root, dirs, files in os.walk(directory):
        child_root = root.replace(directory, '').lstrip('/')
        for pattern in patterns:
            result.extend([os.path.join(child_root, name)
                           for name in fnmatch.filter(files, pattern)])
    return result

# be careful with the syntax of this line since it is parsed from
# the docs/conf.py file
VERSION = '0.17.0'

setup(
    name='peer',
    version=VERSION,
    url='https://github.com/Yaco-Sistemas/peer',
    license='BSD',
    description=('Public Endpoint Entities Registry'),
    long_description=(read('README.rst') + '\n\n' + read('CHANGES.rst')),
    author='Terena',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    packages=find_packages('.'),
    package_dir={'peer': 'peer'},
    package_data={
        'peer': recursive_include('peer', ['*.html', '*.css', '*.js', '*.txt',
                                           '*.png', '*.ico', '*.wsgi', '*.xsd'])
    },
    zip_safe=False,
    install_requires=[
        'Django==1.7.1',
        'psycopg2==2.4.2',
        'django-registration-redux==1.1',
        'django-recaptcha==1.0.2',
        'fudge==1.0.3',
        'django-vff==0.2b3',
        'lxml==3.1.2',
        'Pygments==1.4',
        'dnspython==1.11.0',
        'gitdb==0.6.4',
        'djangosaml2==0.13.0',
        'python-whois==0.2',
        'publicsuffix==1.0.5',
        'pycrypto==2.6.1',
    ],
    dependency_links=[
    ]
)
