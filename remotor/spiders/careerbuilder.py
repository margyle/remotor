# -*- coding: utf-8 -*-
"""Scrape jobs from careerbuilder.com.
"""
from datetime import datetime, timedelta
import re
from urlparse import urljoin

from scrapy import Request, Selector
import scrapy

from remotor.items import JobItem
from remotor.spiders import utilities


class CareerbuilderSpider(scrapy.Spider):
    """Spider for careerbuilder.com.

    This is a simple site with a single page of jobs, with links to the ads.

    """
    name = "careerbuilder"
    root = 'http://www.careerbuilder.com'
    allowed_domains = ["www.careerbuilder.com"]
    start_urls = ['http://www.careerbuilder.com/jobs-remote-python']

    job_selector = '//a[starts-with(@href, "/job/")]/@href'

    def parse(self, response):
        """Get the joblinks and hand them off.
        """
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
        item['url'] = response.url.split('?')[0]
        item['site'] = 'CareerBuilder'
        item['title'] = s.css('h1::text').extract_first()
        item['text'] = s.css('.job-facts::text').extract()
        item['text'].extend(s.css('.item').css('.tag::text').extract())
        item['text'].extend(s.css('.description::text').extract())
        try:
            posted = s.xpath(
                '//h3[@id="job-begin-date"]/text()').extract_first()
            item['date_added'] = utilities.naturaltime(
                posted.replace('Posted ', '')).isotime()
        except Exception as e:
            self.logger.error(e)
        yield item
