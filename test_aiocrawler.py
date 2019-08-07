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
