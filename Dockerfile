FROM python:3.9-slim

RUN apt update -q \
    && apt install --no-install-recommends -yq espeak \
    libespeak-dev \
    ffmpeg

RUN pip install numpy==1.21.2
RUN pip install pytest==6.2.5
RUN apt install -yq gcc \
    && pip install afaligner==0.1.4 \
    && apt remove --purge -yq gcc

WORKDIR /syncabook
COPY src src
COPY tests tests
COPY LICENSE MANIFEST.in pytest.ini README.md setup.py ./

RUN pip install .

WORKDIR /
ENTRYPOINT ["syncabook"]