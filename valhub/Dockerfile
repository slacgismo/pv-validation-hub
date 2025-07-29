FROM python:3.11-slim

# docker build --progress=plain -t "hmm:Dockerfile" -f valhub/Dockerfile .
WORKDIR /root
# RUN mkdir -p .aws
# COPY .aws /root/.aws
RUN mkdir valhub
WORKDIR /root/valhub

VOLUME /root/valhub

COPY . .

RUN chmod +x /root/valhub/startup.sh

# Set Django admin username, password, and other environment variables
ENV PORT=8005

RUN apt-get update -qq
RUN apt-get install -y libpq-dev python3-psycopg2
# RUN apt-get --assume-yes install python3-pip
RUN apt-get --assume-yes install mariadb-client supervisor postgresql-client 
RUN apt-get --assume-yes install python3-dev default-libmysqlclient-dev build-essential pkg-config
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install -r requirements.txt

CMD ["/bin/bash", "/root/valhub/startup.sh"]
