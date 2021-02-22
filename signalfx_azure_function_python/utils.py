import os
from typing import Dict

import azure.functions as func

from .version import name, version

REGIONS = {
    "East US 2": "eastus2",
    "West US 2": "westus2",
    "South Central US": "southcentralus",
    "West Central US": "westcentralus",
    "East US": "eastus",
    "North Central US": "northcentralus",
    "North Europe": "northeurope",
    "Canada East": "canadaeast",
    "Central US": "centralus",
    "West US": "westus",
    "West Europe": "westeurope",
    "Central India": "centralindia",
    "Southeast Asia": "southeastasia",
    "Canada Central": "canadacentral",
    "Korea Central": "koreacentral",
    "France Central": "francecentral",
    "South India": "southindia",
    "Australia East": "australiaeast",
    "Australia Southeast": "australiasoutheast",
    "Japan West": "japanwest",
    "UK West": "ukwest",
    "UK South": "uksouth",
    "Japan East": "japaneast",
    "East Asia": "eastasia",
    "Brazil South": "brazilsouth",
    "Unknown": "Unknown",
}


def get_metrics_url() -> str:
    """
    Get metrics url from envvar.

    :return: SignalFx's Ingest url
    :rtype: str
    """
    realm = os.environ.get("SIGNALFX_REALM", "us0")

    return f"https://ingest.{realm}.signalfx.com"


def get_access_token() -> str:
    """
    Get SignalFx access token from env var.

    :return: SignalFx's access token
    :rtype: str
    """

    token = os.environ.get("SIGNALFX_AUTH_TOKEN")

    if not token:
        raise ValueError("Missing SIGNALFX_AUTH_TOKEN")
    return token


def get_default_dimensions(context: func.Context) -> Dict[str, any]:
    """
    Get default dimensions from env vars.

    :return: Default dimensions for metrics
    :rtype: dict
    """

    website_owner_name = os.environ.get("WEBSITE_OWNER_NAME", None)
    if website_owner_name:
        subscription_id = website_owner_name.split("+")[0]
    else:
        subscription_id = "Unknown"

    default_dimensions = dict()
    default_dimensions["azure_function_name"] = context.function_name
    default_dimensions["azure_resource_name"] = os.environ.get("WEBSITE_SITE_NAME", None) or os.environ.get(
        "APP_POOL_ID", "Unknown"
    )
    default_dimensions["azure_region"] = REGIONS[os.environ.get("Location", "Unknown")]
    default_dimensions["function_wrapper_version"] = f"{name}-{version}"
    default_dimensions["is_Azure_Function"] = "true"
    default_dimensions["metric_source"] = "azure_function_wrapper"
    default_dimensions["resource_group"] = os.environ.get("WEBSITE_RESOURCE_GROUP", "Unknown")
    default_dimensions["subscription_id"] = subscription_id

    return default_dimensions
