# -*- coding: utf-8 -*-
from urllib.parse import urljoin

from scrapy import Request, Selector
import scrapy

from remotor.items import JobItem
from remotor import utilities


class StackoverflowSpider(scrapy.Spider):
    name = "stackoverflow"
    root = "https://stackoverflow.com"
    allowed_domains = ["stackoverflow.com"]
    start_urls = ['https://stackoverflow.com/jobs?l=remote']
    job_selector = '//div[contains(@class, "-job-item")]'

    def parse(self, response):
        """Get the joblinks and hand them off.
        """
        s = Selector(response)
        jobs = s.xpath(self.job_selector)
        for job in jobs:
            item = JobItem()
            joblink = job.xpath('//a[@class="job-link"]/@href').extract_first()
            if not joblink:
                continue
            item = JobItem()
            item['url'] = urljoin(self.root, joblink)
            item['site'] = 'StackOverflow'
            item['title'] = job.xpath('//h2/a/@title').extract_first()
            item['text'] = job.xpath(
                '//a[@class="post-tag"]/text()').extract()
            try:
                posted = s.xpath(
                    '//p[@class="-posted-date"]/text()').extract_first()
                parsed = utilities.stackoverflowtime(posted).isoformat()
                item['date_posted'] = parsed
            except Exception as e:
                self.logger.error(e)
            request = Request(
                item['url'],
                callback=self.parse_job,
                meta={'item': item},
                )
            yield request

    def parse_job(self, response):
        s = Selector(response)
        item = response.meta['item']
        item['text'].extend(
            s.xpath('//span[@class="-badge"]//text()').extract())
        item['text'].extend(
            s.xpath('//div[@class="description"]//text()').extract())
        yield item
