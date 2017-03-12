# -*- coding: utf-8 -*-
from datetime import datetime
import os
import re
import time

import pymongo
from scrapy.conf import settings
from scrapy.exceptions import DropItem
from scrapy.mail import MailSender

from main.techs import get_tech


def clean_text(text):
    """Remove duplicated whitespace from text and join as one long string.
    """
    normalised = (re.sub(r'\s+', ' ', t) for t in text)
    normalised = ' '.join(t.strip().lower() for t in normalised if t != ' ')
    return normalised


class RemotorPipeline(object):
    """Basic processing of the JobItem.
    """
    def process_item(self, item, spider):
        """Clean the text and identify technologies in the ad.
        """
        item['text'] = clean_text(item['text'])
        item['technologies'] = get_tech(item['text'])
        return item


class MongoDBPipeline(object):
    """Pass JobItem into MongoDB fr storage.
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
                # if so, check date added
                stored['times_seen'] += 1
                self.jobs_collection.update(
                    {'_id': stored['_id']}, dict(stored), False)
                spider.logger.debug(
                    "{0} updated in Jobs database!".format(type(item)))
            else:
                # if not, add date to item
                item['date_added'] = datetime.now().isoformat()
                item['times_seen'] = 0
                self.jobs_collection.insert(item)
                spider.logger.debug(
                    "{0} added to Jobs database!".format(type(item)))
        return item


class EmailPipeline(object):
    """Email out job if it meets our requirements.
    """

    mailer = MailSender(
        smtphost='smtp.gmail.com',
        mailfrom=os.environ.get('BOT_EMAIL'),
        smtpport=os.environ.get('BOT_SMTP_PORT'),
        smtpuser=os.environ.get('BOT_EMAIL'),
        smtppass=os.environ.get('BOT_PASSWORD'),
        )

    def process_item(self, item, spider):
        """Check if requirements are met, and if so send email.
        """
        to_send = item['times_seen'] % (24 * 7) == 0  # once a week
        if not to_send:
            return
        techs = set(t for t in item['technologies'])
        desired = set(os.environ.get('DESIRED_TECHS').split(','))
        if not techs.intersection(desired):  # check for the desired techs
            return
        time.sleep(2)  # don't fire out too many emails at once
        title = item['title'].encode('utf-8')
        techs = ' - '.join(item['technologies']).encode('utf-8')
        self.mailer.send(
            to=[os.environ.get('USER_EMAIL')],
            subject='{title}: {techs}'.format(**locals()),
            body=item['url'] + '\r\n' + item['text'].encode('utf-8'),
            charset='utf-8',
            )
