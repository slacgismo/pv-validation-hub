FROM python:3.10-slim as base

# docker build --progress=plain -t "hmm:Dockerfile" -f valhub/Dockerfile .
WORKDIR /root
RUN mkdir admin
WORKDIR /root/admin
COPY . .

ENV PORT 7000
EXPOSE 7000

RUN apt-get update -qq
RUN apt-get install -y libpq-dev python3-psycopg2 curl nano
# RUN apt-get --assume-yes install python3-pip
RUN apt-get --assume-yes install mariadb-client supervisor postgresql-client
RUN apt-get --assume-yes install python3-dev default-libmysqlclient-dev build-essential cmake git
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install -r requirements.txt
# RUN git clone https://github.com/kperrynrel/time-shift-validation-hub.git

ENTRYPOINT ["tail", "-f", "/dev/null"]