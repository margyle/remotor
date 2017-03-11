# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JobItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
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
