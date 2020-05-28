FROM python:3.8

WORKDIR /syncabook

COPY syncabook syncabook
COPY setup.py setup.py

RUN python setup.py sdist && \
    pip install dist/syncabook*.tar.gz

RUN apt-get update && \
    apt-get install espeak -y && \
    apt-get install libespeak-dev && \
    apt-get install ffmpeg -y

RUN pip install numpy

RUN git clone https://github.com/r4victor/afaligner && \
    cd afaligner && \
    python setup.py sdist && \
    pip install dist/afaligner*.tar.gz

ENTRYPOINT [ "syncabook" ]