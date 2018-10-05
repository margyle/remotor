# -*- coding: utf-8 -*-
"""Scrape jobs from jobspresso.co.
"""
import datetime
import json
from urllib.parse import urljoin

from scrapy import Selector
import scrapy
from scrapy.http import Request

from remotor.items import JobItem
from remotor import utilities


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
        response = utilities.build_response(html)
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
        try:
            posted = s.xpath('//date/text()').extract_first()
            item['date_posted'] = parse_time(posted).isoformat()
        except Exception as e:
            self.logger.error(e)
        yield item


def parse_time(text, now=None):
    """Parse date in the format "Posted <month> <day>"."""
    if not now:
        now = datetime.datetime.now()
    this_year = now.year
    parsed = datetime.datetime.strptime(text, 'Posted %B %d')
    if (parsed.month, parsed.day) == (now.month, now.day):
        return datetime.datetime.now()  # add the time
    if datetime.datetime(this_year, parsed.month, parsed.day) <= now:
        return datetime.datetime(this_year, parsed.month, parsed.day)
    else:
        return datetime.datetime(this_year - 1, parsed.month, parsed.day)


def test_parse_time():
    tests = [('Posted June 20', datetime.datetime(2017, 6, 20)),
             ('Posted June 21', datetime.datetime(2016, 6, 21)),
             ]
    now = datetime.datetime(2017, 6, 20)
    for test in tests:
        assert parse_time(test[0], now) == test[1]

