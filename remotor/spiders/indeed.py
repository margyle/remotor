# -*- coding: utf-8 -*-
from urlparse import urljoin

from scrapy import Request, Selector
import scrapy

from remotor.items import JobItem


class IndeedSpider(scrapy.Spider):
    root = 'https://www.indeed.com'
    name = "indeed"
    allowed_domains = ["www.indeed.com"]
    start_urls = ['https://www.indeed.com/jobs?q=python&l=Remote']

    job_selector = '.row, .result'

    def parse(self, response):
        """Get the joblinks and hand them off.
        """
        s = Selector(response)
        jobs = s.css(self.job_selector)
        for job in jobs:
            joblink = job.xpath('h2/a/@href').extract_first()
            if not joblink:
                continue
            item = JobItem()
            item['url'] = urljoin(self.root, joblink)
            item['title'] = job.xpath('h2/a/@title').extract_first()
            item['text'] = job.xpath(
                'table//span[@class="summary"]/text()').extract()
            request = Request(
                item['url'],
                callback=self.parse_job,
                meta={'item': item},
                )
            yield request

    def parse_job(self, response):
        """Parse a joblink into a JobItem.
        """
        item = response.meta['item']
        s = Selector(response)
        item['text'].extend(s.xpath('//p/text()').extract())
        item['text'].extend(s.xpath('//ul/text()').extract())
        item['text'].extend(s.xpath('//span/text()').extract())
        yield item
