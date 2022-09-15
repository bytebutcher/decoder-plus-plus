FROM ubuntu:18.04
LABEL maintainer="bytebutcher"
RUN apt-get update && apt-get install -y python3.8 python3-pip git
RUN apt-get install -y qt5-default
RUN apt-get install -y libgl1 libxcb-xinerama0
COPY / /app
# Upgrading pip manually is usually not recommended since this may 
# break the system. However, to install PyQt5 a later version of 
# pip is required.
RUN pip3 install --upgrade pip && pip3 install /app[qt5] /app[extras]
CMD ["dpp"]
