'''
A webcrawler built on asyncio and aiohttp
'''
import asyncio
import logging
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse
from typing import Set, Iterable, List, Tuple, Dict

from aiohttp import ClientSession, ClientResponseError
from aiohttp import ClientConnectionError, ClientPayloadError
from aiohttp.client_exceptions import TooManyRedirects
from bs4 import BeautifulSoup # type: ignore
from bs4.element import Tag # type: ignore


logger = logging.getLogger('AIOCrawler')


class InvalidContentTypeError(Exception):
    '''
    Exception raised when response content type is not in allowed types
    '''
    def __init__(self, response):
        self.response = response


@dataclass
class TaskQueueMessage:
    url: str
    depth: int
    retry_count: int


class AIOCrawler:
    '''
    Crawler baseclass that concurrently crawls multiple pages till provided depth
    Built on asyncio
    '''
    valid_content_types: Set[str] = {
        'text/html',
        'text/xhtml',
        'application/xhtml+xml',
        'application/xhtml',
        'application/html',
    }

    def __init__(self, init_url: str, depth: int = 1, concurrency: int = 100, max_retries: int = 2, user_agent: str = 'AIOCrawler') -> None:
        '''
        Initialize State
        '''
        self.init_url = init_url
        self.depth = depth
        self.concurrency = concurrency
        self.max_retries = max_retries
        self.user_agent = user_agent
        self.base_url: str = '{}://{}'.format(
            urlparse(self.init_url).scheme,
            urlparse(self.init_url).netloc,
        )
        self.crawled_urls: Set[str] = set()
        self.results: List = []
        self.session: ClientSession = ClientSession()
        self.task_queue: asyncio.Queue = asyncio.Queue(maxsize=concurrency)

    async def _make_request(self, url: str) -> str:
        '''
        Wrapper on aiohttp to make get requests on a shared session
        '''
        logging.debug('Fetching: {url}')
        headers = {
            'User-Agent': self.user_agent,
        }
        async with self.session.get(url, headers=headers,
                                    raise_for_status=True,
                                    max_redirects=10) as response:

            if response.content_type not in self.valid_content_types:
                raise InvalidContentTypeError(response)

            html = await response.text()
            return html

    def normalize_urls(self, urls: Iterable[Tag]) -> Set[str]:
        '''
        Normalizes passed urls - Adds domain to relative links
        and ignores links from other domains
        '''
        links = {
            urljoin(self.base_url, url['href'])
            for url in urls
            if urljoin(self.base_url, url['href']).startswith(self.base_url)
        }
        return links

    def find_links(self, html: str) -> Set[str]:
        '''
        Finds all the links in passed html
        '''
        soup = BeautifulSoup(html, 'html.parser')
        links = self.normalize_urls(soup.select('a[href]'))
        return links

    def parse(self, url: str, links: Set[str], html: str):
        raise NotImplementedError('{}.parse callback is not defined'.format(self.__class__.__name__))

    async def crawl_page(self, url: str) -> Tuple[str, Set[str], str]:
        '''
        Request a webpage and return all relevant data from it
        '''
        html = await self._make_request(url)
        links = self.find_links(html)
        return url, links, html

    async def retry_task(self, task):
        '''
        Retries a task if max retries not hit
        '''
        if task.retry_count < self.max_retries:
            self.crawled_urls.discard(task.url)
            task_message = TaskQueueMessage(task.url, task.depth, task.retry_count + 1)
            await self.task_queue.put(task_message)
        else:
            logger.error(f'Max retries exceeded for url: {task.url}')

    async def worker(self) -> None:
        '''
        Pops a url from the task queue and crawls the page
        '''
        while True:
            task = await self.task_queue.get()
            logger.debug(f'Working on {task.url} at {task.depth}')

            if (task.depth >= self.depth) or (task.url in self.crawled_urls):
                self.task_queue.task_done()
                logger.debug('Max depth reached')
                continue

            self.crawled_urls.add(task.url)

            try:
                url, links, html = await self.crawl_page(task.url)
            except ClientResponseError as excp:

                if excp.status > 499:
                    await self.retry_task(task)
                else:
                    logger.error(f'Client error with status: {excp.status} at url: {task.url}')

            except ClientConnectionError as excp:
                await self.retry_task(task)
            except InvalidContentTypeError as excp:
                logger.error(f'Non html content type received in response at url: {task.url}')
            except TooManyRedirects as excp:
                logger.error(f'Redirected too many times at url: {task.url}')
            except ClientPayloadError as excp:
                logger.error(f'Invalid compression or encoding at url: {task.url}')
            except Exception as excp:
                logger.error(f'Unhandled exception: {excp}')
            else:
                self.results.append(self.parse(url, links, html))

                for link in links:
                    task_message = TaskQueueMessage(link, task.depth + 1, 0)
                    await self.task_queue.put(task_message)
            finally:
                self.task_queue.task_done()

    async def crawl(self) -> None:
        '''
        Starts concurrent workers and kickstarts scraping
        '''
        task_message = TaskQueueMessage(self.init_url, 0, 0)
        self.task_queue.put_nowait(task_message)
        workers = [asyncio.create_task(self.worker()) for i in range(self.concurrency)]

        await self.task_queue.join()

        for worker in workers:
            worker.cancel()

        await self.session.close()

    async def get_results(self) -> List:
        '''
        Run the crawler and return the generated sitemap
        '''
        await self.crawl()
        return self.results


class SitemapCrawler(AIOCrawler):
    '''
    Subclasses AIOCrawler to generate a sitemap for a given domain.
    Call `get_results` to access the sitemap.
    '''

    def parse(self, url: str, links: Set[str], html: str) -> Tuple[str, Set[str]]:
        '''
        Return a tuple to create the sitemap
        '''
        return url, links
