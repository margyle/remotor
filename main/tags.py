"""Fetch the top 1000 tags from StackOverflow for use in tech identification.

This is a script used in development. We save it in case we want to harvest
tags from a different StackExchange site in future.

"""
import requests

data = {
    'pagesize': '100',
    'order': 'desc',
    'sort': 'popular',
    'site': 'stackoverflow',
    }
url = "https://api.stackexchange.com/2.2/tags"
tags = []
for p in range(1, 11):
    data['page'] = p
    res = requests.get(url.format(**locals()), params=data)
    res = res.json()
    tags.extend(item['name'] for item in res['items'])
print(tags)
