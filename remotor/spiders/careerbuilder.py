# -*- coding: utf-8 -*-
"""Scrape jobs from careerbuilder.com.
"""
from datetime import datetime, timedelta
import re
from urlparse import urljoin

from scrapy import Request, Selector
import scrapy

from remotor.items import JobItem


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
            item['date_added'] = parse_time(
                s.xpath('//h3[class="job-begin-date"]/text()').extract_first())
        except Exception as e:
            self.logger.error(e)
        yield item


def parse_time(text):
    text = text.replace('Posted', '').strip()
    # try the simple patterns
    patterns = {
        "now": '-timedelta(minutes=0)',
        "a minute ago": '-timedelta(minutes=1)',
        "an hour ago": '-timedelta(hours=1)',
        "1 day ago": '-timedelta(days=1)',
                }
    if text in patterns:
        delta = eval(patterns[text])
        parsed = delta + datetime.now()
        return parsed.isoformat()
    # otherwise more complex parsing
    patterns = {
        r'n seconds ago':"-timedelta(seconds=int(re.findall(r'^(\d*) seconds ago', text)[0]))",
        r'n minutes ago':"-timedelta(minutes=int(re.findall(r'^(\d*) minutes ago', text)[0]))",
        r'n hours ago':"-timedelta(hours=int(re.findall(r'^(\d*) hours ago', text)[0]))",
        r"n days ago": "-timedelta(days=int(re.findall(r'^(\d*) days ago', text)[0]))",
        r"1 day, 1 hour ago": "-timedelta(days=int(re.findall(r'^(\d*) day,', text)[0]), hours=int(re.findall(r'(\d*) hour ago$', text)[0]))",
        r"2 days, 1 hour ago": "-timedelta(days=int(re.findall(r'^(\d*) days,', text)[0]), hours=int(re.findall(r'(\d*) hour ago$', text)[0]))",
        r"1 day, 2 hours ago": "-timedelta(days=int(re.findall(r'^(\d*) day,', text)[0]), hours=int(re.findall(r'(\d*) hours ago$', text)[0]))",
        r"n days, n hours ago": "-timedelta(days=int(re.findall(r'^(\d*) days,', text)[0]), hours=int(re.findall(r'(\d*) hours ago$', text)[0]))",
    }
    for pattern in patterns:
        try:
            delta = eval(patterns[pattern])
            parsed = delta + datetime.now()
            return parsed.isoformat()
        except IndexError as e:
            continue

def test_parse_time():
    tests = [
        ('Posted 57 seconds ago', -timedelta(seconds=57)),
        ('Posted 4 minutes ago', -timedelta(minutes=4)),
        ('Posted 4 hours ago', -timedelta(hours=4)),
        ('Posted an hour ago', -timedelta(hours=1)),
        ('Posted a minute ago', -timedelta(minutes=1)),
        ('Posted now', -timedelta(hours=0)),
        ('Posted 1 day ago', -timedelta(days=1)),
        ('Posted 2 days ago', -timedelta(days=2)),
        ('Posted 1 day ago', -timedelta(days=1)),
        ('Posted 1 day, 1 hour ago', -timedelta(days=1, hours=1)),
        ('Posted 1 day, 2 hours ago', -timedelta(days=1, hours=2)),
        ('Posted 2 days, 1 hour ago', -timedelta(days=2, hours=1)),
        ('Posted 2 days, 2 hours ago', -timedelta(days=2, hours=2)),
        ]
    for test in tests:
        try:
            delta = parse_time(test[0])
            assert(delta == datetime.now() + test[1])
        except (AssertionError, TypeError, KeyError, ValueError) as e:
            print(test)
            print(e)
            raise