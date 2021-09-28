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

    def __init__(self, urls, prefixes, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
        if not (url.startswith('/') or url.startswith('http')):
            return False
        try:
            return not self.allowed_prefixes or get_prefix(url) in self.allowed_prefixes
        except (TypeError, AttributeError):
            return False
    
    def parse(self, response):
        if response.status != 200:
            item = {}
            item['url'] = response.url
            item['link_text'] = response.meta.get('link_text')
            item['previous_page'] = response.meta.get('prev_url')
            item['status'] = response.status

            yield item
        
        try:
            lang = response.xpath('/html/@lang').get()
        except:
            lang = 'en'
        
        for link in response.css('a'):
            href = link.xpath('@href').get()
            text = link.xpath('text()').get()
            if self.is_allowed(href):
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
args = parser.parse_args()

if args.urls:
    process = CrawlerProcess(settings={
        "FEEDS": {
            f"exported_broken_links/broken_links_{time.strftime('%Y-%m-%d_%H%M')}.csv": {"format": "csv"},
        },
        "BOT_NAME": 'website_tester',
        "DEPTH_LIMIT": 0,
        "RETRY_ENABLED": False,
        "HTTPERROR_ALLOW_ALL": True,
        "ROBOTSTXT_OBEY": True,
        "DEFAULT_REQUEST_HEADERS": {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en',
        },
        "AUTOTHROTTLE_ENABLED": True,
    })

    process.crawl(BrokenLinksSpider, urls=args.urls, prefixes=args.prefixes)
    process.start()
