#!/usr/bin/env python

# Imports

import argparse
from utils.url_text_scrape import get_url

def parse_arguments():
    arg_p = argparse.ArgumentParser("Get a summary of some text")
    arg_p.add_argument("-u", "--url", type=str, help="A url to parse.")
    arg_p.add_argument("-i", "--input-file", type=str, help="A file containing plain text to parse")
    args = arg_p.parse_args()
    return args

def usage():
    print("get_summary [-i <file> | -u <url> ] ")

def main():
    test_list = [ "safetag", "organization", "auditor", "threat", "security", "audit", "activity", "penetration test", "intelligence gathering", "engagement", "risk assessment", "vulnerability", "pentest", "recommendation", "adversary", "actor", "framework", "guide", "attack", "report", "attacker", "training", "agency", "risk assessment", "capability", "outcome", "threat actor", "asset", "incident", "expertise", "matrix", "exercise", "roadmap", "audits", "modeling"]
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
