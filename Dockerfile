FROM python:3.8

WORKDIR /syncabook

COPY syncabook syncabook
COPY setup.py setup.py

RUN apt-get update && \
    apt-get install -y espeak \
    libespeak-dev \
    ffmpeg

RUN pip install numpy
RUN pip install afaligner

RUN python setup.py sdist && \
    pip install dist/syncabook*.tar.gz

ENTRYPOINT [ "syncabook" ]