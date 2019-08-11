import pytest # type: ignore
import asyncio
import aiocrawler
from aiocrawler import AIOCrawler, SitemapCrawler, InvalidContentTypeError, TaskQueueMessage


@pytest.fixture
def crawler():
    url = 'https://www.example.com'
    crawler = AIOCrawler(url)
    return crawler


@pytest.fixture
def html():
    html_string = '''
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
def create_mock_coroutine(mocker, monkeypatch):

    def _create_mock_patch_coro(to_patch=None):
        mock = mocker.Mock()

        async def _coro(*args, **kwargs):
            return mock(*args, **kwargs)

        if to_patch:
            monkeypatch.setattr(to_patch, _coro)

        return mock, _coro

    return _create_mock_patch_coro


@pytest.fixture
def mock_make_request(monkeypatch, html):

    async def mock_make_request(*args, **kwargs):
        return html

    monkeypatch.setattr(AIOCrawler, '_make_request', mock_make_request)


@pytest.fixture
def mock_make_request_generic(create_mock_coroutine):
    mock_make_request, mock_coroutine = create_mock_coroutine(to_patch='aiocrawler.AIOCrawler._make_request')
    return mock_make_request


@pytest.fixture
def mock_queue(mocker, monkeypatch):
    queue = mocker.Mock()
    monkeypatch.setattr(asyncio, 'Queue', queue)
    return queue.return_value


@pytest.fixture
def mock_put_nowait(mock_queue, create_mock_coroutine):
    mock_put, coro_put = create_mock_coroutine()
    mock_queue.put_nowait = coro_put
    return mock_put


@pytest.fixture
def mock_join(mock_queue, create_mock_coroutine):
    mock_join, coro_join = create_mock_coroutine()
    mock_queue.join = coro_join
    return mock_join


def test_task_queue_message():
    url = 'https://www.example.com'
    depth = 5
    retry_count = 3
    task_message = TaskQueueMessage(url, depth, retry_count)
    assert task_message.url == url
    assert task_message.depth == depth
    assert task_message.retry_count == retry_count


def test_initial_default_depth(crawler):
    assert crawler.depth == 1


def test_initial_default_concurrency(crawler):
    assert crawler.concurrency == 100


def test_initial_default_task_queue_maxsize(crawler):
    assert crawler.task_queue.maxsize == crawler.concurrency


def test_initial_default_max_retries(crawler):
    assert crawler.max_retries == 2


def test_initial_default_user_agent(crawler):
    assert crawler.user_agent == 'AIOCrawler'


def test_initial_crawled_urls(crawler):
    assert isinstance(crawler.crawled_urls, set)
    assert not crawler.crawled_urls


def test_initial_results(crawler):
    assert isinstance(crawler.results, list)
    assert not crawler.results


def test_base_url(crawler):
    assert crawler.base_url == 'https://www.example.com'


def test_setting_initial_url(crawler):
    url = 'https://www.example.com'
    assert crawler.init_url == url


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


def test_setting_max_retries():
    max_retries = 5
    url = 'https://www.example.com'
    crawler = AIOCrawler(url, max_retries=max_retries)
    assert crawler.max_retries == max_retries


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


@pytest.mark.asyncio
async def test_retry_task(crawler):
    task_message = TaskQueueMessage('https://www.example.com', 2, 1)
    await crawler.retry_task(task_message)
    assert crawler.task_queue.qsize() == 1


@pytest.mark.asyncio
async def test_retry_task_with_max_retries_exceeded(crawler):
    task_message = TaskQueueMessage('https://www.example.com', 2, 5)
    await crawler.retry_task(task_message)
    assert crawler.task_queue.qsize() == 0


def test_parse_raises_not_implemented(crawler, html):
    url = 'https://wwww.example.com'
    links = {'https://www.example.com/about', 'https://www.example.com/contactus'}

    with pytest.raises(NotImplementedError):
        crawler.parse(url, links, html)


@pytest.mark.asyncio
async def test_get_results(crawler, create_mock_coroutine):
    mock_crawl, _ = create_mock_coroutine(to_patch='aiocrawler.AIOCrawler.crawl')
    results = await crawler.get_results()
    mock_crawl.assert_called_once()
    assert results == []


# @pytest.mark.asyncio
# async def test_crawl(crawler, create_mock_coroutine, mock_put_nowait, mock_queue, mock_join):
    # mock_worker, _ = create_mock_coroutine(to_patch='aiocrawler.AIOCrawler.worker')
    # await crawler.crawl()
    # mock_put_nowait.assert_called_once_with(TaskQueueMessage(crawler.init_url, 0, 0))
    # mock_join.assert_called_once()
    # assert mock_worker.call_count == crawler.concurrency


def test_sitemap_crawler_parse(html):
    crawler = SitemapCrawler('https://www.example.com')
    url = 'https://wwww.example.com'
    links = {'https://www.example.com/about', 'https://www.example.com/contactus'}
    assert crawler.parse(url, links, html) == (url, links)
