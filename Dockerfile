# Docker file for a slim Ubuntu-based Python3 image

FROM python:latest
LABEL maintainer="cooper@pobox.com"
USER root

# Needed for string substitution
SHELL ["/bin/bash", "-c"]

RUN apt-get -y update

RUN pip3 --no-cache-dir install --upgrade pip setuptools
RUN apt-get -y install build-essential libpoppler-cpp-dev pkg-config python-dev libpoppler-dev

COPY bashrc /etc/bash.bashrc
RUN chmod a+rwx /etc/bash.bashrc

# https://pythonspeed.com/articles/activate-virtualenv-dockerfile/
RUN python -m venv /app/.venv

RUN mkdir -p /app
WORKDIR /app
COPY . /app
RUN source /app/.venv/bin/activate
RUN . /app/.venv/bin/activate && pip install --upgrade pip
RUN . /app/.venv/bin/activate && pip install -r requirements.txt
RUN . /app/.venv/bin/activate && python -m spacy download zh_core_web_sm  # Chinese
RUN . /app/.venv/bin/activate && python -m spacy download da_core_news_sm # Danish
RUN . /app/.venv/bin/activate && python -m spacy download nl_core_news_sm # Dutch
RUN . /app/.venv/bin/activate && python -m spacy download en_core_web_sm  # English
RUN . /app/.venv/bin/activate && python -m spacy download fr_core_news_sm # French
RUN . /app/.venv/bin/activate && python -m spacy download de_core_news_sm # German
RUN . /app/.venv/bin/activate && python -m spacy download el_core_news_sm # Greek
RUN . /app/.venv/bin/activate && python -m spacy download ja_core_news_sm # Japanese
RUN . /app/.venv/bin/activate && python -m spacy download it_core_news_sm # Italian
RUN . /app/.venv/bin/activate && python -m spacy download lt_core_news_sm # Lithuanian
RUN . /app/.venv/bin/activate && python -m spacy download xx_ent_wiki_sm  # Multi-language
RUN . /app/.venv/bin/activate && python -m spacy download nb_core_news_sm # Norwegian Bokmål
RUN . /app/.venv/bin/activate && python -m spacy download pl_core_news_sm # Polish
RUN . /app/.venv/bin/activate && python -m spacy download pt_core_news_sm # Portuguese
RUN . /app/.venv/bin/activate && python -m spacy download ro_core_news_sm # Romanian
RUN . /app/.venv/bin/activate && python -m spacy download es_core_news_sm # Spanish

# Define default command.
CMD ["bash"]

