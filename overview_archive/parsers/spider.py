import scrapy

class GithubSpider(scrapy.Spider):
    name = 'base_spider'

    def __init__(self, category=None, *args, **kwargs):
        super(MySpider, self).__init__(*args, **kwargs)
        self.start_urls = ['http://www.example.com/categories/%s' % category]
