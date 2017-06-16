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
        item['date_added'] = parse_time(
            s.xpath('//h3[class="job-begin-date"]/text()'))
        yield item

def parse_time(text):
    text = text.replace('Posted', '').strip()
    patterns = {
        "now": '-timedelta(minutes=0)',
        "a minute ago":'-timedelta(minutes=1)',
        "an hour ago":'-timedelta(hours=1)',
                }
    if text in patterns:
        return datetime.now() + eval(patterns[text])
    formats = {
        r'(\d*) seconds ago':"-timedelta(seconds=int(re.findall(r'(\d*) seconds ago', text)[0]))",
        r'(\d*) minutes ago':"-timedelta(minutes=int(re.findall(r'(\d*) minutes ago', text)[0]))",
        r'(\d*) hours ago':"-timedelta(hours=int(re.findall(r'(\d*) hours ago', text)[0]))",
#        r"%-d day, %-H hour ago": 'datetime.strptime("%-d day, %-H hour ago", text)',
#        r"%-d days ago": 'datetime.strptime("%-d days ago", text)',
#        r"%-d days, %-H hour ago": 'datetime.strptime("%-d days, %-H hour ago", text)',
#        r"%-d day, %-H hours ago": 'datetime.strptime("%-d day, %-H hours ago", text)',
#        r"%-d days, %-H hours ago": 'datetime.strptime("%-d days, %-H hours ago", text)',
    }
    for f in formats:
        try:
            return(eval(formats[f]), f)
        except IndexError as e:
            print(e)
            continue

def test_parse_time():
    tests = [
        'Posted 4 hours ago',
        ]
    delta, f = parse_time(tests[0])
    assert(parse_time(tests[0])[0] == -timedelta(hours=4))
