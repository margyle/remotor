# -*- coding: utf-8 -*-
from urlparse import urljoin

from scrapy import FormRequest, Request, Selector
import scrapy
from scrapy.shell import inspect_response

from remotor.items import JobItem


class VirtualvocationsSpider(scrapy.Spider):
    root = "https://www.virtualvocations.com"
    name = "virtualvocations"
    allowed_domains = ["www.virtualvocations.com"]

    job_selector = (
        '//a[starts-with(@href, "{0}/job/")]/@href'.format(root))

    def start_requests(self):
        return [
            FormRequest("https://www.virtualvocations.com/jobs/",
                formdata={'search': 'python', 'location': 'remote'},
                callback=self.parse)
                ]

    def parse(self, response):
        """Get the joblinks and hand them off.
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
        s = Selector(response)
        joblinks = s.xpath(self.job_selector).extract()
#        for joblink in joblinks[:1]:
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
        item['title'] = s.css('h1::text').extract_first()
        item['text'] = s.xpath('//div[@id="job_details"]//text()').extract()
        yield item
