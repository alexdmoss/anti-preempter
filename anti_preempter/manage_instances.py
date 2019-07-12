import logging
from time import time
from typing import List
from operator import itemgetter
from anti_preempter.google_client import google_api_call
from anti_preempter.google_client import google_api_create_service
from anti_preempter.utils import get_time_as_seconds_since_epoch

logger = logging.getLogger(__name__)


def list_preemptible_instances(project: str) -> List:
    instances = []
    compute = google_api_create_service("compute", "v1")
    request = compute.instances().aggregatedList(project=project, filter="scheduling.preemptible = true")
    response = google_api_call(request)
    # there is probably a more pythonic way of doing this ...
    if response:
        if "items" in response:
            for zone, zone_items in response["items"].items():
                for instance_key, instance_list in zone_items.items():
                    if "warning" not in instance_key:
                        for instance in instance_list:
                            logger.info(f"Found {instance['name']}, created at {instance['creationTimestamp']}")
                            instances.append([instance["name"], get_time_as_seconds_since_epoch(
                                instance["creationTimestamp"]), instance["zone"]])
    # sorts oldest --> newest
    instances.sort(key=itemgetter(1))
    return instances


def delete_instance(project, zone, instance):
    compute = google_api_create_service("compute", "v1")
    request = compute.instances().delete(project=project, zone=zone, instance=instance)
    return google_api_call(request)


def wait_for_operation(project, zone, operation):
    logger.info("Waiting for operation to finish ...")
    compute = google_api_create_service("compute", "v1")
    while True:
        request = compute.zoneOperations().get(project=project, zone=zone, operation=operation)
        result = google_api_call(request)
        if result["status"] == "DONE":
            logger.info("Operation completed")
            if "error" in result:
                raise Exception(result["error"])
            return result
        time.sleep(1)
