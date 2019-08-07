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

    def __init__(self, init_url: str, depth: int = 1, concurrency: int = 1000,
                 user_agent: str = 'AIOCrawler') -> None:
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
        self.sitemap: Dict[str, Set[str]] = {}
        self.session: ClientSession = ClientSession()
        self.task_queue: asyncio.Queue = asyncio.Queue(maxsize=concurrency)

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

    async def crawl_page(self, url: str) -> Tuple[str, Set[str], bytes]:
        '''
        Request a webpage and return all relevant data from it
        '''
        html = await self._make_request(url)
        links = self.find_links(html)
        return url, links, html

    async def worker(self) -> None:
        '''
        Pops a url from the task queue and crawls the page
        '''
        while True:
            url, depth = await self.task_queue.get()
            print(f'Working on {url} at {depth}')

            if (depth >= self.depth) or (url in self.crawled_urls):
                self.task_queue.task_done()
                print('Max depth reached')
                continue

            self.crawled_urls.add(url)

            try:
                url, links, _ = await self.crawl_page(url)
            except Exception as excp:
                #TODO: Handle exception correctly
                print(f'=============={excp}===============')
            else:
                self.sitemap[url] = links

                for link in links:
                    await self.task_queue.put((link, depth + 1))
            finally:
                self.task_queue.task_done()

    async def crawl(self) -> None:
        '''
        Starts concurrent workers and kickstarts scraping
        '''
        self.task_queue.put_nowait((self.init_url, 0))
        workers = [asyncio.create_task(self.worker()) for i in range(self.concurrency)]

        await self.task_queue.join()

        for worker in workers:
            worker.cancel()

        await self.session.close()

    async def generate_sitemap(self) -> Dict[str, Set[str]]:
        '''
        Run the crawler and return the generated sitemap
        '''
        await self.crawl()
        return self.sitemap
