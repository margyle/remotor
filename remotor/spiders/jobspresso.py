# -*- coding: utf-8 -*-
"""Scrape jobs from jobspresso.co.
"""
import json
from urlparse import urljoin

from scrapy import Selector
import scrapy
from scrapy.http import Request

from remotor.items import JobItem
from remotor.spiders.utilities import build_response


class JobspressoSpider(scrapy.Spider):
    """Spider for jobspresso.co

    This is a simple site with a JSON object including html, with links to the
    ads.

    """
    name = "jobspresso"
    root = 'https://jobspresso.co'
    allowed_domains = ["jobspresso.co"]
    start_urls = [
        'https://jobspresso.co/jm-ajax/get_listings/?search_keywords=remote',
        ]

    job_selector = (
        '//a[starts-with(@href, "https://jobspresso.co/job/")]/@href')


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
        item['site'] = 'Jobspresso'
        item['title'] = s.xpath(
            '//h2[@class="page-title"]//text()').extract_first()
        item['text'] = s.xpath(
            '//div[@itemprop="description"]//text()').extract()
        yield item
