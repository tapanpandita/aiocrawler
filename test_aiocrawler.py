import pytest # type: ignore
from aiocrawler import AIOCrawler


@pytest.fixture
def crawler():
    url = 'https://www.example.com'
    crawler = AIOCrawler(url)
    return crawler


@pytest.fixture
def html():
    html_string = b'''
    <html>
    <body>
        <a href="https://www.example.com/about">Test 1</a>
        <a href="https://api.example.com/docs">Test 2</a>
        <a href="/careers">Test 3</a>
    </body>
    </html>
    '''
    return html_string


@pytest.fixture
def mock_make_request(monkeypatch, html):

    async def mock_make_request(*args, **kwargs):
        return html

    monkeypatch.setattr(AIOCrawler, '_make_request', mock_make_request)


def test_setting_initial_url(crawler):
    url = 'https://www.example.com'
    assert crawler.init_url == url


def test_initial_default_depth(crawler):
    assert crawler.depth == 1


def test_initial_default_concurrency(crawler):
    assert crawler.concurrency == 1000


def test_initial_default_user_agent(crawler):
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


def test_find_links(html, crawler):
    links = crawler.find_links(html)
    assert links == {'https://www.example.com/about', 'https://www.example.com/careers'}


@pytest.mark.asyncio
async def test_crawl_page(mock_make_request, crawler, html):
    url = 'https://www.example.com'
    url, links, html = await crawler.crawl_page(url)
    assert url == url
    assert links == {'https://www.example.com/about', 'https://www.example.com/careers'}
    assert html == html
