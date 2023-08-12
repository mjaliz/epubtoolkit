FROM python:3.10.12

RUN apt update -q \
    && apt install --no-install-recommends -yq espeak \
    libespeak-dev \
    ffmpeg

RUN pip install 'fastapi[all]'
RUN pip install pandas
RUN pip install beautifulsoup4
RUN pip install numpy
RUN pip install aeneas
RUN pip install afaligner
RUN pip install -U spacy
RUN python3 -m spacy download en_core_web_trf
COPY ./src /src