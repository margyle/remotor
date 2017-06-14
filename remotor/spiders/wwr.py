# -*- coding: utf-8 -*-
"""Scrape jobs from weworkremotely.com.
"""
from urlparse import urljoin

from scrapy import Request, Selector
import scrapy

from remotor.items import JobItem


class WwrSpider(scrapy.Spider):
    """Spider for weworkremotely.com

    This is a simple site with a page of jobs containing links to the ads.

    """
    name = "wwr"
    root = "https://weworkremotely.com"
    allowed_domains = ["weworkremotely.com"]
    start_urls = ['https://weworkremotely.com/jobs/search?term=python']

    job_selector = '//a[starts-with(@href, "/jobs/")]/@href'

    def parse(self, response):
        """Get the joblinks and hand them off.
        """
        self.logger.info("URI: %s" % self.settings['MONGODB_URI'])
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
        item['site'] = 'WeWorkRemotely'
        item['title'] = s.css('h1::text').extract_first()
        item['company'] = s.css('.company::text').extract_first()
        item['location'] = s.css('.location::text').extract_first()
        item['text'] = s.css(
            '.listing-container').xpath('div/text()').extract()
        item['text'].extend(s.css(
            '.listing-container').xpath('ul/li/text()').extract())
        yield item
