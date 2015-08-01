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
import subprocess
import nltk
import string
from nltk.util import ngrams
from overview_archive.utils import identify
import re
from nltk.corpus import stopwords
from bs4 import BeautifulSoup, Comment
from bs4.diagnose import diagnose

# logging
import logging
log = logging.getLogger("oa.{0}".format(__name__))


def from_file(file_path, filetype):
    """Cleans away everything but the text from a file for parsing."""
    mimetypes = ['text/html',
                 'application/pdf']

    if filetype not in mimetypes:
        log.error("Filetype {0} of file {1} not a currently cleanable filetype.".format(filetype, file_path))
        raise ValueError("Filetype {0} of file {1} not a currently cleanable filetype.".format(filetype, file_path))
    if filetype == 'application/pdf':
        cleaned, header = from_pdf(file_path)
    elif filetype == 'text/html':
        cleaned, header = from_html(file_path)
    return cleaned, header

def from_html(file_path):
    with open(file_path, "r") as html_file:
        html_text = html_file.read()

        html_obj = BeautifulSoup(html_text, 'lxml')
        html_title = html_obj.title.string.strip()
        # Remove all comment elements
        comments = html_obj.findAll(text=lambda text:isinstance(text, Comment))
        [comment.extract() for comment in comments]
        #print(html_obj)

        # print and reparse html or we get an error for some reason
        html_obj = BeautifulSoup(html_obj.prettify(), 'lxml')

        # remove all script and style elements
        for unwanted in html_obj(["script", "style"]):
            unwanted.extract()

        # print and reparse html or we get an error for some reason
        html_obj = BeautifulSoup(html_obj.prettify(), 'lxml')

        # get the text
        text = html_obj.get_text()

        # break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)
    return text, html_obj.title.string

def from_pdf(file_path):
    """Extracts text from a pdf using pdftotext."""
    if identify.filetype(file_path).decode() != 'application/pdf':
        raise TypeError("File {0} is not a pdf and cannot be extracted using this function.".format(file_path))
    try:
        pdf_text = subprocess.check_output(["pdftotext",  "-raw", "-nopgbrk", "-eol", "unix",  file_path, "-"])
        pdf_info = subprocess.check_output(["pdfinfo", file_path])
        pdf_meta = pdf_info.decode().split("\n")
        pdf_title = None
        #Get pdf meta-data and extract a file name if any.
        for i in pdf_meta:
            _title = re.match("^Title:(.*$)", i)
            if _title:
                pdf_title = _title.group(1).strip()
        return pdf_text, pdf_title
    except subprocess.CalledProcessError as _err:
        log.debug(_err)
        log.error("pdftotext failed while attempting to parse the supplied pdf.")
        raise TypeError("Unable to parse supplied PDF.")



def wordlist(text):
    try:
        text = text.decode()
    except AttributeError:
        pass
    tokens = nltk.word_tokenize(text)
    lowered = [x.lower() for x in tokens]
    plain = [re.sub(r'\W+', '', x) for x in lowered]
    unique_words = set(plain)
    stop_words = stopwords.words('english')
    nostop = [x for x in unique_words if x not in stop_words]
    no_blanks = [x for x in nostop if len(x) > 1]
    return no_blanks

def termlist(text):
    try:
        text = text.decode()
    except AttributeError:
        pass
    terms = []
    for line in text:
        print(line)
        clean = line.lower().strip()
        terms.append(clean)
    return terms


def entity_list(text):
    """Extract a list of entities from a piece of text"""
    try:
        text = text.decode()
    except AttributeError:
        pass
    # Parse the text into tagged and chunked sentences
    sentences = nltk.sent_tokenize(text)
    tokenized_sentences = [nltk.word_tokenize(sentence) for sentence in sentences]
    tagged_sentences = [nltk.pos_tag(sentence) for sentence in tokenized_sentences]
    chunked_sentences = nltk.ne_chunk_sents(tagged_sentences, binary=True)

    entity_names = []
    for tree in chunked_sentences:
        entity_names.extend(extract_entity_names(tree))
    # return unique entities
    return set(entity_names)

def extract_entity_names(tree):
    entity_names = []

    if hasattr(tree, 'label') and tree.label:
        if tree.label() == 'NE':
            entity_names.append(' '.join([child[0] for child in tree]))
        else:
            for child in tree:
                entity_names.extend(extract_entity_names(child))

    return entity_names
