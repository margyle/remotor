"""Useful functions to be used by more than one spider.
"""
from scrapy.http import HtmlResponse, Request


def build_response(html):
    request = Request(url='http://dummy.url')

    response = HtmlResponse(url='http://dummy.url',
        request=request,
        body=html,
        encoding='utf-8',
        )
    return response
