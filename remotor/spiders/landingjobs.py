# -*- coding: utf-8 -*-
"""Scrape jobs from landing.jobs.
"""
import json
from urllib.parse import urljoin

from scrapy import Request, Selector
import scrapy

from remotor.items import JobItem


class LandingjobsSpider(scrapy.Spider):
    """Spider for landing.jobs

    This is a simple site with a JSON object of jobs, with url links to the ads.

    """

    name = "landingjobs"
    root = "https://landing.jobs"
    allowed_domains = ["landing.jobs"]
    start_urls = ["https://landing.jobs/jobs/search.json?page=1&remote=true"]

    def parse(self, response):
        """Get the joblinks and hand them off.
        """
        data = json.loads(response.text)
        joblinks = [job["url"] for job in data["offers"]]
        for joblink in joblinks:
            request = Request(urljoin(self.root, joblink), callback=self.parse_job)
            yield request

    def parse_job(self, response):
        """Parse a joblink into a JobItem.
        """
        s = Selector(response)
        item = JobItem()
        item["url"] = response.url
        item["site"] = "LandingJobs"
        item["title"] = s.css("h1::text").extract_first()
        item["text"] = s.xpath('//section[@class="ld-job-details"]//text()').extract()
        item["text"].extend(
            s.xpath('//section[@class="ld-job-offer-section"]//text()').extract()
        )
        yield item
