# Decoder++ Installation Guide

The following sections provide additional information about how Decoder++ can be installed on various Systems.

## Ubuntu

### Qt6
```bash
apt-get update
apt-get install -y python3 python3-pip git \
  libqt6core6 libqt6network6 libqt6openglwidgets6 libqt6widgets6 qt6-qpa-plugins \
  libgl1 libxcb-xinerama0
git clone https://github.com/bytebutcher/decoder-plus-plus/
cd decoder-plus-plus
pip3 install --upgrade pip && pip3 install decoder-plus-plus[qt6]
```

### Qt5
```bash
apt-get update
apt-get install -y python3 python3-pip git qt5-default libgl1 libxcb-xinerama0
git clone https://github.com/bytebutcher/decoder-plus-plus/
cd decoder-plus-plus
pip3 install --upgrade pip && pip3 install decoder-plus-plus[qt5]
```

## Git

### Qt6
```bash
git clone https://github.com/bytebutcher/decoder-plus-plus
pip3 install decoder-plus-plus/.[qt6]
```

### Qt5
```bash
git clone https://github.com/bytebutcher/decoder-plus-plus
pip3 install decoder-plus-plus/.[qt5]
```

## Docker container

### Qt6
```bash
git clone https://github.com/bytebutcher/decoder-plus-plus
cd decoder-plus-plus/docker
bash docker-build-dpp qt6 && bash docker-run-dpp qt6
```

### Qt5
```bash
git clone https://github.com/bytebutcher/decoder-plus-plus
cd decoder-plus-plus/docker
bash docker-build-dpp qt5 && bash docker-run-dpp qt5
```