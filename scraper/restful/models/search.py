import os

# https://preslav.me/2019/01/09/dotenv-files-python/
from dotenv import load_dotenv
from flask import request
from flask_restful import Resource
from googleapiclient.discovery import build

from ..constants import countries, file_types, languages

__title__ = 'stimson-web-scraper'
__author__ = 'Alan S. Cooper'
__license__ = 'MIT'
__copyright__ = 'Copyright 2020, The Stimson Center'
__maintainer__ = "The Stimson Center"
__maintainer_email = "cooper@pobox.com"


# =====================================================================================================================
# https://developers.google.com/custom-search/v1/reference/rest/v1/cse/list
# https://github.com/caiogranero/google-custom-search-api-python
# I.O.U. caiogranero $10.00 since the Google documentation is not correct and your's is correct!
# Args:
#   q: string, Query (required)
#   c2coff: string, Turns off the translation between zh-CN and zh-TW.
#   cr: string, Country restrict(s).
#   cref: string, The URL of a linked custom search engine
#   cx: string, The custom search engine ID to scope this search query
#   dateRestrict: string, Specifies all search results are from a time period
#   exactTerms: string, Identifies a phrase that all documents in the search results must contain
#   excludeTerms: string, Identifies a word or phrase that should not appear in any documents in the search results
#   fileType: string, Returns images of a specified type. Some of the allowed values are: bmp, gif, png, jpg, svg, pdf..
#   filter: string, Controls turning on or off the duplicate content filter.
#     Allowed values
#       0 - Turns off duplicate content filter.
#       1 - Turns on duplicate content filter.
#   gl: string, Geolocation of end user.
#   googlehost: string, The local Google domain to use to perform the search.
#   highRange: string, Creates a range in form as_nlo value..as_nhi value and attempts to append it to query
#   hl: string, Sets the user interface language.
#   hq: string, Appends the extra query terms to the query.
#   linkSite: string, Specifies that all search results should contain a link to a particular URL
#   lowRange: string, Creates a range in form as_nlo value..as_nhi value and attempts to append it to query
#   lr: string, The language restriction for the search results
#     Allowed values
#       lang_ar - Arabic
#   orTerms: string, Provides additional search terms to check for in a document, where each document in the search results must contain at least one of the additional search terms
#   num: integer, Number of search results to return
#   relatedSite: string, Specifies that all search results should be pages that are related to the specified URL
#   rights: string, Filters based on licensing. Supported values include: cc_publicdomain, cc_attribute, cc_sharealike, cc_noncommercial, cc_nonderived and combinations of these.
#   safe: string, Search safety level
#     Allowed values
#       high - Enables highest level of safe search filtering.
#       medium - Enables moderate safe search filtering.
#       off - Disables safe search filtering.
#   siteSearch: string, Specifies all search results should be pages from a given site
#   siteSearchFilter: string, Controls whether to include or exclude results from the site named in the as_sitesearch parameter
#     Allowed values
#       e - exclude
#       i - include
#   sort: string, The sort expression to apply to the results
#   start: integer, The index of the first result to return
# =====================================================================================================================
#  {
#       allOfTheseWords: null,
#       orTerms: null,
#       country: "any",
#       fileType: "any",
#       exactTerms: null,
#       language: "any",
#       excludeTerms: null,
#       lowRange: null,
#       highRange: null,
#       siteSearch: null,
#       sort: "relevance" // blank
#       means
#       sort # by relevance
#  }
# https://developers.google.com/custom-search/docs/element
# https://stackoverflow.com/questions/37083058/programmatically-searching-google-in-python-using-custom-search
class Search(Resource):
    @staticmethod
    def post():
        # Get environment variables
        load_dotenv()
        api_key = os.getenv('GOOGLE_SECRET_API_KEY')
        cse_id = os.getenv('GOOGLE_SECRET_CUSTOM_SEARCH_ID')
        form = request.get_json()
        kwargs = dict()
        kwargs['filter'] = 1  # Turns on duplicate content filter
        kwargs['safe'] = 'high'  # Enables highest level of safe search filtering
        kwargs['q'] = form['allOfTheseWords']  # must be here
        if "orTerms" in form and form['orTerms']:
            # Provides additional search terms to check for in a document, where each document in
            # the search results must contain at least one of the additional search terms.
            kwargs['orTerms'] = form['orTerms']
        if form['country'] and form['country'].lower() != 'any':
            # https://developers.google.com/custom-search/docs/element
            # Restricts search results to documents originating in a particular country.
            # You may use Boolean operators in the cr parameter's value.
            kwargs['cr'] = countries[form['country']]
        if "exactTerms" in form and form['exactTerms']:
            # Identifies a phrase that all documents in the search results must contain
            kwargs['exactTerms'] = form['exactTerms']
        if form["fileType"] and form['fileType'].lower() != 'any':
            # Restricts results to files of a specified extension. A list of
            # file types indexable by Google can be found in Search Console
            kwargs['fileType'] = file_types[form['fileType']]
        if form['language'] and form['language'].lower() != 'any':
            # https://developers.google.com/custom-search/docs/element
            language_code = languages[form['language']]
            # The local Google domain (for example, google.com, google.de, or google.fr) to use to perform the search
            kwargs['gl'] = language_code
            # Restricts the search to documents written in a particular language
            kwargs['lr'] = f"lang_{language_code}"
        if "excludeTerms" in form and form['excludeTerms']:
            # Identifies a word or phrase that should not appear in any documents in the search results.
            kwargs['excludeTerms'] = form['excludeTerms']
        if "lowRange" in form \
                and form['lowRange'] \
                and form['lowRange'].lower() != "any" \
                and "highRange" in form \
                and form['highRange'] \
                and form['highRange'].lower() != "any":
            # Use lowRange and highRange to append an inclusive search range of lowRange...highRange to the query.
            kwargs['lowRange'] = form['lowRange']
            kwargs['highRange'] = form['highRange']
        if "siteSearch" in form and form['siteSearch']:
            # Specifies a given site which should always be included or excluded from results
            # (see siteSearchFilter parameter, below)
            kwargs['siteSearch'] = form['siteSearch']
        if form['sort'] and form['sort'] == 'date':
            # In Google, sort_by ""  by default is sorted by "relevance"
            kwargs['sort'] = form['sort']

        # print(json.dumps(kwargs))
        service = build("customsearch", "v1", developerKey=api_key)
        response = list()
        start = form['start'] if 'start' in form else 1
        page_limit = 10
        for page in range(0, page_limit):
            result = service.cse().list(
                cx=cse_id,
                start=start,
                **kwargs
            ).execute()
            if 'items' in result and len(result['items']):
                for item in result['items']:
                    if 'displayLink' in item and item['displayLink'] \
                            and 'snippet' in item and item['snippet'] \
                            and 'link' in item and item['link']:
                        response.append(item)
                        start += 1
            else:
                break
        return response, 200, {'Content-Type': 'application/json'}
