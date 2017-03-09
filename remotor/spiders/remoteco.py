# -*- coding: utf-8 -*-
from urlparse import urljoin

from scrapy import Request, Selector
import scrapy
from scrapy.shell import inspect_response

from remotor.items import JobItem


class RemotecoSpider(scrapy.Spider):
    """Spider for We Work Remotely Python jobs.
    """
    root = "https://weworkremotely.com"

    name = "remoteco"
    allowed_domains = ["remote.co"]
    start_urls = [
        'https://remote.co/jm-ajax/get_listings/?search_keywords=python']
    job_selector = (
        '//a[starts-with(@href, "\\")]/@href')

    def parse(self, response):
        """Get the joblinks and hand them off.
        """
        sel = Selector(response)
        joblinks = sel.xpath(self.job_selector).extract()
        joblinks = clean_links(joblinks)
#        for joblink in list(joblinks)[:1]:
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
        item['company'] = s.xpath(
            '//strong[@itemprop="name"]/text()').extract_first()
        job = s.css('.job-description')
        job.xpath('p[1]')
        item['text'] = s.xpath(
            '//div[@class="job_description"]//text()').extract()
        yield item


def clean_links(links):
    """Generator returning useable links.
    """
    for link in links:
        link = link[2:-1].replace('\\', '')
        if link.startswith('https://remote.co/job/'):
            yield link
