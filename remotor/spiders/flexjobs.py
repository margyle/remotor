# -*- coding: utf-8 -*-
"""Scrape jobs from flexjobs.com.
"""
import datetime
import re
from urlparse import urljoin

from scrapy import Request, Selector
import scrapy

from remotor.items import JobItem


class FlexjobsSpider(scrapy.Spider):
    """Spider for flexjobs.com

    This is a two-layer site with a pagination page, with links to the ads from
    the numbered pages.

    """
    name = "flexjobs"
    root = "https://www.flexjobs.com"
    allowed_domains = ["www.flexjobs.com"]
    start_urls = [
        'https://www.flexjobs.com/search?search=python&location=remote']

    job_selector = (
        '//div[@id="joblistarea"]//a[starts-with(@href, "/publicjobs/")]/@href')

    def parse(self, response):
        """Get the pagination links and hand them off.
        """
        s = Selector(response)
        pagination = s.css('.pagination')
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
        item['site'] = 'FlexJobs'
        item['title'] = s.css('h1::text').extract_first()
        item['text'] = s.css('#job-description p::text').extract()
        item['text'].extend(s.css('td::text, th::text').extract())
        try:
            item['date_added'] = parse_time(item['text'])
        except Exception as e:
            self.logger.error(e)
        yield item


def parse_time(text):
    """Extract the date posted from the ad text."""
    matches = re.findall(r'\d{2}\/\d{2}\/\d{2}', ''.join(text))
    if matches:
        date = matches[0]
        parsed = datetime.datetime.strptime(date, '%m/%d/%y').isoformat()
        return parsed


def test_parse_time():
    tests = [
        ('afafs 10/01/17', '2017-10-01T00:00:00'),
        ('10/01/17 afafs', '2017-10-01T00:00:00'),
        ('afafs 10/01/17 afafs', '2017-10-01T00:00:00'),
        ('afafs ', None),
        ]
    for test in tests:
        try:
            time = parse_time(test[0])
            assert(time == test[1])
        except (AssertionError, TypeError, KeyError, ValueError) as e:
            print(test)
            print(e)
            raise