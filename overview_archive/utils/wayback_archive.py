#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of overview-archive, a tool for archiving and tagging resoruces.
# Copyright © 1991 Asad Dhamani
# Copyright © 2015 seamus tuohy, <stuohy@internews.org>
#
# GNU GENERAL PUBLIC LICENSE - Version 2, June 1991
# https://github.com/dhamaniasad/waybackcheck/tree/2697166c784f09678665245ea9eb3322b92ea88e

from urllib.request import urlopen
from urllib.request import urlparse
from urllib.error import HTTPError
import json

# command line
import argparse

# logging
import logging
log = logging.getLogger("oa.{0}".format(__name__))


def try_safely(remote_url):
    try:
        if urlparse(remote_url):
            try:
                log.info("Attempting to archive url.")
                archive = get(remote_url)
                log.info("Archive Created.")
                return archive
            except HTTPError:
                log.info("Cannot archive object, returning url.")
                return remote_url
    except ValueError as _e:
        log.info("No URL given")
        log.debug(_e)
    log.info("Not a valid URL")
    return remote_url



def get(inputurl):
    # Submit url to wayback machine
    # wayback machine submission url
    wbkurl = "http://web.archive.org/save/"
    # Submit the url
    urlopen(wbkurl+inputurl)

    # Return latest snapshot url
    # wayback machine availability api url
    wbkav = "http://archive.org/wayback/available?url="
    # open wayback availability url
    wbcheck = urlopen(wbkav+inputurl)
    # load json data
    wbcheck_data = wbcheck.read().decode('utf-8')
    log.debug("Data Received from wayback archive: {0}".format(wbcheck_data))
    wbcheckjson = json.loads(wbcheck_data)
    archived_snapshots = wbcheckjson['archived_snapshots']
    latest_snapshot = archived_snapshots['closest']['url']
    return latest_snapshot


def parse_arguments():
    parser = argparse.ArgumentParser("Get a summary of some text")
    parser.add_argument("--url", "-u",
                        help="The url to send to Internet Archives Wayback Machine")
    args = parser.parse_args()
    return args


def main():
    args = parse_arguments()
    try:
        archived_url = get(args.url)
    except HTTPError:
        print(args.url)


if __name__ == '__main__':
    main()
