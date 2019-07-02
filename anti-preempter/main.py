#!/usr/bin/env python

import sys
import logging
import argparse
from time import gmtime, strftime

logging.basicConfig(level=logging.INFO,
                    format='-> [%(levelname)s] [%(asctime)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M')

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--dryrun", help="Dry-run only, do not kill any nodes", action="store_true")
    parser.add_argument("-v", "--debug", help="Turn on debugging", action="store_true")

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    logger.info("Pre-pre-empter script started at " + get_timestamp())

    if args.dryrun:
        logger.info("Running in dry-run mode - nodes will not be deleted")

    logger.info("Script completed at " + get_timestamp())


def get_timestamp() -> str:
    return strftime("%Y-%m-%d %H:%M:%S", gmtime())


def init():
    if __name__ == "__main__":
        sys.exit(main())


init()
