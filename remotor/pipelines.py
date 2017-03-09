# -*- coding: utf-8 -*-
import pymongo
from scrapy.conf import settings
from scrapy.exceptions import DropItem


# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
class RemotorPipeline(object):
    def process_item(self, item, spider):
        return item


class MongoDBPipeline(object):

    def __init__(self):
        connection = pymongo.MongoClient(
            settings['MONGODB_SERVER'],
            settings['MONGODB_PORT']
        )
        db = connection[settings['MONGODB_DB']]
        self.jobs_collection = db[settings['MONGODB_JOBS_COLLECTION']]

    def process_item(self, item, spider):
        valid = True
        for data in item:
            if not data:
                valid = False
                raise DropItem("Missing {0}!".format(data))
        if valid:
            self.jobs_collection.update(dict(item), dict(item), True)
            spider.logger.debug(
                "{0} added to Jobs database!".format(type(item)))
        return item
