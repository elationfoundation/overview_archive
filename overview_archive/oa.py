#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of overview archive, a package that makes creating archives of various sources and getting content about them easier for me..
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

import argparse
import random
import string
import tempfile
from os import path, getcwd
from datetime import datetime

from overview_archive.get import get_any
from overview_archive.utils import identify
from overview_archive.utils import clean_text
from overview_archive import extract
from overview_archive.utils import org_mode

import logging
logging.basicConfig(level=logging.ERROR)
log = logging.getLogger("oa")

def set_logging(verbose=False, debug=False):
    if debug == True:
        log.setLevel("DEBUG")
    elif verbose == True:
        log.setLevel("INFO")


def parse_arguments():
    parser = argparse.ArgumentParser("Get a summary of some text")
    parser.add_argument("--verbose", "-v",
                        help="Turn verbosity on",
                        action='store_true')
    parser.add_argument("--debug", "-d",
                        help="Turn debugging on",
                        action='store_true')
    parser.add_argument("--input_path", "-i",
                        help="The path to retreive an object from.")
    parser.add_argument("--org_output_path", "-o",
                        help="The path to write the org-object to.")
    parser.add_argument("--keywords", "-k",
                        help="The list of keywords to extract from the text (case insensitive).")
    args = parser.parse_args()
    return args

def usage():
    print("overview archive ")

def go(args):
    set_logging(args["verbose"], args["debug"])
    results = {}
    # get the date
    results['date'] = str(datetime.now())

    log.debug("getting {0}.".format(args["input_path"]))
    if identify.is_url(args["input_path"]):
        results['origin_type'] = "url"
    else:
        results['origin_type'] = "file"
    with tempfile.TemporaryDirectory() as temp_dir:
        #Create a local directory for parsing content
        _filename = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        local_path = path.join(temp_dir, _filename)
        #local_path = "/home/s2e/temp/test_html.txt"
        log.debug("temporary file path created for object at {0}".format(local_path))

        log.info("Retreiving object from {0}".format(args["input_path"]))
        local_object, object_location = get_any(args["input_path"], local_path)
        log.info("Object sucessfully retreived from {0}".format(args["input_path"]))
        log.info("identifying object type")
        results['location'] = object_location
        # Identify if ovject has been archived.
        if identify.is_url(object_location):
            if identify.is_archive(object_location):
                results['archived'] = True
            else:
                results['archived'] = False
        else:
            results['archived'] = False

        # if identify.is_url(args["input_path"]):
        #     # Check if the object has custom parsers, and if so, get any pre-defined properties
        #     w_custom_parsers = identify.get_w_custom(args["input_path"])
        #     for i in w_custom_parsers:
        #         _parser = w_custom_parsers[i].data
        #         results[] =

        # Get filetype
        filetype = identify.filetype(local_path).decode()
        results['filetype'] = filetype

        # Extract text and title from file
        raw_text, title = extract.from_file(local_path, filetype)
        log.debug("raw text found: {0}".format(raw_text))

        # Add title to results
        log.debug("title found: {0}".format(title))
        # Check to see if we puled a proper title
        if title:
            results['title'] = title.strip()
        # if we don't have a title, it was probobly a file
        elif results['origin_type'] == "file":
            # Use the filename instead
            results['title'] = path.basename(args["input_path"])

        # compare words against a keyword file
        keyword_unison = None
        if args["keywords"]:
            log.info("starting word extraction")
            words = extract.wordlist(raw_text)
            log.debug("words found: {0}".format(words))
            log.info("starting keyword extraction from file")
            with open(args["keywords"], 'r') as keyword_file:
                keywords = extract.wordlist(keyword_file.read())
                log.debug("keywords list: {0}".format(terms))
            keyword_union = list(set(words) & set(keywords))
            log.debug("keywords overlapping: {0}".format(keyword_union))
            if keyword_union:
                log.debug("keywords found: {0}".format(keyword_union))
                results['keywords'] = keyword_union
            else:
                log.debug("No Keywords Found")
        else:
            log.info("no keyword file given. Skipping keyword extraction.")

        # Getting entitites
        log.info("capturing entities")
        entitites = extract.entity_list(raw_text)
        log.info("entities have been captured")
        log.debug("entitites found {0}.".format(entitites))
        results['entities'] = entitites

        # Place cleaned test into a file????
        #_filename = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        #cleaned_text_path = path.join(temp_dir, _filename)

        # for i in results:
        #     print("\n", i, " : ", results[i])

        if args["org_output_path"]:
            org_mode_object = []
            if results['origin_type'] == "url":
                heading = "".join(["[[", results['location'].strip(), "][", results['title'].strip(), "]]" ])
                org_mode_object.append(org_mode.Entry(1, heading))
            else:
                org_mode_object.append(org_mode.Entry(1, results['title']))
            org_mode_object.append(":PROPERTIES:")
            org_date = org_mode.get_org_date()
            org_mode_object.append(org_mode.make_property("captured", org_date))
            org_mode_object.append(":END:")


            # archived
            # origin_type
            # results['keywords']
            try:
                _keywords = results['keywords']
                org_mode_object.append(org_mode.Entry(2, "keywords"))
                for e in _keywords:
                    org_mode_object.append(org_mode.Entry(1, e.lower(), starter_char="-"))
            except KeyError:
                log.info("Not adding keywords to org object because they were not found.")

            org_mode_object.append(org_mode.Entry(2, "entities"))
            for e in entitites:
                org_mode_object.append(org_mode.Entry(1, e.lower(), starter_char="-"))

            with open(args["org_output_path"], 'a') as org_file:
                for i in org_mode_object:
                    org_file.write("\n")
                    org_file.write(str(i))
