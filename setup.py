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
from dpp import __version__

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / 'README.md').read_text()


# This call to setup() does all the work
setup(
    name='decoder-plus-plus',
    version=__version__,
    description='An extensible application for penetration testers and software developers to decode/encode data into various formats.',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/bytebutcher/decoder-plus-plus',
    author='bytebutcher',
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
        'passlib>=1.7.4',
        'fuzzywuzzy>=0.18.0',
        'filemagic>=1.6',
        'hashid>=3.1.4',
        'urlextract>=1.6.0',
        'lxml>=4.9.1',
        'pycryptodome>=3.15.0'
    ],
    extras_require={
        'qt5': ['PyQt5<5.16'],
        'qt6': ['PyQt6<6.2.0']
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
