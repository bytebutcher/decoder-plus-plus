FROM ubuntu:18.04
LABEL maintainer="bytebutcher"
RUN apt-get update && apt-get install -y python3 python3-pip git
RUN apt-get install -y qt5-default
RUN apt-get install -y libgl1 libxcb-xinerama0
COPY / /app
RUN pip3 install --upgrade pip && pip3 install /app[qt5]
CMD ["dpp"]
