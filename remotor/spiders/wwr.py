# -*- coding: utf-8 -*-
"""Scrape jobs from weworkremotely.com.
"""
import datetime
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
        try:
            posted = s.xpath('//div/h3/text()').extract_first()
            item['date_added'] = parse_date(posted).isoformat()
        except Exception as e:
            self.logger.error(e)
        yield item


def parse_date(text, now=None):
    """Parse date in the format "Posted <month> <day>"."""
    if not now:
        now = datetime.datetime.now()
    this_year = now.year
    parsed = datetime.datetime.strptime(text, 'Posted %b %d')
    if (parsed.month, parsed.day) == (now.month, now.day):
        return datetime.datetime.now()  # add the time
    if datetime.datetime(this_year, parsed.month, parsed.day) <= now:
        return datetime.datetime(this_year, parsed.month, parsed.day)
    else:
        return datetime.datetime(this_year - 1, parsed.month, parsed.day)


def test_parse_time():
    tests = [('Posted Jun 20', datetime.datetime(2017, 6, 20)),
             ('Posted Jun 21', datetime.datetime(2016, 6, 21)),
             ]
    now = datetime.datetime(2017, 6, 20)
    for posted, expected in tests:
        res = parse_date(posted, now)
        assert datetime.datetime(res.year, res.month, res.day) == expected

