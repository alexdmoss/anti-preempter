#!/usr/bin/env python

import sys
import logging
import argparse
from typing import List
from anti_preempter.manage_instances import list_preemptible_instances
from anti_preempter.manage_instances import delete_instance
from anti_preempter.manage_instances import wait_for_operation
from anti_preempter.utils import get_current_time_as_seconds
from anti_preempter.utils import get_env_variable

logging.basicConfig(level=logging.INFO,
                    format="-> [%(levelname)s] [%(asctime)s] %(message)s",
                    datefmt="%Y-%m-%d %H:%M")

logger = logging.getLogger(__name__)


def main():

    GCP_PROJECT_ID = get_env_variable("GCP_PROJECT_ID")
    INSTANCE_INTERVAL = int(get_env_variable("INSTANCE_INTERVAL"))

    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--dryrun", help="Dry-run only, do not delete any nodes", action="store_true")
    parser.add_argument("-v", "--debug", help="Turn on debugging", action="store_true")

    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    logger.info("anti-pre-empter has started")

    if args.dryrun:
        logger.info("Running in dry-run mode - nodes will not be deleted")

    instances = list_preemptible_instances(project=GCP_PROJECT_ID)

    instance_to_delete = find_instance_to_restart(instances=instances, interval=INSTANCE_INTERVAL)

    if instance_to_delete:
        if not args.dryrun:
            logger.info(f"Deleting {instance_to_delete[0]} in {instance_to_delete[1]}")
            operation = delete_instance(project=GCP_PROJECT_ID, instance=instance_to_delete[0], zone=instance_to_delete[1])
            if operation:
                wait_for_operation(project=GCP_PROJECT_ID, zone=instance_to_delete[1], operation=operation["name"])
        else:
            logger.info(f"DRY RUN: Would delete {instance_to_delete[0]} in {instance_to_delete[1]}, but SKIPPING")
    else:
        logger.info("No instances found to delete")

    logger.info("Script completed")


def find_instance_to_restart(instances, interval) -> List:
    # instances are sorted name:creationTimestamp oldest --> newest
    # if the current instance is within 1 hour of next, cycle the current and break (eventual consistency)
    logger.debug("Looking for instances which are close to creation times of another")
    # this is not very pythonic!
    i = 0
    for instance in instances:
        instance_name = instance[0]
        this_creation_time = instance[1]
        zone_prefix, instance_zone = instance[2].rsplit("/", 1)
        i = i + 1
        try:
            next_creation_time = instances[i][1]
        except IndexError:
            next_creation_time = get_current_time_as_seconds()
        logger.debug(f"For Instance {instance_name} in {instance_zone}, comparing {next_creation_time} to {this_creation_time}")
        if (int(next_creation_time) - int(this_creation_time)) <= interval:
            logger.info(f"{instance_name} will be deleted")
            return [instance_name, instance_zone]


def init():
    if __name__ == "__main__":
        sys.exit(main())


init()
