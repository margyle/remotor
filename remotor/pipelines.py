# -*- coding: utf-8 -*-
from datetime import datetime
import os
import re
import time

import pymongo
from scrapy.conf import settings
from scrapy.exceptions import DropItem

from main.techs import get_tech
import logging


logger = logging.getLogger('__name__')


def clean_text(text):
    """Remove duplicated whitespace from text and join as one long string.
    """
    normalised = (re.sub(r'\s+', ' ', t) for t in text)
    normalised = ' '.join(t.strip().lower() for t in normalised if t != ' ')
    return normalised


def make_presentable(text):
    """Remove duplicated whitespace from text and format it to be presentable.
    """
    normalised = (re.sub(r'[^\S\r\n]', ' ', t) for t in text)
    normalised = ''.join(t for t in normalised)

    return normalised

# to move into separate handling later
DELETE_PHRASES = [
    'Apply Save this job Save Delete',
    ]

class RemotorPipeline(object):
    """Basic processing of the JobItem.
    """
    def process_item(self, item, spider):
        """Clean the text and title and identify technologies in the ad.
        """
        item['presentable'] = make_presentable(item['text'])
        item['text'] = clean_text(item['text'])
        for phrase in DELETE_PHRASES:
            item['text'] = item['text'].replace(phrase, '')
        title = clean_text([item['title']])
        item['technologies'] = get_tech(title)
        item['technologies'].extend(get_tech(item['text']))
        return item


class MongoDBPipeline(object):
    """Pass JobItem into MongoDB for storage.
    """
    def __init__(self):
        """Connect to the database.
        """
        client = pymongo.MongoClient(
            os.environ.get('MONGODB_URI'),
            connectTimeoutMS=30000,
            socketTimeoutMS=None,
            socketKeepAlive=True
            )
        db = client.get_default_database()
        self.jobs_collection = db[settings['MONGODB_JOBS_COLLECTION']]

    def process_item(self, item, spider):
        """Check if we need to store the item and decide whether to notify.
        """
        # check if already in the database
        stored = self.jobs_collection.find_one({'url': item['url']})
        valid = True
        for data in item:
            if not data:
                valid = False
                raise DropItem("Missing {0}!".format(data))
        if valid:
            if stored:
                item = stored
                item['times_seen'] += 1
                self.jobs_collection.update(
                    {'_id': item['_id']}, dict(item), False)
            else:
                # if not (and if not already set), add date to item
                if not item.get('date_added', False):
                    item['date_added'] = datetime.now().isoformat()
                if not item.get('date_posted', False):
                    item['date_posted'] = datetime.now().isoformat()
                item['times_seen'] = 0
                self.jobs_collection.insert(item)
        return item


class EmailPipeline(object):
    """Email out job if it meets our requirements.
    """
    mailer = settings['MAILER']

    def __init__(self, stats):
        self.stats = stats

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.stats)

    def process_item(self, item, spider):
        """Check if requirements are met, and if so send email.
        """
        self.stats.set_value('ads/spider', spider.name)
        to_send = item['times_seen'] == 0  # once only
        if not to_send:
            self.stats.inc_value('ads/repeated')
            return
        techs = set(t for t in item['technologies'])
        desired = set(os.environ.get('DESIRED_TECHS').split(','))
        if not techs.intersection(desired):  # check for the desired techs
            self.stats.inc_value('ads/no_desired_techs')
            return
        ignored = set(os.environ.get('IGNORED_TECHS').split(','))
        if techs.intersection(ignored):  # check for absence of ignored techs
            self.stats.inc_value('ads/has_ignored_techs')
            return
        time.sleep(2)  # don't fire out too many emails at once
        title = item['title'].encode('utf-8')
        techs = ' - '.join(item['technologies']).encode('utf-8')
        text = item['text'].encode('utf-8')
        self.mailer.send(
            to=[os.environ.get('USER_EMAIL')],
            subject='{title}: {techs}'.format(**locals()),
            body=item['url'].encode('utf-8') + '\r\n' + text,
            charset='utf-8',
            )
        self.stats.inc_value('ads/emailed')
