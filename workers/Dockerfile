FROM python:3.11-slim

ARG DOCKER_HOST_VOLUME_DATA_DIR=${DOCKER_HOST_VOLUME_DATA_DIR}
ARG DOCKER_HOST_VOLUME_RESULTS_DIR=${DOCKER_HOST_VOLUME_RESULTS_DIR}

WORKDIR /root/worker
COPY . .

RUN mkdir -p /root/worker/logs

ENV DOCKER_HOST_VOLUME_DATA_DIR=${DOCKER_HOST_VOLUME_DATA_DIR}
ENV DOCKER_HOST_VOLUME_RESULTS_DIR=${DOCKER_HOST_VOLUME_RESULTS_DIR}

ENV PORT 8500
EXPOSE 8500
EXPOSE 65535

RUN apt-get update -qq
RUN apt-get install -y libpq-dev python3-psycopg2 curl nano
# RUN apt-get --assume-yes install python3-pip
RUN apt-get --assume-yes install mariadb-client supervisor postgresql-client libopenblas-dev
RUN apt-get --assume-yes install python3-dev default-libmysqlclient-dev build-essential cmake git libhdf5-dev pkg-config
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install -r requirements.txt --timeout=1000

CMD ["/bin/sh", "/root/worker/docker-entrypoint.sh"]