import datetime
import functools
import os
from typing import Dict, Union, List
import logging

import signalfx

from . import utils

DATAPOINT_TYPE = Dict[str, Dict[str, Union[str, int, Dict[str, any]]]]
SFX_OUTPUT_TYPE = Dict[str, Union[str, int, Dict[str, any]]]

default_dimensions = dict()
ingest = None

logging.getLogger("signalfx_azure_function_python")


def map_datapoint(data_point: DATAPOINT_TYPE) -> SFX_OUTPUT_TYPE:
    """
    Create dict value to send to SFX.
    :param data_point: Dict with values to send
    :type data_point: dict
    :return: SignalFx data
    :rtype: dict
    """
    return {
        "metric": data_point["metric"],
        "value": data_point["value"],
        "dimensions": dict(data_point["dimensions"], **default_dimensions) if "dimensions" in data_point else default_dimensions,
    }


def map_datapoints(data_points: List[DATAPOINT_TYPE]) -> List[SFX_OUTPUT_TYPE]:
    """
    Generate list of data to send to SFX.

    :param data_points: List of datapoints
    :type data_points: List
    :return: List of data to send to SFX
    :rtype: list
    """
    return [map_datapoint(data_point) for data_point in data_points]


def send_metric(counters: List[SFX_OUTPUT_TYPE] = [], gauges: List[SFX_OUTPUT_TYPE] = []):
    """
    Send metrics to ingest endpoint.

    :param counters: List of counters to send
    :type counters: list
    :param gauges: List of gauges to send
    :type gauges: list
    """
    if ingest:
        logging.debug("Counters to send: %s", counters)
        logging.debug("Gauges to send: %s", gauges)
        ingest.send(counters=map_datapoints(counters), gauges=map_datapoints(gauges))


def send_counter(metric_name: str, metric_value: int = 1, dimensions: Dict[str, any] = {}) -> None:
    """
    Send counter to SFX.

    :param metric_name: Name of the metric
    :type metric_name: str
    :param metric_value: Value of the metric. Default = 1
    :type metric_value: int
    :param dimensions: Dimensions to send with the metric
    :type dimensions: dict
    :return: None
    :rtype: None
    """
    send_metric(counters=[{"metric": metric_name, "value": metric_value, "dimensions": dimensions}])


def send_gauge(metric_name: str, metric_value: float, dimensions: Dict[str, any] = {}) -> None:
    """
    Send gauge to SFX.

    :param metric_name: Name of the metric
    :type metric_name: str
    :param metric_value: Value of the metric.
    :type metric_value: float
    :param dimensions: Dimensions to send with the metric
    :return: None
    :rtype: None
    """
    send_metric(gauges=[{"metric": metric_name, "value": metric_value, "dimensions": dimensions}])


def emit_metrics(extra_dimensions=None):
    """
    Wrapper decorator.

    :param extra_dimensions: Extra dimentions to add to metrics
    :type extra_dimensions: dict
    :return: Wrapped function
    """

    def wrapper_decorator(func):
        """Decorator."""

        @functools.wraps(func)
        def wrapper_send_metrics(*args, **kwargs):
            access_token = utils.get_access_token()
            global ingest

            ingest_endpoint = utils.get_metrics_url()
            ingest_timeout = float(os.environ.get("SIGNALFX_SEND_TIMEOUT", 0.3))

            sfx = signalfx.SignalFx(ingest_endpoint=ingest_endpoint)

            ingest = sfx.ingest(access_token, timeout=(1, ingest_timeout))
            context = kwargs.get("context", None)

            global default_dimensions
            default_dimensions = utils.get_default_dimensions(context)
            default_dimensions["metric_source"] = "azure_function_wrapper"

            if extra_dimensions is not None:
                default_dimensions = dict(default_dimensions, **extra_dimensions)

            start_counters = [{"metric": "azure.function.invocations", "value": 1}]
            send_metric(counters=start_counters)
            end_counters = []
            time_start = datetime.datetime.now()
            try:
                result = func(*args, **kwargs)
                return result
            except Exception:
                end_counters.append({"metric": "azure.function.errors", "value": 1})
                raise
            finally:
                time_taken = datetime.datetime.now() - time_start
                send_metric(
                    counters=end_counters,
                    gauges=[{"metric": "azure.function.duration", "value": time_taken.total_seconds() * 1000}],
                )

                # flush everything
                ingest.stop()

        return wrapper_send_metrics

    return wrapper_decorator
