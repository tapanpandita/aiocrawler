import pytest # type: ignore
from aiocrawler import AIOCrawler


def test_setting_initial_url():
    url = 'https://www.example.com'
    crawler = AIOCrawler(url)
    assert crawler.init_url == url


def test_initial_default_depth():
    url = 'https://www.example.com'
    crawler = AIOCrawler(url)
    assert crawler.depth == 1


def test_initial_default_concurrency():
    url = 'https://www.example.com'
    crawler = AIOCrawler(url)
    assert crawler.concurrency == 1000


def test_initial_default_user_agent():
    url = 'https://www.example.com'
    crawler = AIOCrawler(url)
    assert crawler.user_agent == 'AIOCrawler'


def test_setting_depth():
    depth = 5
    url = 'https://www.example.com'
    crawler = AIOCrawler(url, depth=depth)
    assert crawler.depth == depth


def test_setting_concurrency():
    concurrency = 250
    url = 'https://www.example.com'
    crawler = AIOCrawler(url, concurrency=concurrency)
    assert crawler.concurrency == concurrency


def test_setting_user_agent():
    user_agent = 'Test User Agent'
    url = 'https://www.example.com'
    crawler = AIOCrawler(url, user_agent=user_agent)
    assert crawler.user_agent == user_agent


def test_find_links():
    url = 'https://www.example.com'
    crawler = AIOCrawler(url)
    html = '''
    <html>
    <body>
        <a href="https://www.example.com/about">Test 1</a>
        <a href="https://api.example.com/docs">Test 2</a>
        <a href="/careers">Test 3</a>
    </body>
    </html>
    '''
    links = crawler.find_links(html)
    assert links == {'https://www.example.com/about', 'https://www.example.com/careers'}
