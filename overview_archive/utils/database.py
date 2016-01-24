#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of overview archive, a package that makes creating archives of various sources and getting content about them easier for me.
# Copyright © 2016 seamus tuohy, <s2e at seamustuohy dot com>
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
#import xapian
#from polyglot.text import Text
from os import mkdir, path
from whoosh.fields import Schema, TEXT, BOOLEAN, DATETIME, ID
from whoosh.index import create_in, exists_in, open_dir
from whoosh.qparser import QueryParser

import logging
log = logging.getLogger("oa.{0}".format(__name__))


def main():
    args = parse_arguments()
    set_logging(args.verbose, args.debug)

class WhooshDB():
    def __init__(self, index_path):
        self.schema = Schema(path=ID(unique=True, stored=True),
                             title=TEXT(stored=True),
                             archive=TEXT,
                             has_archive=BOOLEAN,
                             url=TEXT,
                             captured_date=DATETIME,
                             mime_type=TEXT(stored=True),
                             extension=TEXT,
                             langauge=TEXT,
                             content=TEXT)
        self.index = index_path

    @property
    def index(self):
        """I'm the 'index' property."""
        return self._index

    @index.setter
    def index(self, value):
        if not path.exists(value):
            log.info("creating woosh database directory")
            mkdir(value)
        if not exists_in(value):
            log.info("Whoosh DB does not exist. Creating it.")
            create_in(value, self.schema)
        else:
            log.info("Whoosh DB exist. Using Existing WhooshDB.")
        ix = open_dir(value)
        self._index = ix

    @index.deleter
    def index(self):
        del self._index

    def search(self, query_string, search_type="content"):
        log.info("searching for {0}".format(query_string))
        self._current_query = query_string
        self._page = 0
        return self.search_next(search_type)

    def search_next(self, search_type="content"):
        self._page += 1
        with self.index.searcher() as searcher:
            parser = QueryParser(search_type, self.schema)
            query = parser.parse(self._current_query)
            results = searcher.search_page(query, self._page)
            #print(results[0])
            #print(len(results[0]))
        return results

    def get(self, path):
        with self.index.searcher() as searcher:
            return searcher.document(path=path)

    def add_document(self, document):
        # for i in document:
        #     print("{0}:{1}".format(i, str(document[i])[:20]))
        log.info("Adding document {0}".format(document["title"]))
        writer = self.index.writer()
        writer.add_document(path = document["path"],
                            title = document["title"],
                            archive = document["archive"],
                            has_archive = document["has_archive"],
                            url = document["url"],
                            captured_date = document["captured_date"],
                            mime_type = document["mime_type"],
                            extension = document["extension"],
                            langauge = document["langauge"],
                            content = document["content"])
        writer.commit()


# Command Line Functions below this point

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
    args = parser.parse_args()
    return args

def usage():
    print("TODO: usage needed")

if __name__ == '__main__':
    main()
