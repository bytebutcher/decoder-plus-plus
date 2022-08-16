FROM ubuntu:22.04
LABEL maintainer="bytebutcher"
RUN apt-get update && apt-get install -y python3 python3-pip git
RUN apt-get install -y libqt6core6 libqt6network6 libqt6openglwidgets6 libqt6widgets6 qt6-qpa-plugins
RUN apt-get install -y libgl1 libxcb-xinerama0
COPY / /app
RUN pip3 install --upgrade pip && pip3 install /app[qt6]
ENV QT_QPA_PLATFORM_PLUGIN_PATH=/usr/lib/x86_64-linux-gnu/qt6/plugins/platforms/
CMD ["dpp"]
