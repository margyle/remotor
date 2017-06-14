# -*- coding: utf-8 -*-
"""Scrape jobs from remoteworking.co.
"""
import json
from urlparse import urljoin

from scrapy import Request, Selector
import scrapy

from remotor.items import JobItem
from remotor.spiders.utilities import build_response


class RemoteworkingSpider(scrapy.Spider):
    """Spider for remoteworking.co

    This is a simple site with a JSON object of jobs, with html containing
    links to the ads.

    """
    name = "remoteworking"
    root = 'http://www.remoteworking.co'
    allowed_domains = ["remoteworking.co"]
    start_urls = [
        'http://www.remoteworking.co/jm-ajax/get_listings/?search_keywords=python&search_location=&search_categories%5B%5D=&per_page=20',
        ]

    job_selector = (
        '//a[starts-with(@href, "http://www.remoteworking.co/job/")]/@href')


    def parse(self, response):
        """Get the joblinks and hand them off.
        """
        data = json.loads(response.text)
        html = data['html']
        response = build_response(html)
        s = Selector(response)
        joblinks = s.xpath(self.job_selector).extract()
        for joblink in joblinks:
            request = Request(
                urljoin(self.root, joblink),
                callback=self.parse_job,
                )
            yield request

    def parse_job(self, response):
        """Parse a joblink into a JobItem.
        """
        s = Selector(response)
        item = JobItem()
        item['url'] = response.url
        item['site'] = 'RemoteWorking'
        item['title'] = s.css('h1::text').extract_first()
        item['html'] = s.xpath(
            '//div[@itemprop="description"]').extract()
        item['text'] = s.xpath(
            '//div[@itemprop="description"]//text()').extract()
        yield item
