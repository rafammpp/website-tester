import scrapy, re, logging


def get_prefix(url):
    regex = re.compile(r'(http(s)?://(?P<domain>[^/]+))?/(?P<prefix>\w\w(-\w\w)?)/(?P<path>.*)')
    matches = regex.match(url)
    return matches.group('prefix') if matches else ''


class BrokenLinksSpider(scrapy.Spider):
    name = 'internal-broken-links'
    allowed_domains = []
    allowed_prefixes = ['']
    start_urls = []

    def __init__(self, urls, prefixes=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for url in urls.split(','):
            url = url.strip()
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

        try:
            self.allowed_prefixes += [ p.strip() for p in prefixes.split(',') ]
        except AttributeError:
            pass
        
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