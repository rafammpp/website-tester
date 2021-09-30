Simple script to check recursively all internal links of a website. It will export the errors on a CSV file named 'broken_links_{date}.csv'.

# Requirements
Python >= 3.6 (because of the f-strings)
Scrapy >= 2.5.0

# Installation guide


# Usage

`python internal_broken_links.py [-h] urls [urls ...] [-p PREFIXES [PREFIXES ...]]`

It will check only links from the same domain as the ones passed as an arguments. You know, internal links.

## Examples:

Check internal links of example.com starting on the root page:
`python internal_broken_links.py https://example.com/`

Check internal links of example.com and another-domain.com starting at its root pages:
`python internal_broken_links.py https://example.com/ http://another-domain.com/`

Check internal links of example.com but only the ones under US english language prefix:
`python internal_broken_links.py https://example.com/en-us/ -p en-us`

Check internal links of example.com starting on US english language prefix but follow links of Spanish Spain as well:
`python internal_broken_links.py https://example.com/en-us/ -p es-es en-us`

# Recomendations
To avoid getting banned by your own website, whitelist your ip on the server.

Scrapy has a lot of [settings](https://docs.scrapy.org/en/latest/topics/settings.html#built-in-settings-reference). If you need to tweak anything, there is a high chance that you can use one of those.

Review the CSV containing the errors with excel or google sheet or similar.