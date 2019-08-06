'''
A webcrawler built on asyncio and aiohttp
'''
import asyncio
import logging
from urllib.parse import urljoin, urlparse
from typing import Set, Iterable, List, Tuple, Dict

from aiohttp import ClientSession
from bs4 import BeautifulSoup # type: ignore


class AIOCrawler:
    '''
    Implements all the methods necessary to crawl an entire domain
    '''

    def __init__(self, init_url: str, depth: int = 1, concurrency: int = 1000,
                 user_agent: str = 'AIOCrawler') -> None:
        '''
        Initialize state
        '''
        self.init_url = init_url
        self.depth = depth
        self.concurrency = concurrency
        self.user_agent = user_agent

        self.base_url: str = '{}://{}'.format(
            urlparse(self.init_url).scheme,
            urlparse(self.init_url).netloc,
        )
        self.crawled_urls: Set[str] = set()
        self.session: ClientSession = ClientSession()
        self.bounded_sempahore: asyncio.BoundedSemaphore = asyncio.BoundedSemaphore(concurrency)

    async def _make_request(self, url: str) -> bytes:
        '''
        Wrapper on aiohttp to make get requests on a shared session
        '''
        logging.debug('Fetching: {url}')
        headers = {
            'User-Agent': self.user_agent,
        }
        async with self.bounded_sempahore:
            async with self.session.get(url, headers=headers, timeout=30) as response:
                html = await response.read()
                return html

    def find_links(self, html: bytes) -> Set[str]:
        '''
        Find all the links in passed html
        '''
        soup = BeautifulSoup(html, 'html.parser')
        links = {
            urljoin(self.base_url, a['href'])
            for a in soup.select('a[href]')
            if urljoin(self.base_url, a['href']).startswith(self.base_url)
        }
        return links

    async def crawl_page(self, url: str) -> Tuple[str, Set[str], bytes]:
        '''
        Request a webpage and return all relevant data from it
        '''
        html = await self._make_request(url)
        links = self.find_links(html)
        return url, links, html

    async def crawl_multiple_pages(self, urls_to_crawl: Iterable[str]) -> List[Tuple[str, Set[str], str]]:
        '''
        Request multiple webpages. Scrape and return relevant data for each.
        '''
        tasks = []

        for url in urls_to_crawl:

            if url in self.crawled_urls:
                continue

            self.crawled_urls.add(url)
            tasks.append(asyncio.create_task(self.crawl_page(url)))

        results = [await task for task in asyncio.as_completed(tasks)]
        return results

    async def sitemap(self) -> Dict[str, Set[str]]:
        '''
        Generate a sitemap for given domain
        '''
        urls = [self.init_url]
        sitemap = {}

        for _ in range(self.depth):
            results = await self.crawl_multiple_pages(urls)
            urls = []

            for url, links, _ in results:
                urls.extend(links)
                sitemap[url] = links

        await self.session.close()

        return sitemap



class AnotherCrawler:

    def __init__(self, init_url: str, depth: int = 1, concurrency: int = 1000,
                 user_agent: str = 'AnotherCrawler') -> None:
        '''
        Initialize State
        '''
        self.init_url = init_url
        self.depth = depth
        self.concurrency = concurrency
        self.user_agent = user_agent

        self.base_url: str = '{}://{}'.format(
            urlparse(self.init_url).scheme,
            urlparse(self.init_url).netloc,
        )
        self.crawled_urls: Set[str] = set()
        self.session: ClientSession = ClientSession()
        self.task_queue: asyncio.Queue = asyncio.Queue(maxsize=concurrency)
        self.results_queue: asyncio.Queue = asyncio.Queue(maxsize=concurrency)

    async def _make_request(self, url: str) -> bytes:
        '''
        Wrapper on aiohttp to make get requests on a shared session
        '''
        logging.debug('Fetching: {url}')
        headers = {
            'User-Agent': self.user_agent,
        }
        async with self.session.get(url, headers=headers) as response:
            html = await response.read()
            return html

    def find_links(self, html: bytes) -> Set[str]:
        '''
        Find all the links in passed html
        '''
        soup = BeautifulSoup(html, 'html.parser')
        links = {
            urljoin(self.base_url, a['href'])
            for a in soup.select('a[href]')
            if urljoin(self.base_url, a['href']).startswith(self.base_url)
        }
        return links

    async def crawl_page(self, url: str):
        '''
        Request a webpage and return all relevant data from it
        '''
        html = await self._make_request(url)
        links = self.find_links(html)
        return url, links, html

    async def consumer(self):
        '''
        '''
        while True:
            url, depth= await self.task_queue.get()
            print(f'Working on {url} at {depth}')

            if depth >= self.depth:
                self.task_queue.task_done()
                print('Max depth reached')
                break

            if url in self.crawled_urls:
                continue

            self.crawled_urls.add(url)
            data = await self.crawl_page(url)
            await self.results_queue.put((data, depth))
            self.task_queue.task_done()

    async def producer(self):
        '''
        '''
        while True:
            data, depth = await self.results_queue.get()
            url, links, html = data

            curr_depth = depth + 1

            for url in links:
                await self.task_queue.put((url, curr_depth))

            self.results_queue.task_done()

    async def crawl(self):
        '''
        '''
        self.task_queue.put_nowait((self.init_url, 0))
        producers = [asyncio.create_task(self.producer()) for i in range(2)]
        consumers = [asyncio.create_task(self.consumer()) for i in range(self.concurrency)]

        await asyncio.gather(*producers, *consumers)

        # results = [await task for task in asyncio.as_completed(consumers)]

        print('Waiting for tasks_queue to join')
        await self.task_queue.join()
        print('Waiting for results_queue to join')
        await self.results_queue.join()

        print('Waiting for producers to cancel')
        for producer in producers: producer.cancel()
        print('Waiting for consumers to cancel')
        for consumer in consumers: consumer.cancel()

        print('Waiting for session to close')
        await self.session.close()
