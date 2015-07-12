#!/usr/bin/env python

# Imports

from bs4 import BeautifulSoup
from urllib import urlopen

# Scraping

def get_url(url):
    url_obj = urlopen(url).read()
    html = BeautifulSoup(url_obj)
    raw = html.get_text()
    return raw

# Parse Arguments

def parse_arguments():
    arg_p = argparse.ArgumentParser("Get raw text from a url")
    arg_p.add_argument("-u", "--url", type=str, help="A url to parse.")
    args = arg_p.parse_args()
    return args

# Main

if __name__ == '__main__':
    import sys
    import argparse
    args = parse_arguments()
    raw = get_url(args.url)
    utf_text = raw.encode("UTF-8")
    clean_text = ' '.join(utf_text.split())
    sys.stdout.write(clean_text)
    sys.exit(0)
