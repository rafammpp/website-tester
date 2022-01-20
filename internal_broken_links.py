#!/usr/bin/env python
import scrapy, re, logging, argparse, time
from scrapy.crawler import CrawlerProcess


def get_prefix(url):
    regex = re.compile(r'(http(s)?://(?P<domain>[^/]+))?/(?P<prefix>[a-zA-Z-]+)/(?P<path>.*)')
    matches = regex.match(url)
    return matches.group('prefix')


class BrokenLinksSpider(scrapy.Spider):
    name = 'internal-broken-links'
    allowed_domains = []
    allowed_prefixes = []
    start_urls = []
    accept_lang = ''

    def __init__(self, urls, prefixes, domains, accept_lang='', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.allowed_domains += domains
        self.accept_lang = accept_lang
        for url in urls:
            self.start_urls.append(url)
            regex = re.compile(r'http(s)?://(?P<domain>[^/]+)(/(?P<path>.*))?')
            matches = regex.match(url)
            try:
                if (domain:=matches.group('domain')) not in self.allowed_domains:
                    self.allowed_domains.append(domain)
            except AttributeError:
                self.allowed_domains.append(url)

        self.allowed_prefixes += prefixes
        
        logging.info(f'Allowed domains: {self.allowed_domains}')
        logging.info(f'Allowed prefixes: {self.allowed_prefixes}')

    def is_allowed(self, url):
        if url.startswith(('mailto:','tel:', 'javascript:',)): return False
        match = re.compile(r"^(?P<schema>[^:]+)://.+$").match(url)
        schema = match.group('schema') if match else None
        
        if schema and not schema.startswith('http'):
            return False
        try:
            return not self.allowed_prefixes or get_prefix(url) in self.allowed_prefixes
        except (TypeError, AttributeError):
            return True

    def parse(self, response):
        if response.status != 200:
            item = {
                'url': response.url,
                'link_text': response.meta.get('link_text'),
                'previous_page': response.meta.get('prev_url'),
                'status': response.status,
            }

            yield item
        
        if self.accept_lang:
            lang = self.accept_lang
        else:
            try:
                lang = response.xpath('/html/@lang').get()
            except:
                lang = 'en'
        
        for link in response.css('a'):
            href = link.xpath('@href').get()
            text = link.xpath('text()').get()
            if href and self.is_allowed(href):
                yield response.follow(link, self.parse,
                    meta={
                        'link_text': text,
                        'prev_url': response.url,
                    },
                    headers={
                        'Accept-Language': lang,
                    }
                )


parser = argparse.ArgumentParser(description='Check site internal links')
parser.add_argument('urls', type=str, nargs='+', help='URLs, with scheme, to start with.')
parser.add_argument('-p', '--prefixes', dest='prefixes', nargs='+', help="Allowed lang_code prefixes. Useful to check only a few langs.", default=[])
parser.add_argument('-d', '--domains', dest='domains', nargs='+', help='Only follow links from these domains.')
parser.add_argument('--disable-throttling', dest='disable_throttling', action='store_true', help='Disable the authrottling extension. This will impact a lot on the server performance, be nice', default=False)
parser.add_argument('--disable-retry', dest='disable_retry', action='store_true', help='If an URL returns an error, don\'t retry.', default=False)
parser.add_argument('--csv-name', dest='csv_name', default='')
parser.add_argument('--accept-lang', default='', help='Specify an accept lang for request headers.')
args = parser.parse_args()

suffix = f"{time.strftime('%Y-%m-%d')}_{args.csv_name}"

if args.urls:
    process = CrawlerProcess(settings={
        "FEEDS": {
            f"exported_broken_links/broken_links_{suffix}.csv": {"format": "csv"},
        },
        "BOT_NAME": 'website_tester',
        "CONCURRENT_REQUESTS": 32,
        "LOG_LEVEL": 'INFO',
        "DEPTH_LIMIT": 0,
        "RETRY_ENABLED": not args.disable_retry,
        "HTTPERROR_ALLOW_ALL": True,
        "ROBOTSTXT_OBEY": True,
        "DEFAULT_REQUEST_HEADERS": {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': args.accept_lang or 'en',
        },
        "AUTOTHROTTLE_ENABLED": not args.disable_throttling,
    })

    process.crawl(
        BrokenLinksSpider,
        urls=args.urls,
        prefixes=args.prefixes,
        domains=args.domains,
        accept_lang=args.accept_lang,
    )
    process.start()
