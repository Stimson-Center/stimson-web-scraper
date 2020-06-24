#!/usr/bin/env bash

pip3 install -r requirements.txt
python3 -m spacy download zh_core_web_sm  # Chinese
python3 -m spacy download da_core_news_sm # Danish
python3 -m spacy download nl_core_news_sm # Dutch
python3 -m spacy download en_core_web_sm  # English
python3 -m spacy download fr_core_news_sm # French
python3 -m spacy download de_core_news_sm # German
python3 -m spacy download el_core_news_sm # Greek
python3 -m spacy download it_core_news_sm # Italian
python3 -m spacy download ja_core_news_sm # Japanese
python3 -m spacy download lt_core_news_sm # Lithuanian
python3 -m spacy download xx_ent_wiki_sm  # Multi-language
python3 -m spacy download nb_core_news_sm # Norwegian Bokmål
python3 -m spacy download pl_core_news_sm # Polish
python3 -m spacy download pt_core_news_sm # Portuguese
python3 -m spacy download ro_core_news_sm # Romanian
python3 -m spacy download es_core_news_sm # Spanish
