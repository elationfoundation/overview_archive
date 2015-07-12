#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of overview archive.
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

# identification
import magic
from os import path
from os.path import abspath

import logging
log = logging.getLogger(__name__)


def get_type(file_path):
    if path.exists(file_path) and path.isfile(file_path):
        try:
            file_type = magic.from_file(abspath(file_path), mime=True)
        except IOError:
            log.error("{0} is not a valid file".format(file_path))
            raise IOError("{0} is not a valid file".format(file_path))
    else:
        log.error("{0} is not a valid path to a file".format(file_path))
        raise IOError("{0} is not a valid path to a file".format(file_path))
    log.debug("filetype for {0} identified as {1}".format(file_path, file_type))
    return file_type
