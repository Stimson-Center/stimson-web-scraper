import json
import os

import requests
from bs4 import BeautifulSoup
# https://preslav.me/2019/01/09/dotenv-files-python/
from dotenv import load_dotenv
from fake_useragent import UserAgent
from googleapiclient.discovery import build  # Import the library
from scraper import Article


# https://towardsdatascience.com/current-google-search-packages-using-python-3-7-a-simple-tutorial-3606e459e0d4
class GoogleCustomSearch:
    # Get environment variables
    load_dotenv()
    api_key = os.getenv('GOOGLE_SECRET_API_KEY')
    cse_id = os.getenv('GOOGLE_SECRET_CUSTOM_SEARCH_ID')
    # https://www.pingshiuanchua.com/blog/post/scraping-search-results-from-google-search
    ua = UserAgent()

    def get_search_urls(self, query, number_of_search_results_return):
        # type: (str, int) -> list

        """Google Custom Search enables you to create a search engine for your website, your blog, or a collection
           of websites. You can configure your engine to search both web pages and images

        :param query: data with coordinates
            :type:string
            :example:
                "child AND soldiers"
        :param number_of_search_results_return: 
            :type: integer
            :example:
                a value [1..10]
        :return: list of urls
        """
        query_service = build("customsearch", "v1", developerKey=self.api_key)
        kwargs = {
            'num': number_of_search_results_return
        }
        # https://developers.google.com/custom-search/v1/cse/list
        query_results = query_service.cse().list(q=query,  # Query
                                                 cx=self.cse_id,  # CSE ID
                                                 **kwargs
                                                 ).execute()
        my_google_urls = []
        for result in query_results['items']:
            my_google_urls.append(result['link'])
        return my_google_urls

    #  <tr class="gsc_a_tr">,
    #     <td class="gsc_a_t">,
    #        <a href="javascript:void(0)"
    #           data-href="/citations?view_op=view_citation&amp;hl=en&amp;user=A5NhLJkAAAAJ&amp;citation_for_view=A5NhLJkAAAAJ:TQgYirikUcIC"
    #           class="gsc_a_at">The rites of the child: Global discourses of youth and reintegrating child soldiers in Sierra Leone</a>,
    #        <div class="gs_gray">S Shepler</div>,
    #        <div class="gs_gray">Journal of Human Rights 4 (2), 197-211<span class="gs_oph">, 2005</span></div>,
    #     </td>,
    #     <td class="gsc_a_c"><a href="https://scholar.google.com/scholar?oi=bibs&amp;hl=en&amp;cites=17455492728027388341"
    #                            class="gsc_a_ac gs_ibl">156</a>
    #     </td>,
    #     <td class="gsc_a_y"><span class="gsc_a_h gsc_a_hc gs_ibl">2005</span></td>,
    #  </tr>,
    def get_scholar_list(self, google_search_urls):
        # type: (list) -> list
        sites = list()

        for google_search_url in google_search_urls:
            response = requests.get(google_search_url, headers={'User-Agent': self.ua.random})
            soup = BeautifulSoup(response.text, 'html.parser')
            # https://www.pingshiuanchua.com/blog/post/scraping-search-results-from-google-search
            for tr in soup.find_all('tr', {'class': 'gsc_a_tr'}):
                # Checks if each element is present, else, raise exception
                try:
                    td = tr.find('td', attrs={'class': 'gsc_a_t'})
                    title = td.find('a', href=True).get_text()

                    td = tr.find('td', attrs={'class': 'gsc_a_c'})
                    link = td.find('a', href=True)

                    # Check to make sure everything is present before appending to lists
                    if link != '' and link['href'] != '' and title != '':
                        sites.append({'title': title, 'link': link['href']})
                # Next loop if one element is not present
                except Exception as ex:
                    print(json.dumps(ex, sort_keys=True, indent=4))

            for h3 in soup.find_all('h3', {'class': 'gs_rt'}):
                try:
                    a = h3.find('a', href=True)
                    title = a.get_text()
                    link = a.attrs

                    # for tag in soup.find_all("meta"):
                    #     if tag.get("property", None) == "og:title":
                    #         x = tag.get("content", None)
                    #         print(tag.get("content", None))
                    #     elif tag.get("property", None) == "og:url":
                    #         x = tag.get("content", None)
                    #         print(tag.get("content", None))
                    # Check to make sure everything is present before appending to lists
                    if link != '' and link['href'] != '' and title != '':
                        sites.append({'title': title, 'link': link['href']})
                # Next loop if one element is not present
                except Exception as ex:
                    print(json.dumps(ex, sort_keys=True, indent=4))

        return sites

    def get_article(self, url, language='en'):
        response = requests.get(url, headers={'User-Agent': self.ua.random})
        soup = BeautifulSoup(response.text, 'lxml')
        article = Article(url, language=language)
        article.build()
        if not article.authors:
            x = response.text.find('"authors":[{"name":')
            if x:
                a = response.text[x+10:]
                y = a.find(']')
                a = a[:y+1]
                authors = json.loads(a)
                for author in authors:
                    article.authors.append(author['name'])
        return article
