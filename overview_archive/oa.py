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
from collections import namedtuple

from overview_archive.get import get_any
from overview_archive.utils import clean_text, database, identify, org_mode
from overview_archive import extract
from urllib.error import HTTPError
import logging
from uuid import uuid4
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
    parser.add_argument("--debug", "-d",                        help="Turn debugging on",
                        action='store_true')
    parser.add_argument("--input_path", "-i",
                        help="The path to retreive an object from.")
    parser.add_argument("--org_output_path", "-o",
                        help="The path to write the org-object to.")
    parser.add_argument("--keywords", "-k",
                        help="The list of keywords to extract from the text (case insensitive).")
    parser.add_argument("--capture_entities", "-e",
                        help="Should the parser capture entities.",
                        action='store_true')
    parser.add_argument("--whoosh_dir", "-w",
                        help="The path to the directory containing the whoosh index to use.")
    parser.add_argument("--whoosh_text_dir", "-W",
                        help="The path where raw text should be stored when using Whoosh.")
    args = parser.parse_args()
    return args

def usage():
    print("overview archive ")

def write_org(args):
    # Create an org-mode object in case we get errors.
    # We want to be all the way into the properties before we get exceptions
    org_mode_object = []
    org_mode_object.append(org_mode.Entry(1, args["input_path"]))
    org_mode_object.append(":PROPERTIES:")
    org_date = org_mode.get_org_date()
    org_mode_object.append(org_mode.make_property("captured", org_date))
    org_mode_object.append(org_mode.make_property("failed", True))
    try:
        # Try and hope it works.
        go(args)
    except HTTPError as _e:
        org_mode_object.append(org_mode.make_property("error", _e))
        org_mode_object.append(":END:")
        with open(args["org_output_path"], 'a') as org_file:
                for i in org_mode_object:
                    org_file.write("\n")
                    org_file.write(str(i))


def go(args):
    set_logging(args["verbose"], args["debug"])
    results = {}
    # get the date
    results['date'] = datetime.now()

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
        # Identify if object has been archived.
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

        # add raw text to results
        results['raw_text'] = raw_text
        # compare words against a keyword file
        keyword_union = None
        term_match = []
        if args["keywords"]:
            log.info("starting keyword extraction from file")
            with open(args["keywords"], 'r') as keyword_file:
                terms = extract.termlist(keyword_file)
                log.debug("keywords list: {0}".format(terms))
                for _t in terms:
                    if _t in raw_text:
                        term_match.append(_t)
            if term_match != []:
                keyword_union = set(term_match)
                log.debug("keywords overlapping: {0}".format(keyword_union))
            if keyword_union:
                log.debug("keywords found: {0}".format(keyword_union))
                results['keywords'] = keyword_union
            else:
                log.debug("No Keywords Found")
        else:
            log.info("no keyword file given. Skipping keyword extraction.")

        # Getting entitites
        if args["capture_entities"]:
            log.info("capturing entities")
            entitites = extract.entity_list(raw_text)
            log.info("entities have been captured")
            log.debug("entitites found {0}.".format(entitites))
            results['entities'] = entitites

        # Place cleaned test into a file????
        #_filename = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        #cleaned_text_path = path.join(temp_dir, _filename)

        # Set the directory for whoosh text
        if args["whoosh_text_dir"]:
            raw_text_path = "{0}/{1}".format(args["whoosh_text_dir"], uuid4().hex)
        else:
            raw_text_path = "/tmp/whoosh/docs/{0}".format(uuid4().hex)

        with open(raw_text_path, "w+") as raw_file:
            raw_file.write(results['raw_text'])

        if args['whoosh_dir']:
            document = {"path":"",
                        "title":"",
                        "archive":"",
                        "has_archive":"",
                        "url":"",
                        "captured_date":"",
                        "mime_type":"",
                        "extension":"",
                        "langauge":"",
                        "content":""}
            document["title"] = results['title'].strip()
            if results['origin_type'] == "url":
                document["url"] = args["input_path"]

            if results['archived'] == True:
                document["has_archive"] = True
                document["archive"] = results['location']
            else:
                document["has_archive"] = False
                document["archive"] = ""

            document["captured_date"] = results['date']
            document["mime_type"] = results['filetype']
            document["extension"] = "" # TODO
            document["language"] = "" # TODO
            document["path"] = raw_text_path
            document["content"] = results['raw_text']
            #print(type(document.content))
            DB = database.WhooshDB(args['whoosh_dir'])
            DB.add_document(document)

        elif args["org_output_path"]:
            org_mode_object = []
            if results['origin_type'] == "url":
                heading = "".join(["[[", results['location'].strip(), "][", results['title'].strip(), "]]" ])
                org_mode_object.append(org_mode.Entry(1, heading))
            else:
                org_mode_object.append(org_mode.Entry(1, results['title']))
            org_mode_object.append(":PROPERTIES:")
            org_date = org_mode.get_org_date()
            org_mode_object.append(org_mode.make_property("captured", org_date))
            org_mode_object.append(org_mode.make_property("is_archived", results['archived']))
            org_mode_object.append(org_mode.make_property("filetype", results['filetype']))
            org_mode_object.append(":END:")

            # archived
            # origin_type
            # results['keywords']
            try:
                _keywords = results['keywords']
                org_mode_object.append(":keywords:")
                for e in _keywords:
                    org_mode_object.append(org_mode.Entry(1, e.lower(), starter_char="-"))
                org_mode_object.append(":END:")
            except KeyError:
                log.info("Not adding keywords to org object because they were not found.")

            org_mode_object.append(":entities:")
            for e in entitites:
                org_mode_object.append(org_mode.Entry(1, e.lower(), starter_char="-"))
            org_mode_object.append(":END:")
            with open(args["org_output_path"], 'a') as org_file:
                for i in org_mode_object:
                    org_file.write("\n")
                    org_file.write(str(i))
