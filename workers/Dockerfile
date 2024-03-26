FROM python:3.11-slim as base

# docker build --progress=plain -t "hmm:Dockerfile" -f valhub/Dockerfile .
WORKDIR /root
RUN mkdir worker
WORKDIR /root/worker
COPY . .

ENV PORT 8500
EXPOSE 8500
EXPOSE 65535

RUN apt-get update -qq
RUN apt-get install -y libpq-dev python3-psycopg2 curl nano
# RUN apt-get --assume-yes install python3-pip
RUN apt-get --assume-yes install mariadb-client supervisor postgresql-client libopenblas-dev
RUN apt-get --assume-yes install python3-dev default-libmysqlclient-dev build-essential cmake git
WORKDIR /root
WORKDIR /root/worker
RUN python3 -m pip install --upgrade pip
WORKDIR /root/worker
RUN python3 -m pip install -r requirements.txt --timeout=1000

CMD ["/bin/sh", "/root/worker/docker-entrypoint.sh"]