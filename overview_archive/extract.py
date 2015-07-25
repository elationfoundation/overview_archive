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
from nltk.util import ngrams
from overview_archive.utils import identify
import string
from collections import Counter
from nltk.corpus import stopwords

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
        cleaned = from_pdf(file_path)
    return cleaned


def from_pdf(file_path):
    """Extracts text from a pdf using pdftotext."""
    if identify.filetype(file_path).decode() != 'application/pdf':
        raise TypeError("File {0} is not a pdf and cannot be extracted using this function.".format(file_path))
    try:
        pdf_text = subprocess.check_output(["pdftotext",  "-raw", "-nopgbrk", "-eol", "unix",  file_path, "-"])
        return pdf_text
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
    tagged = nltk.pos_tag(tokens)
    words = tagged[0:20]
    return words


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


def keywords(raw_text):
    try:
        text = raw_text.decode()
    except AttributeError:
        pass
    # Adapted from http://graus.nu/blog/simple-keyword-extraction-in-python/#comment-113
    # 1. for each document of the corpus:
    # —- tokenize
    tokens = nltk.word_tokenize(text)
    # —- toLowerCase, trim
    make_low = lambda x: x.lower()
    tokens = list(map(make_low, tokens))
    # — delete all non printable characters with a regex
    # TODO: I think that this works, I am not sure that it wont cause problems later. Need a unit test for this.
    clean = lambda dirty: ''.join(filter(string.printable.__contains__, dirty))
    tokens = list(map(clean, tokens))
    # — trim again
    # — delete multiple white spaces
    # — 1.1. Looping on each token of this document:
    # ——–  lemmatization by replacing plurals by singulars using simple heuristics (it takes me just 15 lines of code)
    lemmatiser = nltk.stem.WordNetLemmatizer()
    lemmit = lambda x: lemmatiser.lemmatize(x)
    tokens = list(map(lemmit, tokens))
    # — append the resulting string to the global string containing all documents.
    text_stream = " ".join(tokens)

    # 2. extract n-grams (unigrams, bigrams, trigrams, 4-grams) of the global string and count their frequency
    unigrams = list(ngrams(tokens,1))
    bigrams = list(ngrams(tokens,2))
    trigrams = list(ngrams(tokens,3))
    fourgrams = list(ngrams(tokens,4))
    allgrams = unigrams + bigrams + trigrams + fourgrams
    freqs = Counter(allgrams)

    # 3. remove n-grams with length < 3
    # TODO: I don't understand what this was about so I removed it.
    # long_grams = []
    # for i in allgrams:
    #     only_long = tuple([x for x in i if len(x) > 3])
    #     long_grams.append(only_long)
    # #print(long_grams)
    # freqs = Counter(long_grams)

    # 4. remove n-grams which appear just once or twice (unjustified but reasonable absolute cut-off, help to clean a lot!)
    many_grams = [x for x in freqs if freqs[x] > 2]

    # 5. remove stop words
    # //there are many criteria here, but the main ones are:
    nostop_grams = []
    eng_stopwords = stopwords.words('english')
    for gram in many_grams:
        dump_gram = False
        # — if it is a unigram, remove it if it is in the list of stopwords
        # — if it is a bi-gram or above, remove it IF some of its token belongs to the list of stopwords
        for word in gram:
            if word in eng_stopwords:
                dump_gram = True
        if dump_gram == False:
            nostop_grams.append(gram)

    # 6. keep only the n most frequent n-grams (n depends on the size of your corpus and your goals)
    freqs = Counter(nostop_grams)
    common_grams = freqs.most_common(100)
    print(common_grams)
    # 7. remove redundant n-grams
    # // eg: if a = "University of" and b= "University of Amsterdam" are both in the list of most frequent n-grams, //remove a because it is contained in b, and because it is not n times more frequent than b (I found that a n of 2 or 3 works fine).

    # 8. count the occurrences of each remaining n-gram in each document
    return text_stream
    #return tokens
