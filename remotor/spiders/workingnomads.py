# -*- coding: utf-8 -*-
"""Scrape jobs from workingnomads.co.
"""
import json

import html2text
import scrapy

from remotor.items import JobItem


class WorkingnomadsSpider(scrapy.Spider):
    """Spider for workingnomads.co

    This is a simple site with a JSON object of jobs containing all the details
    of the job with no need to follow any links.

    """
    name = "workingnomads"
    allowed_domains = ["www.workingnomads.co"]
    start_urls = [
        'https://www.workingnomads.co/jobsapi/job/_search?sort=premium:desc,pub_date:desc&_source=company,category_name,description,instructions,id,external_id,slug,title,pub_date,tags,source,apply_url,premium&size=20&from=0&q=(tags:%22python%22)',
        ]

    def parse(self, response):
        data = json.loads(response.text)
        converter = html2text.HTML2Text()
        for job in data['hits']['hits']:
            item = JobItem()
            try:
                item['url'] = (
                    "www.workingnomads.co/jobs/{0}".format(job.get('apply_url')))
            except KeyError:
                item['url'] = (
                    "www.workingnomads.co/jobs/{0}".format(job['_source']['slug']))
            item['site'] = 'WorkingNomads'
            item['text'] = converter.handle(job['_source']['description'])
            item['text'] = [item['text'] + ' '.join(item.get('tags', []))]
            yield item
