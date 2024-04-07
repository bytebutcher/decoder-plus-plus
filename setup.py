# vim: ts=8:sts=8:sw=8:noexpandtab
#
# This file is part of Decoder++
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import pathlib
import setuptools
from setuptools import setup
from dpp import __name__, __version__, __author__

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / 'README.md').read_text()


# This call to setup() does all the work
setup(
    name=__name__,
    version=__version__,
    description='An extensible application for penetration testers and software developers to decode/encode data into various formats.',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/bytebutcher/decoder-plus-plus',
    author=__author__,
    author_email='thomas.engel.web@gmail.com',
    license='GPL-3.0',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent'
    ],
    packages=setuptools.find_packages(),
    install_requires=[
        'qtpy>=2.0.0',
        'qtpynodeeditor>=0.2.0',
        'QtAwesome>=1.0.2',
        'fuzzywuzzy>=0.18.0',
        'filemagic>=1.6',
        'hashid>=3.1.4',
        'urlextract>=1.6.0',
        'lxml>=4.9.1',
    ],
    extras_require={
        'qt5': ['PyQt5<5.16'],
        'qt6': ['PyQt6<6.3.0'],
        'extras': [
            'base45>=0.4.0',
            'css-html-js-minify>=2.5.0',
            'pycryptodome>=3.15.0',
            'jc>=1.21.0',
            'jsbeautifier>=1.14.0',
            'json2xml>=3.19.0',
            'jsonpath_ng>=1.5.0',
            'jwt>=1.3.0',
            'magika>=0.5.0',
            'passlib>=1.7.0',
            'pycryptodome>=3.15.0',
            'validators>=0.20.0'
        ],
        'test': [
            'pytest-qt>=4.2.0',
        ]
    },
    data_files=[
        ('share/icons/hicolor/scalable/apps', ['data/dpp.png']),
        ('share/applications', ['data/dpp.desktop'])
    ],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'dpp=dpp.runner:main',
        ]
    },
)
