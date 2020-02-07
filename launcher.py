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
        "Select the version to launch."
    )
    print("Versions:")
    if bundled:
        print("0) Bundled version (Does not update)")
    vs = []
    for num, version in enumerate(versions):
        print("{}) {}".format(num + 1, version))
        vs.append(version)
    selection = int(input(">")) - 1
    #selection = 0
    if selection == -1 and bundled:
        crystalchat.run()
    elif selection < 0 or selection >= len(versions):
        print("Invalid Version")
        sys.exit(1)
    vir = versions[vs[selection]]
    try:
        os.mkdir("versions")
        os.mkdir("versions/{}".format(vir))
    except:
        pass
    url = "https://raw.githubusercontent.com/webmsgr/crystalchat/{}/crystalchat.py".format(vir)
    if vir in os.listdir("./versions") and vir != "master": # only use master (latest) cache if we cant connect
        with open("./versions/{}/cache".format(vir)) as fl:
            rawdata = fl.read()
    else:
        try:
            rawdata = get_request(url)
        except Exception as e:
            if vir in os.listdir("./versions"):
                with open("./versions/{}/cache".format(vir)) as fl:
                    rawdata = fl.read()
            else:
                raise e
    data = compile(rawdata,"crystalchat.py","exec")
    with open("./versions/{}/cache".format(vir),"w") as fl:
        fl.write(rawdata)
    os.chdir("./versions/{}/".format(vir))
    exec(data)
    os.chdir("../..")
    

if __name__ == "__main__":
    main()
