from setuptools import setup # type: ignore

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name = "pyaiocrawler", # pip install pyaiocrawler
    version = "0.3.3",
    author = "Tapan Pandita",
    author_email = "tapan.pandita@gmail.com",
    description = "Asynchronous web crawler built on asyncio",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tapanpandita/aiocrawler",
    license = "MIT",
    install_requires = ["aiohttp", "beautifulsoup4", "cchardet", "aiodns"],
    py_modules = ["aiocrawler"],
    zip_safe = True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Framework :: AsyncIO",
    ],
)

# TODO: Do all this and delete these lines
# register: Create an accnt on pypi, store your credentials in ~/.pypirc:
#
# [pypirc]
# servers =
#     pypi
#
# [server-login]
# username:<username>
# password:<pass>
#
# $ python setup.py register # one time only, will create pypi page for pocket
# $ python setup.py sdist --formats=gztar,zip upload # create a new release
#
