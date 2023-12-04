FROM python:3.10-slim as base

# docker build --progress=plain -t "hmm:Dockerfile" -f valhub/Dockerfile .
WORKDIR /root
# RUN mkdir -p .aws
# COPY .aws /root/.aws
RUN mkdir valhub
WORKDIR /root/valhub
COPY . .

# Set Django admin username, password, and other environment variables
ARG admin_username
ARG admin_password
ARG admin_email
ARG djangosk

ENV DJANGO_SUPERUSER_USERNAME=$admin_username
ENV DJANGO_SUPERUSER_PASSWORD=$admin_password
ENV DJANGO_SUPERUSER_EMAIL=$admin_email
ENV DJANGO_SECRET_KEY=${djangosk}
ENV PORT 8005

RUN apt-get update -qq
RUN apt-get install -y libpq-dev python3-psycopg2
# RUN apt-get --assume-yes install python3-pip
RUN apt-get --assume-yes install mariadb-client supervisor postgresql-client 
RUN apt-get --assume-yes install python3-dev default-libmysqlclient-dev build-essential
RUN python3 -m pip install --upgrade pip
WORKDIR /root/valhub
RUN python3 -m pip install -r requirements.txt

RUN cd ./valhub
RUN python3 manage.py makemigrations
RUN python3 manage.py collectstatic
CMD ["/usr/bin/supervisord", "-c", "/root/valhub/supervisord.conf"]
