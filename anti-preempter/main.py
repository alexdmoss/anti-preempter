#!/usr/bin/env python

import sys
import logging
import argparse
from time import gmtime, strftime
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from kubernetes.config.config_exception import ConfigException

logging.basicConfig(level=logging.INFO,
                    format='-> [%(levelname)s] [%(asctime)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M')

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--dryrun", help="Dry-run only, do not kill any nodes", action="store_true")
    parser.add_argument("-v", "--debug", help="Turn on debugging", action="store_true")

    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    logger.info("Pre-pre-empter script started at " + get_timestamp())

    if args.dryrun:
        logger.info("Running in dry-run mode - nodes will not be deleted")

    nodes = list_preemptible_nodes()

    print(nodes)

    logger.info("Script completed at " + get_timestamp())


def list_preemptible_nodes():

    logger.debug("Listing nodes")

    nodes =[]

    try:
        config.load_incluster_config()  # on cluster
    except ConfigException:
        config.load_kube_config()       # fallback running locally

    v1 = client.CoreV1Api()

    try:
        response = v1.list_node(watch=False, timeout_seconds=50, label_selector='cloud.google.com/gke-preemptible=true')
        for item in response.items:
            nodes.append(item.metadata.name)
    except ApiException as e:
        logger.error("Exception when calling CoreV1Api->list_node: %s\n" % e)

    return nodes


def get_timestamp() -> str:
    return strftime("%Y-%m-%d %H:%M:%S", gmtime())


def init():
    if __name__ == "__main__":
        sys.exit(main())


init()
