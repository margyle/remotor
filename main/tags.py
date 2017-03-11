import requests

url = "https://api.stackexchange.com/2.2/tags?page={p}&pagesize=100&order=desc&sort=popular&site=stackoverflow"
tags = []
for p in range(1, 11):
    res = requests.get(url.format(**locals()))
    res = res.json()
    tags.extend(item['name'] for item in res['items'])
print(tags)
