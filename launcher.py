#!/usr/bin/env python3
import argparse
import configparser
import os
import shutil
import tempfile
import urllib.request
import zipfile
import sys

try:
    import crystalchat

    bundled = True
except ImportError as e:
    bundled = False
    cchatmain = None
    if getattr(sys, "frozen", False):
        raise e
vurl = (
    "https://raw.githubusercontent.com/webmsgr/crystalchat4/master/autoupdate/versions"
)


def get_request(url):
    with urllib.request.urlopen(url) as response:
        return response.read().decode()


def loadversions():
    vfile = get_request(vurl)
    parser = configparser.ConfigParser()
    parser.read_string(vfile)
    vmapping = {}
    vreleases = {}
    versions = parser["versions"]
    releases = parser["releases"]
    for item in versions:
        vmapping[item] = versions[item]
    for release in releases:
        vreleases[release] = vmapping.get(releases[release], "?")
    return {x: vreleases[x] for x in vreleases if vreleases[x] != "?"}


def main():
    print("Grabbing versions...")
    versions = loadversions()
    print(
        "Select the version to launch.\nIf not installed, it will be installed.\nIf there is a update, it will be downloaded."
    )
    print("Versions:")
    if bundled:
        print("0) Bundled version (Does not update)")
    for num, version in enumerate(versions):
        print("{}) {}".format(num + 1, version))
    selection = int(input(">")) - 1
    #selection = 0
    if selection == -1 and bundled:
        crystalchat.run()
    elif selection < 0 or selection >= len(versions):
        print("Invalid Version")


if __name__ == "__main__":
    main()
