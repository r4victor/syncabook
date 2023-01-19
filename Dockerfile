FROM python:3.9-slim

RUN apt update -q \
    && apt install --no-install-recommends -yq espeak \
    libespeak-dev \
    ffmpeg

WORKDIR /syncabook
COPY requirements requirements

RUN pip install numpy==1.23.4
RUN pip install pytest==7.1.3
RUN apt install -yq gcc \
    && pip install -r requirements/afaligner.txt \
    && pip install afaligner==0.2.0 \
    && apt remove --purge -yq gcc

RUN pip install -r requirements/base.txt

COPY src src
COPY tests tests
COPY LICENSE MANIFEST.in pytest.ini README.md setup.py ./

RUN pip install .

WORKDIR /
ENTRYPOINT ["syncabook"]
