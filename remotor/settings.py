# -*- coding: utf-8 -*-
"""Scrapy settings for remotor project

For simplicity, this file contains only settings considered important or
commonly used. You can find more settings consulting the documentation:
    http://doc.scrapy.org/en/latest/topics/settings.html
    http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
    http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
"""
BOT_NAME = 'remotor'

SPIDER_MODULES = ['remotor.spiders']
NEWSPIDER_MODULE = 'remotor.spiders'

LOG_SHORT_NAME = True
LOG_LEVEL = 'INFO'
# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Hire me for scraping jobs! (jamiebull1@gmail.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False
# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'remotor.pipelines.RemotorPipeline': 300,
    'remotor.pipelines.MongoDBPipeline': 400,
    'remotor.pipelines.EmailPipeline': 500,
}

MONGODB_JOBS_COLLECTION = "jobs"

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
# The initial download delay
AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
