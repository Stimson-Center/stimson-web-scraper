# Docker file for a slim Ubuntu-based Python3 image

FROM python:latest
LABEL maintainer="cooper@pobox.com"
USER root

# Needed for string substitution
SHELL ["/bin/bash", "-c"]

RUN apt-get -y update

# See http://bugs.python.org/issue19846
ENV LANG C.UTF-8

RUN pip3 --no-cache-dir install --upgrade pip setuptools
RUN apt-get -y install build-essential libpoppler-cpp-dev pkg-config python-dev libpoppler-dev

COPY bashrc /etc/bash.bashrc
RUN chmod a+rwx /etc/bash.bashrc

ENV TZ=UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt-get install -y tzdata

RUN pip3 --no-cache-dir install virtualenv

WORKDIR /mnt
RUN virtualenv venv
RUN source venv/bin/activate
COPY requirements.txt .
RUN pip3 --no-cache-dir install -r requirements.txt
COPY .GOOGLE_APPLICATION_CREDENTIALS.json .
RUN export GOOGLE_APPLICATION_CREDENTIALS=/mnt/.GOOGLE_APPLICATION_CREDENTIALS.json

# Define default command.
CMD ["bash"]

