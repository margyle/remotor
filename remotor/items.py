# -*- coding: utf-8 -*-
"""Just a single item, JobItem.
"""
import scrapy


class JobItem(scrapy.Item):
    """Item representing a job ad.
    """
    _id = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    company = scrapy.Field()
    technologies = scrapy.Field()
    location = scrapy.Field()
    text = scrapy.Field()
    date_added = scrapy.Field()
    date_added = scrapy.Field()
    times_seen = scrapy.Field()
    to_send = scrapy.Field()
