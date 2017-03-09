# -*- coding: utf-8 -*-
import json
from urlparse import urljoin

from scrapy import Request, Selector
import scrapy
from scrapy.shell import inspect_response

from remotor.items import JobItem


class LandingjobsSpider(scrapy.Spider):
    root = 'https://landing.jobs'
    name = "landingjobs"
    allowed_domains = ["landing.jobs"]
    start_urls = [
        'https://landing.jobs/offers/search.json?page=1&q=python&full_remote=true']

    def parse(self, response):
        data = json.loads(response.text)
        joblinks = [job['url'] for job in data['offers']]
        for joblink in joblinks:
            request = Request(
                urljoin(self.root, joblink),
                callback=self.parse_job,
                )
            yield request

    def parse_job(self, response):
        """Parse a joblink into a JobItem.
        """
#        inspect_response(response, self)
        s = Selector(response)
        item = JobItem()
        item['url'] = response.url
        item['title'] = s.css('h1::text').extract_first()
        item['text'] = s.xpath(
            '//section[@class="ld-job-details"]//text()').extract()
        item['text'].extend(s.xpath(
            '//section[@class="ld-job-offer-section"]//text()').extract())
        yield item
