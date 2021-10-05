Simple script to check recursively all internal links from a website. It will export the errors on a CSV file named 'broken_links_{date}.csv'.

# Requirements
Python >= 3.8
Scrapy >= 2.5.0

# Installation guide
1. Install python. Follow one of the guides out there. You don't need a virtual environment for this, but do as you like. Make sure to download Python pip as well.
2. Download this repository, either from git with `git clone https://github.com/rafammpp/website-tester.git` or downloading the zip from github.
3. Open a terminal in the directory and run `pip install -r requirements.txt`
4. That's it! Now the usage.

# Usage
```
internal_broken_links.py [-h] [-p PREFIXES [PREFIXES ...]] [-d DOMAINS [DOMAINS ...]]
                                [--disable-throttling] [--disable-retry]
                                urls [urls ...]

Check site internal links

positional arguments:
  urls                  URLs, with scheme, to start with.

optional arguments:
  -h, --help            show this help message and exit
  -p PREFIXES [PREFIXES ...], --prefixes PREFIXES [PREFIXES ...]
                        Allowed lang_code prefixes. Useful to check only a few langs.
  -d DOMAINS [DOMAINS ...], --domains DOMAINS [DOMAINS ...]
                        Only follow links from these domains.
  --disable-throttling  Disable the authrottling extension. This will impact a lot on the server
                        performance, be nice
  --disable-retry       If an URL returns an error, don't retry.
```

It will check only links from the same domain as the ones passed as an arguments. You know, internal links.
Any returning error link will be exported in a csv file. The csv will contain four columns: url, link_text, previous_page, status code.

## Examples:
Check internal links of example.com starting on the root page:
`python internal_broken_links.py https://example.com/`

Check internal links of example.com and another-domain.com starting at its root pages:
`python internal_broken_links.py https://example.com/ http://another-domain.com/`

Check internal links of example.com but only the ones under US english language prefix:
`python internal_broken_links.py https://example.com/en-us/ -p en-us`

Check internal links of example.com starting on US english language prefix but follow links of Spanish Spain as well:
`python internal_broken_links.py https://example.com/en-us/ -p es-es en-us`

Check links from a local server:
`python internal_broken_links.py http://127.0.0.1:8000/ -p 'en' -d 127.0.0.1`

Important note: The allowed domains var can't contain ports, it will be ignored. You have to specify the domain with `-d` option.
Urls always has to be written starting with the schema (http:// or https://).

# Recomendations
To avoid getting banned by your own website, whitelist your ip on the server.

Scrapy has a lot of [settings](https://docs.scrapy.org/en/latest/topics/settings.html#built-in-settings-reference). If you need to tweak anything, there is a high chance that you can use one of those.

Review the CSV containing the errors with excel, google sheet or similar.
