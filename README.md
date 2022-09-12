# Decoder++

![Decoder++ Logo](https://raw.githubusercontent.com/bytebutcher/decoder-plus-plus/master/dpp/images/dpp.png)

An extensible application for penetration testers and software developers to decode/encode data into various formats.

## Setup

```Decoder++``` can be either installed by using ```pip```.

```bash
# Install using pip (latest:qt6)
pip3 install decoder-plus-plus[qt6]

# Install using pip (backport:qt5)
pip3 install decoder-plus-plus[qt5]
```

Please refer to the [Installation Guide](INSTALL.md) for more information regarding individual setups. 

## Overview

This section provides you with an overview about the individual ways of interacting with ```Decoder++```. For additional
usage information check out the ```Advanced Usage``` section.

### Graphical User Interface

If you prefer a graphical user interface to transform your data
```Decoder++``` gives you two choices: a ```main-window-mode``` and a ```dialog-mode```.

![Decoder++ Screenshot](https://raw.githubusercontent.com/bytebutcher/decoder-plus-plus/master/images/dpp-preview-001.png)

While the ```main-window-mode``` supports tabbing, the ```dialog-mode``` has the ability to return the transformed content to ```stdout``` 
ready for further processing. This comes quite in handy if you want to call ```Decoder++``` from other tools 
like BurpSuite (check out the [BurpSuite Send-to extension](https://github.com/bytebutcher/burp-send-to)) or any other script
in which you want to add a graphical user interface for flexible transformation of any input.

![Decoder++ Screenshot](https://raw.githubusercontent.com/bytebutcher/decoder-plus-plus/master/images/dpp-preview-dialog.png)

### Command Line

If you don't want to startup a graphical user interface but still make use of the various transformation methods of 
```Decoder++``` you 
 can use the commandline mode:

```bash
$ dpp -e base64 -h sha1 "Hello, world!"
e52d74c6d046c390345ae4343406b99587f2af0d
```

### Features

* User Interfaces:
    * Graphical User Interface
    * Command Line Interface
* Preinstalled Scripts and Codecs:
    * **Encode/Decode:** Base16, Base32, Base45, Base64, Base64 (URL-safe), Binary, Gzip, Hex, Html, JWT, HTTP64, Octal, Url, Url+, Zlib
    * **Hashing:** Adler-32, Apache-Md5, CRC32, FreeBSD-NT, Keccak224, Keccak256, Keccak384, Keccak512, LM, Md2, Md4,
        Md5, NT, PHPass, RipeMd160, Sha1, Sha3 224, Sha3 256, Sha3 384, Sha3 512, Sha224, Sha256, Sha348, Sha512,
        Sun Md5
    * **Scripts:** CSS-Minify, Caesar, Extract URLs, Filter-Lines, Identify File Format, Identify Hash Format, JS-Beautifier, JS-to-XML, JQ, JSONPath, HTML-Beautifier, Little/Big-Endian Transform, Reformat Text, Remove Newlines, Remove Whitespaces, Search and Replace, Split and Rejoin, Unescape/Escape String, XPath
* Format-Identification
* Smart-Decode
* Plugin System
* Load & Save Current Session
* Supported Platforms:
    * Windows
    * Linux
    * MAC


## Advanced Usage

This section provides you with additional information about how the command line interface can be used.

### Command Line Interface

The commandline interface gives you easy access to all available codecs.

To list them you can use the ```-l``` argument. To narrow down your search the ```-l```
 argument accepts additional parameters which are used as filter:

```bash
$ dpp -l base enc

Codec                 Type
-----                 ----
base16                encoder
base32                encoder
base64                encoder

```
```Decoder++``` distinguishes between encoders, decoders, hashers and scripts.
Like the graphical user interface the command line interface allows you to use multiple codecs in a row:
```bash
$ dpp "H4sIAAXmeVsC//NIzcnJ11Eozy/KSVEEAObG5usNAAAA" -d base64 -d gzip
Hello, world!
```

While encoders, decoders and hashers can be used right away, some of the scripts may require additional configuration.
To show all available options of a specific script you can add the ```help``` parameter:
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

To configure a specific script you need to supply the individual options as name-value pairs (e.g. ```search_term="Hello"```):

```
$ dpp "Hello, world!" -s search_and_replace search_term="Hello" replace_term="Hey"
Hey, world!
```

## Contribute

Feel free to open a new ticket for feature requests or bugs. 
Also don't hesitate to issue a pull-request for new features/plugins. Check out the 
[Development Guide](docs/DEVELOPMENT.md)
in order to see how Decoder++ is structured and how easy new features can be added.

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
