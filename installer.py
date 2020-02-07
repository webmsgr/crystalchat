#!/usr/bin/env python3
import urllib.request
import configparser
import shutil
import tempfile

vurl = "https://raw.githubusercontent.com/webmsgr/crystalchat4/master/autoupdate/versions"
def get_request(url):
    with urllib.request.urlopen(url) as response:
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            shutil.copyfileobj(response, tmp_file)
    return tmp_file

