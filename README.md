 # Decoder++

![Decoder++ Logo](decoder-plus-plus/dpp.png)

An extensible application for penetration testers and software developers to decode/encode data into various formats.  


## Usage

### Graphical User Interface

```bash
python3 dpp.py
```

![Decoder++ Screenshot](images/dpp-screenshot-001.png)

### Command Line Interface

```bash
python3 dpp.py -e base64 -h sha1 "Hello, world!"
e52d74c6d046c390345ae4343406b99587f2af0d
```

### Interactive Python Shell

```bash
python3 dpp.py -i
Decoder++ 0.90
>>> DecoderPlusPlus("Hello, world!").encode().base64().hash().sha1().run()
'e52d74c6d046c390345ae4343406b99587f2af0d'
```

## Features

* Preinstalled Scripts and Codecs:
    * **Encode/Decode:** Base16, Base32, Base64, Hex, Html, Url, Url+
    * **Hashing:** Keccak256, Md5, RipeMd160, Sha1, Sha224, Sha256, Sha348, Sha512
    * **Scripts:** Caesar, Search and Replace
* Plugin System
* Platforms:
    * Windows
    * Linux
    * MAC
* Interfaces:
    * Graphical User Interface
    * Command Line Interface
    * Interactive Python Console    

## Setup

### Manual Installation
```bash
git clone https://github.com/bytebutcher/decoder-plus-plus
cd decoder-plus-plus
pip3 install -r requirements
```

### Automatic Installation
```bash
pip3 install decoder-plus-plus
```

## Advanced Usage

### Command Line Interface
```bash
usage: dpp.py [-?] [-f FILE] [-i] [-e ENCODE] [-d DECODE] [-h HASH]
              [-s SCRIPT [SCRIPT ...]]
              [input]

positional arguments:
  input                 specifies the input-text

optional arguments:
  -?, --help            show this help message and exit
  -f FILE, --file FILE  specifies the input-file
  -i, --interactive     drops into an interactive python shell
  -e ENCODE, --encode ENCODE
                        encodes the input using the specified codec(s).
  -d DECODE, --decode DECODE
                        decodes the input using the specified codec(s)
  -h HASH, --hash HASH  transforms the input using the specified hash-
                        functions
  -s SCRIPT [SCRIPT ...], --script SCRIPT [SCRIPT ...]
                        transforms the input using the specified script
                        (optional arguments)
```

### Interactive Python Console

```python
# Encode / Decode Base64
encoded = DecoderPlusPlus("Hello, world!").encode().base64().run()
decoded = DecoderPlusPlus(encoded).decode().base64().run()
DecoderPlusPlus("Hello, world!").encode().base64().decode().base64().run() == "Hello, world!"

# Hashing
DecoderPlusPlus("Hello, world!").hash().sha1().run()
```

### Plugin Development

To add custom codecs just copy them into the $HOME/.config/dpp/plugins/ folder. 

```python
from core.plugin.abstract_plugin import AbstractPlugin
from core.command import Command

class Plugin(AbstractPlugin):

    def __init__(self, context):
        plugin_name = "URL"
        # plugin_type: Command.Type.DECODER / Command.Type.ENCODER / Command.Type.HASHER / Command.Type.SCRIPT 
        plugin_type = Command.Type.DECODER
        plugin_author = "Your Name"
        plugin_requirements = ["urllib"] # Required Python Libraries
        super().__init__(plugin_name, plugin_type, plugin_author, plugin_requirements)

    def run(self, text):
        # Load the required libraries here ...
        import urllib.parse
        # Run your action ...
        return urllib.parse.unquote(text)
```

## Contribute

Feel free to issue pull-requests for new features/plugins.

## Powered By

* PyQt5
* QtAwesome
* QScintilla
