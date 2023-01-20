FROM python:3.10-slim as base

# Make sure to call Docker build from parent directory! 
# docker build --progress=plain -t "hmm:Dockerfile" -f valhub/Dockerfile .
ADD valhub /root/valhub


ENV PORT 5001
EXPOSE 5001

RUN apt-get update -qq
# RUN apt-get --assume-yes install python3-pip
RUN apt-get --assume-yes install mariadb-client
RUN mkdir canucme
RUN echo $(ls -a)
RUN apt-get --assume-yes install python3-dev default-libmysqlclient-dev build-essential
RUN python3 -m pip install --upgrade pip
WORKDIR /root/valhub
RUN python3 -m pip install -r requirements.txt

RUN cd ./valhub
RUN python3 manage.py runserver 0.0.0.0:5001