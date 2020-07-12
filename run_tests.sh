#!/usr/bin/env bash

python3 -m venv ~/.venv
 . ~/.venv/bin/activate && pip3 install --upgrade pip
 . ~/.venv/bin/activate && pip3 install -r requirements.txt
 . ~/.venv/bin/activate && pip3 install pytest
 . ~/.venv/bin/activate && python3 -m spacy download zh_core_web_sm  # Chinese
 . ~/.venv/bin/activate && python3 -m spacy download da_core_news_sm # Danish
 . ~/.venv/bin/activate && python3 -m spacy download nl_core_news_sm # Dutch
 . ~/.venv/bin/activate && python3 -m spacy download en_core_web_sm  # English
 . ~/.venv/bin/activate && python3 -m spacy download fr_core_news_sm # French
 . ~/.venv/bin/activate && python3 -m spacy download de_core_news_sm # German
 . ~/.venv/bin/activate && python3 -m spacy download el_core_news_sm # Greek
 . ~/.venv/bin/activate && python3 -m spacy download ja_core_news_sm # japanese
 . ~/.venv/bin/activate && python3 -m spacy download it_core_news_sm # Italian
 . ~/.venv/bin/activate && python3 -m spacy download lt_core_news_sm # Lithuanian
 . ~/.venv/bin/activate && python3 -m spacy download xx_ent_wiki_sm  # Multi-language
 . ~/.venv/bin/activate && python3 -m spacy download nb_core_news_sm # Norwegian Bokmål
 . ~/.venv/bin/activate && python3 -m spacy download pl_core_news_sm # Polish
 . ~/.venv/bin/activate && python3 -m spacy download pt_core_news_sm # Portuguese
 . ~/.venv/bin/activate && python3 -m spacy download ro_core_news_sm # Romanian
 . ~/.venv/bin/activate && python3 -m spacy download es_core_news_sm # Spanish
 . ~/.venv/bin/activate && py.test --verbose
 . ~/.venv/bin/activate
