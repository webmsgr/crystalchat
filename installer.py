#!/usr/bin/env python3
import urllib.request
def get_request(url):
    with urllib.request.urlopen('http://python.org/') as response:
        data = response.read()
    return data
