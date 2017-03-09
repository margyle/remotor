# -*- coding: utf-8 -*-
from urlparse import urljoin

from scrapy import Request, Selector
import scrapy
from scrapy.shell import inspect_response

from remotor.items import JobItem


class FlexjobsSpider(scrapy.Spider):
    root = "https://www.flexjobs.com"
    name = "flexjobs"
    allowed_domains = ["www.flexjobs.com"]
    start_urls = [
        'https://www.flexjobs.com/search?search=python&location=remote']

    job_selector = (
        '//div[@id="joblistarea"]//a[starts-with(@href, "/publicjobs/")]/@href')

    def parse(self, response):
        """Get the joblinks and hand them off.
        """
        s = Selector(response)
        pagination = s.css('.pagination')
#        inspect_response(response, self)
        pagelinks = pagination.xpath(
            '//a[contains(@href, "&page=")]/@href').extract()
        for pagelink in pagelinks:
            request = Request(
                urljoin(self.root, pagelink),
                callback=self.parse_jobspage,
                dont_filter=True,
                )
            yield request

    def parse_jobspage(self, response):
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
#        inspect_response(response, self)
        s = Selector(response)
        item = JobItem()
        item['url'] = response.url
        item['title'] = s.css('h1::text').extract_first()
        item['text'] = s.css('#job-description p::text').extract()
        item['text'].extend(s.css('td::text, th::text').extract())
        yield item
