# -*- coding: utf-8 -*-

import json

from scraper.google_customsearch import GoogleCustomSearch
from scraper import Article
from scraper.configuration import Configuration
from bs4 import BeautifulSoup

# Check if your url end-point actively prevents programmatic access.
#
# Take a look at the robots.txt file in the root directory of a website: http://myweburl.com/robots.txt.
#
# If it contains text that looks like this : User-agent: * Disallow: /
#
# This site doesn’t like and want scraping. This gives you the same dreaded error 54, connection reset by the peer.

def test_google_customsearch():

    google_customsearch = GoogleCustomSearch()
    number_of_search_results_return = 10
    google_customsearch_urls = google_customsearch.get_search_urls("Energy AND Investment AND Thailand",
                                                                   number_of_search_results_return)
    assert len(google_customsearch_urls) == number_of_search_results_return
    print(json.dumps(google_customsearch_urls, sort_keys=True, indent=4))
    # [
    #     "http://scholar.google.com/citations?user=A5NhLJkAAAAJ&hl=en",
    #     "http://scholar.google.com/citations?user=6wm6PgUAAAAJ&hl=en",
    #     "http://scholar.google.com/citations?user=QBTuDCMAAAAJ&hl=en",
    #     "http://scholar.google.com/citations?user=RrvwWKMAAAAJ&hl=en",
    #     "http://scholar.google.com/citations?user=WE5-W-MAAAAJ&hl=en",
    #     "http://scholar.google.com/citations?user=-oofbb8AAAAJ&hl=en",
    #     "http://scholar.google.com/citations?user=9ID33ekAAAAJ&hl=en",
    #     "http://scholar.google.com/citations?user=Sc9KjDQAAAAJ&hl=en",
    #     "http://scholar.google.com/citations?user=Zc3O_PIAAAAJ&hl=en",
    #     "http://scholar.google.com/citations?user=ZvKEMG4AAAAJ&hl=en"
    # ]

    # google_customsearch_urls = ['https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q=Energy+AND+Investment+AND+Thailand&btnG=']

    google_scholar_list = google_customsearch.get_scholar_list(google_customsearch_urls)
    assert len(google_scholar_list)
    # [
    #   {'title': 'The rites of the child: Global discourses of youth and reintegrating child soldiers in Sierra Leone',
    #   'link': 'https://scholar.google.com/scholar?oi=bibs&hl=en&oe=ASCII&cites=17455492728027388341'},
    #  {'title': 'Childhood deployed: Remaking child soldiers in Sierra Leone',
    #   'link': 'https://scholar.google.com/scholar?oi=bibs&hl=en&oe=ASCII&cites=1562197344164485303'},
    #  {'title': 'The social and cultural context of child soldiering in Sierra Leone',
    #   'link': 'https://scholar.google.com/scholar?oi=bibs&hl=en&oe=ASCII&cites=2801456600159347306,2342876692076362465'},
    #  {'title': 'Conflicted childhoods: Fighting over child soldiers in Sierra Leone',
    #   'link': 'https://scholar.google.com/scholar?oi=bibs&hl=en&oe=ASCII&cites=5166536830157164695'},
    #  {'title': "Les filles-soldats: Trajectoires d'apres-guerre en Sierra Leone",
    #   'link': 'https://scholar.google.com/scholar?oi=bibs&hl=en&oe=ASCII&cites=4256386125334217038,3443140639708692101'},
    #  {'title': 'Youth music and politics in post-war Sierra Leone',
    #   'link': 'https://scholar.google.com/scholar?oi=bibs&hl=en&oe=ASCII&cites=7479290573901504471'},
    #  {'title': 'Fears and misperceptions of the Ebola response system during the 2014-2015 outbreak in Sierra Leone',
    #   'link': 'https://scholar.google.com/scholar?oi=bibs&hl=en&oe=ASCII&cites=4234978055575867852'},
    #  {'title': 'Conflict resolution and peace education in Africa',
    #   'link': 'https://scholar.google.com/scholar?oi=bibs&hl=en&oe=ASCII&cites=2767737970396513929'},
    #  {'title': 'Introduction to Special Issue:  Everyday Life in Postwar Sierra Leone',
    #   'link': 'https://scholar.google.com/scholar?oi=bibs&hl=en&oe=ASCII&cites=7566681778708760393,12152544947076506357'},
    #  {'title': 'Globalizing Child Soldiers in Sierra Leone',
    #   'link': 'https://scholar.google.com/scholar?oi=bibs&hl=en&oe=ASCII&cites=10814473918134518824,3375434679098497636'},
    #  {'title': '"We Know Who is Eating the Ebola Money!": Corruption, the State, and the Ebola Response',
    #   'link': 'https://scholar.google.com/scholar?oi=bibs&hl=en&oe=ASCII&cites=9128440790715340524'},
    #  {'title': "The real and symbolic importance of food in war: hunger pains and big men's bellies in Sierra Leone",
    #   'link': 'https://scholar.google.com/scholar?oi=bibs&hl=en&oe=ASCII&cites=9905123341282723924'},
    #  {'title': 'Human rights in Sierra Leone: A research report to Search for Common Ground',
    #   'link': 'https://scholar.google.com/scholar?oi=bibs&hl=en&oe=ASCII&cites=13107069810915134828,15377318137642268427,3454836454865524689'},
    #  {'title': 'Understanding Sierra Leonean and Liberian teachers’ views on discussing past wars in their classrooms',
    #   'link': 'https://scholar.google.com/scholar?oi=bibs&hl=en&oe=ASCII&cites=12949722154100302826'},
    #  {'title': 'Effects in post-conflict West Africa of teacher training for refugee women',
    #   'link': 'https://scholar.google.com/scholar?oi=bibs&hl=en&oe=ASCII&cites=8801945510765123587'},
    #  {'title': "Are 'Child Soldiers' in Sierra Leone a New Phenomenon?",
    #   'link': 'https://scholar.google.com/scholar?oi=bibs&hl=en&oe=ASCII&cites=3445296365394933234'},
    #  {'title': 'The Ebola Virus and the Vampire State',
    #   'link': 'https://scholar.google.com/scholar?oi=bibs&hl=en&oe=ASCII&cites=11108937194783384380'},
    #  {'title': '“Helping our children will help in the reconstruction of our country”: Repatriated Refugee Teachers in post-conflict Sierra Leone and Liberia',
    #      'link': 'https://scholar.google.com/scholar?oi=bibs&hl=en&oe=ASCII&cites=12844568485919732454'},
    #  {'title': 'Educated in War:  The Rehabilitation of Child Soldiers in Sierra Leone',
    #   'link': 'https://scholar.google.com/scholar?oi=bibs&hl=en&oe=ASCII&cites=6231157277439024114'},
    #  {'title': 'Producing ebola: creating knowledge in and about an epidemic',
    #   'link': 'https://scholar.google.com/scholar?oi=bibs&hl=en&oe=ASCII&cites=10199900368582209076'}
    # ]
    articles = []
    for google_scholar in google_scholar_list:
        google_customsearch = GoogleCustomSearch()
        article = google_customsearch.get_article(google_scholar['link'], language='en')
        articles.append(article)
    assert len(articles) == len(google_scholar_list)


def test_google_book():
    config = Configuration()
    config.memoize_articles = False
    config.use_canonical_link = True
    pdf_defaults = {
        # "application/pdf": "%PDF-",
        # "application/x-pdf": "%PDF-",
        "application/x-bzpdf": "%PDF-",
        "application/x-gzpdf": "%PDF-"
    }
    urls = [
        "https://books.google.com/books?id=HiJNbEy5f70C&pg=PA332&lpg=PA332&dq=extract+author+in+plain+text+document&source=bl&ots=yuwD1QlvQa&sig=ACfU3U16y90fka4nbXnt8RCJuV9wmQoilQ&hl=en&sa=X&ved=2ahUKEwj_rKKD-uDoAhVRFjQIHWEnCmUQ6AEwFHoECBcQMg#v=onepage&q=extract%20author%20in%20plain%20text%20document&f=false"
    ]
    for url in urls:
        article = Article(url.rstrip(),
                          request_timeout=config.request_timeout,
                          config=config,
                          ignored_content_types_defaults=pdf_defaults)
        article.build()
        assert article.canonical_link== article.url

#
# def test_google_phantomjs():
#     from selenium import webdriver
#     driver = webdriver.PhantomJS()
#     driver.get('https://scholar.google.com/scholar?oi=bibs&hl=en&oe=ASCII&cites=17455492728027388341')
#     p_element = driver.find_elements_by_class_name('gs_a')
#     print(p_element.text)
#     x = driver.page_source


def test_chromium():
    from scraper.chromium import get_page_source
    x = get_page_source('https://scholar.google.com/scholar?oi=bibs&hl=en&oe=ASCII&cites=17455492728027388341')
    soup = BeautifulSoup(x, 'html.parser')
    y = soup.findAll(name='div', attrs={'class': 'gs_a'})
    pass
