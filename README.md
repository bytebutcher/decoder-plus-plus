 # Decoder++

![Decoder++ Logo](decoder-plus-plus/dpp.png)

An extensible application for penetration testers and software developers to decode/encode data into various formats.  


## Usage

Start the Decoder++ GUI:

```bash
python3 dpp.py
```

![Decoder++ Screenshot](images/dpp-screenshot-001.png)

Use the Decoder++ Command Line Interface:

```bash
python3 dpp.py -t "Hello, world!" -e base64 -a sha1
e52d74c6d046c390345ae4343406b99587f2af0d
```

Drop into the Decoder++ Interactive Python Shell:

```bash
python3 dpp.py -i
Decoder++ 0.90
>>> DecoderPlusPlus("Hello, world!").encode().base64().hash().sha1().run()
'e52d74c6d046c390345ae4343406b99587f2af0d'
```

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

## Features

* Graphical User Interface
* Command Line Interface
* Interactive Python Console
* Plugin System
* Cross-Platform-Compatible
* Preinstalled Scripts and Codecs:
    * **Encode/Decode:** Base16, Base32, Base64, Hex, Html, Url, Url+
    * **Hashing:** Keccak256, Md5, RipeMd160, Sha1, Sha224, Sha256, Sha348, Sha512
    * **Scripts:** Caesar, Search and Replace

## Powered By

* PyQt5
* QtAwesome
* QScintilla
