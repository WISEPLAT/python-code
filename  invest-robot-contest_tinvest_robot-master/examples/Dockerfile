FROM python:3.8

RUN apt-get -y update
RUN apt-get -y install libc-dev
RUN apt-get -y install build-essential

WORKDIR /project

COPY requirements.txt ./
RUN pip install --upgrade pip -r requirements.txt; exit 0

COPY fetch.py trade.py ./