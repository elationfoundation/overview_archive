#!/usr/bin/env python3

# Imports


# logging
import logging
log = logging.getLogger("oa.{0}".format(__name__))

# Scraping


def remove_wayback_toolbar():
    """Remove wayback toolbar from webpages.

    Toolbar starts and ends with a consistant set of strings.

    <!-- BEGIN WAYBACK TOOLBAR INSERT -->
    [...]
    <!-- END WAYBACK TOOLBAR INSERT -->

    """
    log.warn("TODO implement this function.")


def from_file(file_path, filetype):
    """Cleans away everything but the text from a file for parsing."""
    mimetypes = ['text/html',
                 'application/pdf']

    if filetype not in mimetypes:
        log.error("Filetype {0} of file {1} not a currently cleanable filetype.".format(filetype, file_path))
        raise ValueError("Filetype {0} of file {1} not a currently cleanable filetype.".format(filetype, file_path))


def clean_pdf_text(file_path):
    """ """
    log.warn("TODO Write this function.")




# Parse Arguments

def parse_arguments():
    parser = argparse.ArgumentParser("Clean scraped text from a file.")
    parser.add_argument("--input_file", "-i",
                        help="The path to extract into plain text")
    parser.add_argument("--output_file", "-o",
                        help="The file path to write the parsed text. This will overwrite the path.",
                        default=path.join(getcwd(), "parsed_text"))
    parser.add_argument("--verbose", "-v",
                        help="Turn verbosity on",
                        action='store_true')
    parser.add_argument("--debug", "-d",
                        help="Turn debugging on",
                        action='store_true')
    parser = arg_p.parse_args()
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
