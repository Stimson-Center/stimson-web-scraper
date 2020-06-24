stimson-web-scraper
===================

Scrapes and crawls websites for textual data and urls in any ISO language

 
Table of Contents
=================

  * [Getting Started on Mac OS](#getting-started-on-mac-os)
  * [Install Desktop tools](#install-desktop-tools)
     * [Download GitHub desktop](#download-github-desktop)
     * [Optionally Download PyCharm Professional](#optionally-download-pycharm-professional)
  * [Git on the Server Generating Your SSH Public Key](#git-on-the-server-generating-your-ssh-public-key)
  * [get project source code](#get-project-source-code)
  * [Getting started with Web Scraping](#getting-started-with-web-scraping)
     * [Execute test suite to ensure environmental integrity](#execute-test-suite-to-ensure-environmental-integrity)
     * [Execute as an Python3 executable](#execute-as-an-python3-executable)
     * [Execute as an Python3 package](#execute-as-an-python3-package)
        * [Get an article from a Website Page](#get-an-article-from-a-website-page)
        * [Foreign Language Websites](#foreign-language-websites)
        * [Extract text from Adobe PDF files in any ISO language](#extract-text-from-adobe-pdf-files-in-any-iso-language)
        * [Get all of the URLs within a Website](#get-all-of-the-urls-within-a-website)
        * [Get a Wikipedia Article including embedded tables](#get-a-wikipedia-article-including-embedded-tables)
  * [Optionally Setting up a Docker environment](#optionally-setting-up-a-docker-environment)
* [Contributing](#contributing)
   
## Getting Started on Mac OS

In a terminal window:

```bash
    ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
    xcode-select --install
    brew update
    brew upgrade

    git --version
    git version 2.24.1 (Apple Git-126)

    brew install python3
    python3 --version
        Python 3.7.7

    pip3 install -U pytest
    py.test --version
	This is pytest version 5.4.1, imported from /usr/local/lib/python3.7/site-packages/pytest/__init__.py
```

## Install Desktop tools

### Download GitHub desktop

```bash
    open https://desktop.github.com
```

### Optionally Download PyCharm Professional

```bash
    open https://www.jetbrains.com/pycharm/download
```

## Git on the Server Generating Your SSH Public Key

[Reference](https://git-scm.com/book/en/v2/Git-on-the-Server-Generating-Your-SSH-)

```bash
open https://help.github.com/articles/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent/
```

```
check to make sure your github key has been added to the ssh-agent list.  Here's my ~/.ssh/config file

 Host github.com github
     IdentityFile ~/.ssh/id_rsa
     IdentitiesOnly yes
     UseKeyChain yes
     AddKeysToAgent yes
```

```bash
    cd ~/.ssh
    ssh-keygen -o
    ssh-add -K ~/.ssh/id_rsa
    ssh-add -L
```

## get project source code

```bash
    cd ~
    git clone https://github.com/Stimson-Center/stimson-web-scraper.git
```

## Getting started with Web Scraping

### Execute test suite to ensure environmental integrity

```bash
    cd ~/stimson-web-scraper
    ./start.sh
    export GOOGLE_APPLICATION_CREDENTIALS=.GOOGLE_APPLICATION_CREDENTIALS.json
    py.test --verbose
```

### Execute as an Python3 executable

```bash
    cd ~/stimson-web-scraper/scraper
    ./start.sh
    export GOOGLE_APPLICATION_CREDENTIALS=.GOOGLE_APPLICATION_CREDENTIALS.json
    ./cli.py -u https://www.yahoo.com -l en
```

### Execute as an Python3 package

#### Get an article from a Website Page

```python
import datetime
from scraper import Article

url = 'http://fox13now.com/2013/12/30/new-year-new-laws-obamacare-pot-guns-and-drones/'
article = Article(url)
article.build()

# Access Data scraped from this web site page

article.authors
['Leigh Ann Caldwell', 'John Honway']

article.publish_date
datetime.datetime(2013, 12, 30, 0, 0)

article.text
'Washington (CNN) -- Not everyone subscribes to a New Year's resolution...'

article.top_image
'http://someCDN.com/blah/blah/blah/file.png'

article.movies
['http://youtube.com/path/to/link.com', ...]

article.keywords
['New Years', 'resolution', ...]

article.summary
'The study shows that 93% of people ...'

article.html
'<!DOCTYPE HTML><html itemscope itemtype="http://...'
```

#### Foreign Language Websites

scraper can extract and detect languages *seamlessly*.
If no language is specified, Newspaper will attempt to auto detect a language.
If you are certain that an from scraper then you can specify it by two letter ISO code

To see list of supported ISO languages
```python
import scraper
scraper.get_languages()
```
```
Your available languages are:
input code         full name
af			  Afrikaans
ar			  Arabic
be			  Belarusian
bg			  Bulgarian
bn			  Bengali
br			  Portuguese, Brazil
ca			  Catalan
cs			  Czech
da			  Danish
de			  German
el			  Greek
en			  English
eo			  Esperanto
es			  Spanish
et			  Estonian
eu			  Basque
fa			  Persian
fi			  Finnish
fr			  French
ga			  Irish
gl			  Galician
gu			  Gujarati
ha			  Hausa
he			  Hebrew
hi			  Hindi
hr			  Croatian
hu			  Hungarian
hy			  Armenian
id			  Indonesian
it			  Italian
ja			  Japanese
ka			  Georgian
ko			  Korean
ku			  Kurdish
la			  Latin
lt			  Lithuanian
lv			  Latvian
mk			  Macedonian
mr			  Marathi
ms			  Malay
nb			  Norwegian (Bokmål)
nl			  Dutch
no			  Norwegian
np			  Nepali
pl			  Polish
pt			  Portuguese
ro			  Romanian
ru			  Russian
sk			  Slovak
sl			  Slovenian
so			  Somali
sr			  Serbian
st			  Sotho, Southern
sv			  Swedish
sw			  Swahili
ta			  Tamil
th			  Thai
tl			  Tagalog
tr			  Turkish
uk			  Ukrainian
ur			  Urdu
vi			  Vietnamese
yo			  Yoruba
zh			  Chinese
zu			  Zulu
```

```python
import scraper
scraper.get_available_languages()

{'ar': 'Arabic', 'af': 'Afrikaans', 'be': 'Belarusian', 'bg': 'Bulgarian', 'bn': 'Bengali', 'br': 'Portuguese, Brazil', 'ca': 'Catalan', 'cs': 'Czech', 'da': 'Danish', 'de': 'German', 'el': 'Greek', 'en': 'English', 'eo': 'Esperanto', 'es': 'Spanish', 'et': 'Estonian', 'eu': 'Basque', 'fa': 'Persian', 'fi': 'Finnish', 'fr': 'French', 'ga': 'Irish', 'gl': 'Galician', 'gu': 'Gujarati', 'ha': 'Hausa', 'he': 'Hebrew', 'hi': 'Hindi', 'hr': 'Croatian', 'hu': 'Hungarian', 'hy': 'Armenian', 'id': 'Indonesian', 'it': 'Italian', 'ja': 'Japanese', 'ka': 'Georgian', 'ko': 'Korean', 'ku': 'Kurdish', 'la': 'Latin', 'lt': 'Lithuanian', 'lv': 'Latvian', 'mk': 'Macedonian', 'mr': 'Marathi', 'ms': 'Malay', 'nb': 'Norwegian (Bokmål)', 'nl': 'Dutch', 'no': 'Norwegian', 'np': 'Nepali', 'pl': 'Polish', 'pt': 'Portuguese', 'ro': 'Romanian', 'ru': 'Russian', 'sk': 'Slovak', 'sl': 'Slovenian', 'so': 'Somali', 'sr': 'Serbian', 'st': 'Sotho, Southern', 'sv': 'Swedish', 'sw': 'Swahili', 'ta': 'Tamil', 'th': 'Thai', 'tl': 'Tagalog', 'tr': 'Turkish', 'uk': 'Ukrainian', 'ur': 'Urdu', 'vi': 'Vietnamese', 'yo': 'Yoruba', 'zh': 'Chinese', 'zu': 'Zulu'}

```
To import an article in a supported ISO language
 
```python
from scraper import Article
url = 'http://www.bbc.co.uk/zhongwen/simp/chinese_news/2012/12/121210_hongkong_politics.shtml'

article = Article(url, language='zh') # Chinese
article.build()

print(article.text[:150])

香港行政长官梁振英在各方压力下就其大宅的违章建
筑（僭建）问题到立法会接受质询，并向香港民众道歉。
梁振英在星期二（12月10日）的答问大会开始之际
在其演说中道歉，但强调他在违章建筑问题上没有隐瞒的
意图和动机。 一些亲北京阵营议员欢迎梁振英道歉，
且认为应能获得香港民众接受，但这些议员也质问梁振英有

print(article.title)
港特首梁振英就住宅违建事件道歉


# If you are certain that an from scraper import Article

url = 'http://www.bbc.co.uk/zhongwen/simp/chinese_news/2012/12/121210_hongkong_politics.shtml'

article = Article(url, language='zh') # Chinese
article.build()

print(article.text[:150])
香港行政长官梁振英在各方压力下就其大宅的违章建
筑（僭建）问题到立法会接受质询，并向香港民众道歉。
梁振英在星期二（12月10日）的答问大会开始之际
在其演说中道歉，但强调他在违章建筑问题上没有隐瞒的
意图和动机。 一些亲北京阵营议员欢迎梁振英道歉，
且认为应能获得香港民众接受，但这些议员也质问梁振英有

print(article.title)
港特首梁振英就住宅违建事件道歉

```

#### Extract text from Adobe PDF files in any ISO language

```python
from scraper import Article
url = "http://tpch-th.listedcompany.com/misc/ShareholderMTG/egm201701/20170914-tpch-egm201701-enc02-th.pdf"
article = Article(url=url, language='th')
article.build()
print(article.text)
```

#### Get all of the URLs within a Website

```python
from scraper import Sources
url = "https://www.cnn.com"
sources = Sources(url)

print(sources.get_articles())
print(sources.get_categories)
```

#### Get a Wikipedia Article including embedded tables

```python
from scraper import Article
url = "https://en.wikipedia.org/wiki/International_Phonetic_Alphabet_chart_for_English_dialects"
article = Article(url=url, language='en')
article.build()

print(article.text)
print(article.tables)
```

## Optionally Setting up a Docker environment
        
```bash
	brew install docker
	docker --version
    cd ~/stimson-web-scraper
    ./run_docker.sh
```
You will be put into the virtual machine:

(venv) tf-docker /mnt >


```bash
    virtualenv venv
    source venv/bin/activate
    export GOOGLE_APPLICATION_CREDENTIALS=.GOOGLE_APPLICATION_CREDENTIALS.json
    ./start.sh
    py.test --verbose 
```

For more details see:

[Docker Tutorial](https://github.com/praktikos/stimson-web-scraper/blob/master/DOCKER.md)


# Contributing
   * Fork it
   * Create your feature branch (`git checkout -b your_github_name-feature`)
   * Commit your changes (`git commit -am 'Added some feature'`)
   * Make sure to add tests for it. This is important so we don't break it in a future version unintentionally.
   * [File an Issue](https://github.com/https://github.com/Stimson-Center/stimson-web-scraper/issues)
   * Push to the branch (`git push origin your_github_name-feature`)
   * Create new Pull Request
