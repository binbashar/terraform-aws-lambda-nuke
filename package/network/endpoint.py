# -*- coding: utf-8 -*-

"""Module deleting all aws endpoints."""

import logging

import boto3

from botocore.exceptions import ClientError, EndpointConnectionError


class NukeEndpoint:
    """Abstract endpoint nuke in a class."""

    def __init__(self, region_name=None):
        """Initialize endpoint nuke."""
        if region_name:
            self.ec2 = boto3.client("ec2", region_name=region_name)
        else:
            self.ec2 = boto3.client("ec2")

        try:
            self.ec2.describe_vpc_endpoints()
        except EndpointConnectionError:
            print("Ec2 endpoint resource is not available in this aws region")
            return

    def nuke(self, older_than_seconds):
        """Endpoint deleting function.

        Deleting all aws endpoint with a timestamp greater than
        older_than_seconds.

        :param int older_than_seconds:
            The timestamp in seconds used from which the aws resource
            will be deleted
        """
        for endpoint in self.list_endpoints(older_than_seconds):
            try:
                self.ec2.delete_vpc_endpoints(VpcEndpointIds=[endpoint])
                print("Nuke ec2 endpoint {0}".format(endpoint))
            except ClientError as e:
                error_code = e.response["Error"]["Code"]
                if error_code == "RequestLimitExceeded":
                    logging.info(
                        "DeleteVpcEndpoints operation max retries reached"
                    )
                else:
                    logging.error("Unexpected error: %s", e)

    def list_endpoints(self, time_delete):
        """Aws enpoint list function.

        List IDs of all aws endpoints with a timestamp lower than
        time_delete.

        :param int time_delete:
            Timestamp in seconds used for filter aws endpoint

        :yield Iterator[str]:
            Elastic aws endpoint IDs
        """
        response = self.ec2.describe_vpc_endpoints()

        for endpoint in response["VpcEndpoints"]:
            if endpoint["CreationTimestamp"].timestamp() < time_delete:
                yield endpoint["VpcEndpointId"]
