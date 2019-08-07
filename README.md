AIOCrawler
==========
[![Build Status](https://travis-ci.org/tapanpandita/aiocrawler.svg?branch=master)](https://travis-ci.org/tapanpandita/aiocrawler)
[![Coverage Status](https://coveralls.io/repos/github/tapanpandita/aiocrawler/badge.svg?branch=master)](https://coveralls.io/github/tapanpandita/aiocrawler?branch=master)
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
from aiocrawler import AIOCrawler

crawler = AIOCrawler('https://www.google.com', depth=3)
sitemap = await crawler.generate_sitemap()
```

### Configuring the crawler

```python
from aiocrawler import AIOCrawler

crawler = AIOCrawler(
    init_url='https://www.google.com',
    depth=3,
    concurrency=300,
    user_agent='My Amazing Crawler'
)
```

### Extending the crawler

WIP
