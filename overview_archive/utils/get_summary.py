#!/usr/bin/env python

# Packages Used

# As taken from the [[https://github.com/miso-belica/sumy#python-api][Sumy api page.]]

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

from sumy.parsers.html import HtmlParser
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
from url_text_scrape import get_url
# Needed for command line functionality

import sys
import argparse

# Read text from file

def get_plain_text(text_file):
    with open(text_file, 'r') as f:
        read_data = f.read()
    return read_data

# Summation

def summarize(text, language="english", count=5):
    """
    text (str):
    language (str):
    count (int):
    """
    summary = []
    text_file = text
    parser = PlaintextParser.from_string(text, Tokenizer(language))
    stemmer = Stemmer(language)
    # or for plain text files
    summarizer = Summarizer(stemmer)
    summarizer.stop_words = get_stop_words(language)

    for sentence in summarizer(parser.document, count):
        summary.append(sentence)
    return summary

# Command Line

def parse_arguments():
    arg_p = argparse.ArgumentParser("Get a summary of some text")
    arg_p.add_argument("-u", "--url", type=str, help="A url to parse.")
    arg_p.add_argument("-i", "--input-file", type=str, help="A file containing plain text to parse")
    args = arg_p.parse_args()
    return args

def usage():
    print("get_summary [-i <file> | -u <url> ] ")

# Main

def main():
    args = parse_arguments()
    if args.url:
        text = get_url(args.url)
    elif args.input_file:
        text = get_plain_text(args.input_file)
    else:
        usage()
        sys.exit(64)
    #lang = get_lang(text)
    summary = summarize(text)
    #translated = translate(summary, dev_key, lang)
    #keywords = check_keywords(translated)
    for i in summary:
        sys.stdout.write(str(i).decode("utf8").encode("ascii", errors='ignore'))
        sys.stdout.write("\n")
    sys.exit(0)

if __name__ == "__main__":
    main()
