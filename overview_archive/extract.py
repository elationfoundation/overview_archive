#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of overview archive, a tool for archiving and tagging resources.
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
from utils.identify import get_type


import logging
log = logging.getLogger(__name__)

def set_logging(verbose=False, debug=False):
    logging.basicConfig(level=logging.ERROR)
    if debug == True:
        log.setLevel("DEBUG")
    elif verbose = True:
        log.setLevel("INFO")












def main():
    args = parse_arguments()
    set_logging(args.verbose, args.debug)





def parse_arguments():
    arg_p = argparse.ArgumentParser("Get a summary of some text")
    parser.add_argument("--type", "-t",
                        help="The type of object being extracted.")
    parser.add_argument("--input_file", "-i",
                        help="The path to extract into plain text")
    parser.add_argument("--output_file", "-o",
                        help="The file path to write the parsed text. This will overwrite the path.",
                        default=path.join(getcwd(), "parsed_text")
    parser.add_argument("--verbose", "-v",
                        help="Turn verbosity on",
                        action='store_true')
    parser.add_argument("--debug", "-d",
                        help="Turn debugging on",
                        action='store_true')
    args = arg_p.parse_args()
    return args

if __name__ == '__main__':
    main()
