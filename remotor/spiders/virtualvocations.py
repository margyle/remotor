# -*- coding: utf-8 -*-
"""Scrape jobs from virtualvocations.com.
"""
from urlparse import urljoin

from scrapy import FormRequest, Request, Selector
import scrapy

from remotor.items import JobItem


class VirtualvocationsSpider(scrapy.Spider):
    """Spider for virtualvocations.com

    This is a two-layer site with a pagination page, with links to the ads from
    the numbered pages. The first query is a POST request which means we use
    start_requests() rather than start_urls.

    """
    name = "virtualvocations"
    root = "https://www.virtualvocations.com"
    allowed_domains = ["www.virtualvocations.com"]

    job_selector = (
        '//a[starts-with(@href, "{0}/job/")]/@href'.format(root))

    def start_requests(self):
        """Submit a POST request with our query parameters.
        """
        return [
            FormRequest("https://www.virtualvocations.com/jobs/",
                formdata={'search': 'python', 'location': 'remote'},
                callback=self.parse)
                ]

    def parse(self, response):
        """Get the pagination links and hand them off.
        """
        s = Selector(response)
        pagination = s.css('.pagination')
        pagelinks = [response.url]
        pagelinks.extend(pagination.xpath(
            '//a[contains(@href, "l-remote/p-")]/@href').extract())
        for pagelink in pagelinks:
            request = Request(
                urljoin(self.root, pagelink),
                callback=self.parse_jobspage,
                dont_filter=True,
                )
            yield request

    def parse_jobspage(self, response):
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
        item['url'] = response.url
        item['site'] = 'VirtualVocations'
        item['title'] = s.css('h1::text').extract_first()
        item['text'] = s.xpath('//div[@id="job_details"]//text()').extract()
        yield item
