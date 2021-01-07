import pathlib
import setuptools
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="decoder-plus-plus",
    version="1.1.4",
    description="An extensible application for penetration testers and software developers to decode/encode data into various formats.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/bytebutcher/decoder-plus-plus",
    author="bytebutcher",
    author_email="thomas.engel.web@gmail.com",
    license="GPL-3.0",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ],
    packages=setuptools.find_packages(),
    install_requires=[
        'PyQt5==5.15', 
        'QtAwesome==1.0.2',
        'pysha3==1.0.2',
        'passlib==1.7.4',
        'fuzzywuzzy==0.18.0', 
        'filemagic==1.6', 
        'hashid==3.1.4'
    ],
    data_files=[
        ('share/icons/hicolor/scalable/apps', ['data/dpp.png']),
        ('share/applications', ['data/dpp.desktop'])
    ],
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "dpp=dpp.runner:main",
        ]
    },
)
