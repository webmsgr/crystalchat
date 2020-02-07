#!/usr/bin/env python3
import urllib.request
import configparser
import shutil
import tempfile
import argparse
import zipfile
import os
vurl = "https://raw.githubusercontent.com/webmsgr/crystalchat4/master/autoupdate/versions"
def get_request(url):
    with urllib.request.urlopen(url) as response:
        tmp_file = tempfile.NamedTemporaryFile()
        shutil.copyfileobj(response, tmp_file)
        tmp_file.seek(0)
        return tmp_file

def loadversions():
    vfile = get_request(vurl)
    parser = configparser.ConfigParser()
    parser.read_file(vfile)
    vmapping = {}
    vreleases = {}
    versions = parser["versions"]
    releases = parser["releases"]
    vfile.close()
    for item in versions:
        vmapping[item] = versions[item]
    for release in releases:
        vreleases[release] = vmapping.get(releases[item],"?")
    return {x:vreleases[x] for x in vreleases if vreleases[x] != "?"}


def main():
    print("Grabbing versions...")
    versions = loadversions()
    print("Versions:")
    for num,version in enumerate(versions):
        print("{}) {}".format(num,version))
        
        
if __name__ == "__main__":
    main()
              
