# -*- coding: utf-8 -*-
import scrapy


class WwrSpider(scrapy.Spider):
    name = "wwr"
    allowed_domains = ["weworkremotely.com"]
    start_urls = ['http://weworkremotely.com/']

    def parse(self, response):
        pass
