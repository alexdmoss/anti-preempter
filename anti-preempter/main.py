#!/usr/bin/env python

import sys
import logging
import argparse
from operator import itemgetter
from collections import OrderedDict
from typing import Dict
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

    nodes = list_preemptible_nodes_by_creation_time()

    find_nodes_to_restart(nodes)

    logger.info("Script completed at " + get_timestamp())


def list_preemptible_nodes_by_creation_time() -> Dict:

    logger.debug("Listing nodes")

    v1 = create_k8s_client()

    nodes = {}

    try:
        response = v1.list_node(watch=False, timeout_seconds=50, label_selector='cloud.google.com/gke-preemptible=true')
    except ApiException as e:
        logger.error("Exception when calling CoreV1Api->list_node: %s\n" % e)

    for item in response.items:
        nodes[item.metadata.name] = get_time_as_seconds_since_epoch(item.metadata.creation_timestamp)

    return nodes


def find_nodes_to_restart(nodes):

    # 1978

    current_timestamp = get_current_seconds()
    
    sorted_by_age = OrderedDict(sorted(nodes.items(), key=itemgetter(1)))

    # creation_times = sorted_by_age.values()

    for node, creation_time in sorted_by_age.items():
        delta = int(current_timestamp) - int(creation_time)
        print(delta)
        if delta <= 300:
            print(current_timestamp + " is within 5 minutes of " + creation_time)
        else:
            current_timestamp = creation_time
        print("-------------------")

    # for node, ts in sorted_by_age.items():
    #     for k, v in sorted_by_age.items():
    #         if k != node:
    #             print("Comparing: " + v + " to " + ts)
    #             if int(v) >= (int(ts) - 300):
    #                 print(k + " is within 5 mins of " + node)
    #                 print("--------------------------------")


def create_k8s_client():
    try:
        config.load_incluster_config()  # on cluster
    except ConfigException:
        config.load_kube_config()       # fallback running locally
    return client.CoreV1Api()


def get_timestamp() -> str:
    return strftime("%Y-%m-%d %H:%M:%S", gmtime())


def get_current_seconds() -> str:
    return strftime("%s", gmtime())


def get_time_as_seconds_since_epoch(ts) -> str:
    return ts.strftime('%s')


def init():
    if __name__ == "__main__":
        sys.exit(main())


init()
