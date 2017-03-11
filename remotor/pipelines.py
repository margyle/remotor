# -*- coding: utf-8 -*-
from datetime import datetime
import re

import pymongo
from scrapy.conf import settings
from scrapy.exceptions import DropItem
from scrapy.mail import MailSender

from main.techs import get_tech


def clean_text(text):
    normalised = (re.sub(r'\s+', ' ', t) for t in text)
    normalised = ' '.join(t.strip().lower() for t in normalised if t != ' ')
    return normalised


class RemotorPipeline(object):

    def process_item(self, item, spider):
        item['text'] = clean_text(item['text'])
        item['technologies'] = get_tech(item['text'])
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
        # check if already in the database
        stored = self.jobs_collection.find_one({'url': item['url']})
        valid = True
        for data in item:
            if not data:
                valid = False
                raise DropItem("Missing {0}!".format(data))
        if valid:
            if stored:
                # if so, check date added
                stored['times_seen'] += 1
                stored['to_send'] = stored['times_seen'] % 56 == 0
                self.jobs_collection.update(
                    {'_id': stored['_id']}, dict(stored), False)
                spider.logger.debug(
                    "{0} updated in Jobs database!".format(type(item)))
            else:
                # if not, add date to item
                item['date_added'] = datetime.now().isoformat()
                item['times_seen'] = 1
                item['to_send'] = True
                self.jobs_collection.insert(item)
                spider.logger.debug(
                    "{0} added to Jobs database!".format(type(item)))
        return item


class EmailPipeline(object):

    mailer = MailSender(
        smtphost='smtp.gmail.com',
        mailfrom='remotr.jobs@gmail.com',
        smtpport=587,
        smtpuser="remotr.jobs@gmail.com",
        smtppass="rB078dIQed83!Vur",
        )

    def process_item(self, item, spider):
        if not item.get('to_send'):
            return
        techs = set(t for t in item['technologies'])
        desired = set(['python', 'scrapy'])
        if not techs.intersection(desired):
            item['to_send'] = False
        if item['to_send']:
            title = item['title'].encode('utf-8')
            techs = ' - '.join(item['technologies']).encode('utf-8')
            self.mailer.send(
                to=["jamiebull1@gmail.com"],
                subject='{title}: {techs}'.format(**locals()),
                body=item['url'] + '\r\n' + item['text'].encode('utf-8'),
                charset='utf-8',
                )
