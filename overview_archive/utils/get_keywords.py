#!/usr/bin/env python

# Imports

from rake import Rake
import sys
import argparse

# Read text from file

def get_plain_text(text_file):
    with open(text_file, 'r') as f:
        read_data = f.read()
    return read_data

# extraction
# Create taxonomy vocabulary terms from extracted key word
# Almost entirely taken from https://github.com/aneesha/RAKE
# Using https://www.airpair.com/nlp/keyword-extraction-tutorial as a guide

def get_keywords(text, stopwords="SmartStoplist.txt"):
    #commented out text below uses the rake-tutorial code, which I like better, but is less recently updated
    #https://github.com/zelandiya/RAKE-tutorial
    #phrase_max_words = 3
    #min_word_chars = 5
    #min_kw_repeat_rate = 4
    #rake = Rake(stopwords, min_word_chars, phrase_max_words, min_kw_repeat_rate)
    rake = Rake(stopwords)
    keywords = rake.run(text)
    return keywords

# Command Line

def parse_arguments():
    arg_p = argparse.ArgumentParser("Get a summary of some text")
    arg_p.add_argument("-i", "--input-file", type=str, help="A file containing plain text to parse")
    arg_p.add_argument("-s", "--stopwords-file", type=str, help="A file containing stop words to use to parse text.")
    args = arg_p.parse_args()
    return args

def usage():
    print("get_summary [-i < text file> | -s <stop words file> ] ")

# Main

def main():
    args = parse_arguments()
    if args.input_file:
        text = get_plain_text(args.input_file)
    else:
        usage()
        sys.exit(64)
    #lang = get_lang(text)
    _keywords = get_keywords(text)
    for i in _keywords:
        sys.stdout.write(str(i).encode("UTF-8"))
        sys.stdout.write("\n")
    sys.exit(0)

if __name__ == "__main__":
    main()
