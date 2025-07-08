import requests

PROXY = {
    "http": "http://keyvidai-rotate:MLf8p3R6DEHu7@p.webshare.io:80/",
    "https": "http://keyvidai-rotate:MLf8p3R6DEHu7@p.webshare.io:80/"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def proxy_get(url, **kwargs):
    return requests.get(url, proxies=PROXY, headers=HEADERS, timeout=10, **kwargs)

def proxy_post(url, **kwargs):
    return requests.post(url, proxies=PROXY, headers=HEADERS, timeout=10, **kwargs)
