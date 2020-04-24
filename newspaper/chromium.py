from selenium import webdriver


# https://testdriven.io/blog/building-a-concurrent-web-scraper-with-python-and-selenium/
def get_driver():
    # initialize options
    options = webdriver.ChromeOptions()
    # pass in headless argument to options
    options.add_argument('--headless')
    # initialize driver
    driver = webdriver.Chrome(options=options)
    return driver


def get_page_source(url):
    # https://stackoverflow.com/questions/16511337/correct-way-to-try-except-using-python-requests-module
    browser = get_driver()
    browser.get(url)
    return browser.page_source
