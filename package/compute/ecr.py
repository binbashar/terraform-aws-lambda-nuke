# -*- coding: utf-8 -*-

"""Module deleting all aws Elastic Container Registry resources."""

import logging
import time

import boto3

from botocore.exceptions import ClientError, EndpointConnectionError


def nuke_all_ecr(older_than_seconds):
    """Elastic Container Registry deleting function.

    Deleting all Elastic Container Registry with
    a timestamp greater than older_than_seconds.

    :param int older_than_seconds:
        The timestamp in seconds used from which the aws
        resource will be deleted
    """
    # Creating Unix timestamp
    time_delete = time.time() - older_than_seconds
    ecr = boto3.client("ecr")

    try:
        ecr.describe_repositories()
    except EndpointConnectionError:
        print("ecr resource is not available in this aws region")
        return

    # Delete ecr
    for registry in ecr_list_registry(time_delete):
        try:
            ecr.delete_repository(repositoryName=registry, force=True)
            print("Nuke ECR Registry{0}".format(registry))
        except ClientError as e:
            logging.error("Unexpected error: %s", e)


def ecr_list_registry(time_delete):
    """Elastic Container Registry list function.

    List the names of all Elastic Container Registry with
    a timestamp lower than time_delete.

    :param int time_delete:
        Timestamp in seconds used for filter Elastic Container Registry
    :returns:
        List of Elastic Container Registry names
    :rtype:
        [str]
    """
    ecr_registry_list = []
    ecr = boto3.client("ecr")
    paginator = ecr.get_paginator("describe_repositories")

    for page in paginator.paginate():
        for registry in page["repositories"]:
            if registry["createdAt"].timestamp() < time_delete:
                ecr_registry = registry["repositoryName"]
                ecr_registry_list.insert(0, ecr_registry)
    return ecr_registry_list
