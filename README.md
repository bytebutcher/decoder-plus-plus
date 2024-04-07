![Decoder++ Logo](https://raw.githubusercontent.com/bytebutcher/decoder-plus-plus/master/images/dpp.png)

<a href="https://pypi.python.org/pypi/decoder-plus-plus"><img src="https://img.shields.io/pypi/v/decoder-plus-plus.svg"></a>
<a href="https://pypi.python.org/pypi/decoder-plus-plus"><img src="https://img.shields.io/pypi/dm/decoder-plus-plus"></a>
<a href="https://pypi.python.org/pypi/decoder-plus-plus"><img src="https://img.shields.io/pypi/pyversions/decoder-plus-plus.svg"></a>

# Decoder++

Decoder++ is an extensible application designed for penetration testers, software developers, 
and anyone in between looking to effortlessly decode and encode data across various formats. 
It includes a wide range of preinstalled scripts and codecs, smart decoding and format identification, 
and supports both graphical user interface (GUI) and command-line interface (CLI) operations.

## Quick Start

Get up and running with Decoder++ in just a few steps:

```bash
# Install using pip (latest:qt6)
pip3 install decoder-plus-plus[qt6]

# Or, for a qt5 backport:
pip3 install decoder-plus-plus[qt5]

# To leverage all features and plugins:
pip3 install decoder-plus-plus[extras]
```

For a detailed installation guide, including platform-specific instructions, see the [Installation Guide](docs/INSTALL.md).

## Overview

This section provides an overview about the individual ways of interacting with
```Decoder++```. For additional usage information check out the ```Advanced Usage``` section.

### Graphical User Interface

The graphical user interface provides two distinct interaction modes:
a ```main-window-mode``` and a ```dialog-mode```.

![Decoder++ Screenshot](https://raw.githubusercontent.com/bytebutcher/decoder-plus-plus/master/images/dpp-preview-001.png)

While the ```main-window-mode``` supports tabbing, the ```dialog-mode``` has the ability to return the transformed 
content to ```stdout``` ready for further processing. 
As a result ```Decoder++``` can enhance other tools/scripts 
by providing a graphical user interface for flexible transformation of any input.

![Decoder++ Screenshot](https://raw.githubusercontent.com/bytebutcher/decoder-plus-plus/master/images/dpp-preview-dialog.png)

### Command Line

In addition to the graphical user interface Decoder++ also provides a command line interface:
```bash
$ dpp -e base64 -h sha1 "Hello, world!"
e52d74c6d046c390345ae4343406b99587f2af0d
```

### Codecs and Scripts

```Decoder++``` allows you to choose from a variety of codecs and scripts:

* **Encode/Decode:**
  - Base16, Base32, Base45, Base64, Base64 (URL-safe)
  - Binary, Gzip, Hex, Html, JWT, HTTP64
  - Octal, Url, Url+, Zlib
* **Hashing:** 
  - Adler-32, Apache-Md5, CRC32, FreeBSD-NT
  - Keccak224, Keccak256, Keccak384, Keccak512
  - LM, Md2, Md4, Md5, NT, PHPass
  - RipeMd160, Sha1, Sha3 224, Sha3 256, Sha3 384, Sha3 512
  - Sha224, Sha256, Sha348, Sha512, Sun Md5
* **Scripts:**
  - Caesar, CSS-Minify, Custom Code, Extract URLs, Filter-Lines
  - Identify File Format, Identify Hash Format, JS-Beautifier, JS-to-XML, JQ
  - JSONify, JSONPath, HTML-Beautifier
  - Little/Big-Endian Transform, Reformat Text, Remove Newlines, Remove Whitespaces
  - Search and Replace, Split and Rejoin, Unescape/Escape String, XPath


In cases where you require a bit more flexibility ```Decoder++``` allows you to process your data with 
custom scripts by using the ```Custom Code``` script:

![Decoder++ Screenshot](https://raw.githubusercontent.com/bytebutcher/decoder-plus-plus/master/images/dpp-custom-code-script.png)

## Advanced Usage

This section provides additional information about how the command line interface can be used.

### Command Line Interface

The commandline interface gives easy access to all available codecs.

To list them the ```-l``` argument can be used. To narrow down the search 
the ```-l``` argument accepts additional parameters which work as filter:

```bash
$ dpp -l base enc

Codec                 Type
-----                 ----
base16                encoder
base32                encoder
base64                encoder

```
```Decoder++``` distinguishes between encoders, decoders, hashers and scripts.
Like the graphical user interface the command line interface allows the usage of multiple codecs in a row:
```bash
$ dpp "H4sIAAXmeVsC//NIzcnJ11Eozy/KSVEEAObG5usNAAAA" -d base64 -d gzip
Hello, world!
```

While encoders, decoders and hashers can be used right away, some scripts may require additional configuration.
To show all available options of a specific script add the ```help``` parameter:
```
$ dpp "Hello, world!" -s split_and_rejoin help

Split & Rejoin
==============

             Name  Value  Group            Required  Description
             ----  -----  -----            --------  -----------
   split_by_chars         split_behaviour  yes       the chars used at which to split the text
  split_by_length  0      split_behaviour  yes       the length used at which to split the text
rejoin_with_chars                          yes       the chars used to join the splitted text

```

To configure a specific script the individual options need to be supplied as name-value pairs (e.g. ```search_term="Hello"```):

```
$ dpp "Hello, world!" -s search_and_replace search_term="Hello" replace_term="Hey"
Hey, world!
```

## Contribute

Feel free to open a new ticket for requesting features or reporting bugs. 
Also don't hesitate to issue a pull-request for new features/plugins. 
More information regarding Decoder++ development can be found in the 
[Development Guide](docs/DEVELOPMENT.md).

Thanks to 
* Tim Menapace (RIPEMD160, KECCAK256)
* Robin Krumnow (ROT13)

## Troubleshooting

### Signals are not working on Mac OS

When starting ```Decoder++``` in Mac OS signals are not working.

This might happen when ```PyQt6``` is installed using homebrew. 

### Can not start Decoder++ in Windows using CygWin

When starting ```Decoder++``` in ```CygWin``` an error occurs:
```
  ModuleNotFoundError: No module named 'PyQt6'
```

This might happen even if ```PyQt6``` is installed using pip. 
Currently there is no fix for that. Instead it is recommended
to start ```Decoder++``` using the Windows command line.

### No Module PyQt6 

When starting ```Decoder++``` the error ```No module named 'PyQt6.sig'``` is displayed on the console. 
This may happen when there are competing versions of PyQt6 installed. Reinstalling PyQt6 should fix this error.

```
$ sudo pip3 uninstall PyQt6
$ sudo pip3 install PyQt6
```

### Missing Qt6 libraries

At least in Ubuntu 22.04 it might be necessary to install the following packages using ```apt```:

```
apt install libqt6core6 libqt6network6 libqt6openglwidgets6 libqt6widgets6
```

### X11-forwarding fails

In order to run dpp inside a container/virtual machine you may need to install the 
```qt6-qpa-plugins``` inside the container/virtual machine and configure the 
```QT_QPA_PLATFORM_PLUGIN_PATH``` accordingly:

```
apt install qt6-qpa-plugins
export QT_QPA_PLATFORM_PLUGIN_PATH=/usr/lib/x86_64-linux-gnu/qt6/plugins/platforms/
``` 

See the <a href="https://github.com/bytebutcher/decoder-plus-plus/tree/master/docker">Docker build and run scripts</a> for more information regarding how to build and run a Decoder++ Docker container.

## Inspired By
* PortSwigger's Burp Decoder

## Powered By

* QtPy / PyQt5 / PyQt6
* QtAwesome
