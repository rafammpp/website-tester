import scrapy


class BrokenLinksSpider(scrapy.Spider):
    name = 'brokenlink-checker'
    handle_httpstatus_list = 404, 500,
    allowed_domains = ['127.0.0.1:8000']

    def __init__(self, site, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = [site]
        try:
            self.DOMAIN = site.split('//')[1]
        except IndexError:
            self.DOMAIN = site

        self.visited_urls = []


    def parse(self, response):
        if response.status in self.handle_httpstatus_list:
            item = {}
            item['url'] = response.url
            item['prev_page'] = response.meta['prev_url']
            item['prev_link_url'] = response.meta['prev_href']
            item['prev_link_text'] = response.meta['prev_link_text']
            item['status'] = response.status

            yield item

        if self.DOMAIN in response.url and response.url not in self.visited_urls:
            for link in response.css('a'):
                href = link.xpath('@href').extract()
                text = link.xpath('text()').extract()
                if href: # maybe should show an error if no href
                    self.visited_urls.append(href)
                    yield response.follow(link, self.parse, meta={
                        'prev_link_text': text,
                        'prev_href': href,
                        'prev_url': response.url,
                    })