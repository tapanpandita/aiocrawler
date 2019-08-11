AIOCrawler
==========
[![Build Status](https://travis-ci.org/tapanpandita/aiocrawler.svg?branch=master)](https://travis-ci.org/tapanpandita/aiocrawler)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/eab04685503c490082f1c6a545c4016e)](https://www.codacy.com/app/tapanpandita/aiocrawler?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=tapanpandita/aiocrawler&amp;utm_campaign=Badge_Grade)
[![PyPI version](https://badge.fury.io/py/pyaiocrawler.svg)](https://badge.fury.io/py/pyaiocrawler)

Asynchronous web crawler built on [asyncio](https://docs.python.org/3/library/asyncio.html)

Installation
------------
```shell
pip install pyaiocrawler
```
Usage
-----
### Generating sitemap
```python
from aiocrawler import SitemapCrawler

crawler = SitemapCrawler('https://www.google.com', depth=3)
sitemap = await crawler.get_results()
```
### Configuring the crawler
```python
from aiocrawler import SitemapCrawler

crawler = SitemapCrawler(
    init_url='https://www.google.com', # The base URL to start crawling from
    depth=3,                           # The maximum depth to crawl till
    concurrency=300,                   # Maximum concurrent requests to make
    max_retries=3,                     # Maximum times the crawler will retry to get a response from a URL
    user_agent='My Crawler',           # Use a custom user agent for requests
)
```
### Extending the crawler
To create your own crawler, simply subclass `AIOCrawler` and implement the `parse` method. For every page crawled, the `parse` method is executed with the url of the page, the links in that page and the html of the page. The return of the `parse` method is appended to an array which is then available when the `get_results` method is called. We have implemented an example crawler here that extracts the title from the page.
```python
from aiocrawler import AIOCrawler
from bs4 import BeautifulSoup          # We will use beautifulsoup to extract the title from the html
from typing import Set, Tuple


class TitleScraper(AIOCrawler):
    '''
    Subclasses AIOCrawler to extract titles for the pages on the given domain
    '''

    def parse(self, url: str, links: Set[str], html: bytes) -> Tuple[str, str]:
        '''
        Returns the url and the title of the url
        '''
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.find('title').string
        return url, title


crawler = TitleScraper('https://www.google.com', 3)
titles = await crawler.get_results()
```
Contributing
------------
### Installing dependencies
```shell
pipenv install --dev
```
### Running tests
```shell
pytest --cov=aiocrawler
```
