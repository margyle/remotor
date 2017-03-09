# -*- coding: utf-8 -*-
import json
from urlparse import urljoin

from scrapy import Request, Selector
import scrapy
from scrapy.http import HtmlResponse
from scrapy.shell import inspect_response

from remotor.items import JobItem


def build_response(html):
    request = Request(url='http://dummy.url')

    response = HtmlResponse(url='http://dummy.url',
        request=request,
        body=html,
        encoding='utf-8',
        )
    return response


class RemoteworkingSpider(scrapy.Spider):
    root = 'http://www.remoteworking.co'
    name = "remoteworking"
    allowed_domains = ["remoteworking.co"]
    start_urls = [
        'http://www.remoteworking.co/jm-ajax/get_listings/?search_keywords=python&search_location=&search_categories%5B%5D=&per_page=20',
        ]

    job_selector = (
        '//a[starts-with(@href, "http://www.remoteworking.co/job/")]/@href')


    def parse(self, response):
        data = json.loads(response.text)
        html = data['html']
        response = build_response(html)
        s = Selector(response)
        joblinks = s.xpath(self.job_selector).extract()
        self.logger.info(joblinks)
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
        item['text'] = s.xpath('//div[@itemprop="description"]//text()').extract()
        yield item
