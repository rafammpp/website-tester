import scrapy, re, logging, argparse, time
from scrapy.crawler import CrawlerProcess


def get_prefix(url):
    regex = re.compile(r'(http(s)?://(?P<domain>[^/]+))?/(?P<prefix>\w\w(-\w\w)?)/(?P<path>.*)')
    matches = regex.match(url)
    return matches.group('prefix') if matches else ''


class BrokenLinksSpider(scrapy.Spider):
    name = 'internal-broken-links'
    allowed_domains = []
    allowed_prefixes = ['']
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

            try:
                self.allowed_prefixes.append(get_prefix(url))
            except AttributeError:
                pass

        self.allowed_prefixes += prefixes
        
        logging.info(f'Allowed domains: {self.allowed_domains}')
        logging.info(f'Allowed prefixes: {self.allowed_prefixes}')

    def is_allowed(self, url):
        try:
            url = url[0]
        except (IndexError):
            pass
        try:
            return not self.allowed_prefixes or get_prefix(url) in self.allowed_prefixes
        except (TypeError, AttributeError):
            return False
    
    def parse(self, response):
        if response.status != 200:
            item = {}
            item['url'] = response.url
            item['prev_page'] = response.meta.get('prev_url')
            item['prev_link_url'] = response.meta.get('prev_href')
            item['prev_link_text'] = response.meta.get('prev_link_text')
            item['status'] = response.status

            yield item
        
        try:
            lang = response.xpath('/html/@lang').get()
        except:
            lang = 'en'
        
        for link in response.css('a'):
            href = link.xpath('@href').extract()
            text = link.xpath('text()').extract()

            if self.is_allowed(href):
                yield response.follow(link, self.parse,
                    meta={
                        'prev_link_text': text,
                        'prev_href': href,
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
            f"broken_links_{time.strftime('%Y-%m-%d_%H:%M')}.csv": {"format": "csv"},
        },
        "BOT_NAME": 'website_tester',
        "DEPTH_LIMIT": 0,
        "RETRY_ENABLED": False,
        "HTTPERROR_ALLOW_ALL": True,
        "ROBOTSTXT_OBEY": True,
        "DEFAULT_REQUEST_HEADERS": {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en',
            'X-OV2-Bot-Name': 'broken-links-bot',
        },
    })

    process.crawl(BrokenLinksSpider, urls=args.urls, prefixes=args.prefixes)
    process.start()
