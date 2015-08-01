#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of overview-archive, a tool for archiving and tagging resources.
# Copyright © 2015 seamus tuohy, <stuohy@internews.org>
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the included LICENSE file for details.

# base
import sys

# command line
import argparse

# logging
import logging
log = logging.getLogger("oa.{0}".format(__name__))


# file paths
from os import path, getcwd
from shutil import copy

# network paths
from urllib.parse import urlparse
from urllib.request import urlretrieve
from urllib.error import HTTPError, URLError
from overview_archive.utils import wayback_archive
import scrapy
from overview_archive.parsers import *

def get_w_custom(obj_path):
    #Initialize spiders and pass them the parser NameSpace object
    spiders = [spider(url) for spider in scrapy.Spider.__subclasses__()]


def get_any(obj_path, local_path):
    """
    path (string): The location to use to get the object.
    """
    log.debug("local path is {0}\nobject path is {1}".format(local_path, obj_path))
    # Try as a file
    if path.exists(obj_path) and path.isfile(obj_path):
        log.debug("object is a file. Retreiving now...")
        content_path = get_file(obj_path, local_path)
        return content_path, obj_path
    # Try as an url
    if urlparse(obj_path):
        log.debug("object is a url. Retreiving now...")
        content_path, current_url = get_url(obj_path, local_path)
        return content_path, current_url

    #Move this error down as we add more types of objects to parse
    log.Error("No more types to try.")
    raise ValueError("Path does not lead to a recognized type of object to parse.")

def get_file(file_path, local_path):
    """Get a file at 'file_path' and move it to 'local_path' """
    if path.exists(file_path) and path.isfile(file_path):
        content_path = copy(file_path, local_path)
        return content_path

def get_url(remote_url, local_path):
    # Attempt to Archive the URL
    url = wayback_archive.try_safely(remote_url)
    try:
        log.debug("Attempting to get object")
        local_filename, headers = urlretrieve(url, local_path)
    except URLError as e:
        if hasattr(e, 'reason'):
            log.error('We failed to reach a server.')
            log.error('Reason: ', e.reason)
            raise ValueError("The path provided is invalid")
        elif hasattr(e, 'code'):
            log.error('The server couldn\'t fulfill the request.')
            log.error('Error code: ', e.code)
            raise ValueError("The path provided is invalid")
    return local_filename, url


def main():
    args = parse_arguments()
    set_logging(args.verbose, args.debug)
    path = get_any(args.input_path, args.output_file)
    sys.stdout.write(path)


def set_logging(verbose=False, debug=False):
    logging.basicConfig(level=logging.ERROR)
    if debug == True:
        log.setLevel("DEBUG")
    elif verbose == True:
        log.setLevel("INFO")


def parse_arguments():
    parser = argparse.ArgumentParser("Get a summary of some text")
    parser.add_argument("--input_path", "-i",
                        help="The path to the object to get.")
    parser.add_argument("--output_file", "-o",
                        help="The place to put the plain text",
                        default=getcwd())
    parser.add_argument("--verbose", "-v",
                        help="Turn verbosity on",
                        action='store_true')
    parser.add_argument("--debug", "-d",
                        help="Turn debugging on",
                        action='store_true')
    args = parser.parse_args()
    return args

def usage():
    print("extract [-vd] -i <object to extract> [-t <object type> ")

if __name__ == '__main__':
    main()
