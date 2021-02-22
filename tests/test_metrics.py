import sys
from os.path import dirname, realpath

sys.path.append(dirname(dirname(realpath(__file__))))

from collections import namedtuple
import unittest.mock
import os
import requests_mock
import gzip
import io
import blackboxprotobuf
from signalfx_azure_function_python import metrics, utils, version

from . import helpers

azcontext = namedtuple("Context", ["function_name"])
CONTEXT = azcontext(function_name="TestFunction")
ENVVARS = {
    "SIGNALFX_AUTH_TOKEN": "SFXTOKEN",
    "SIGNALFX_REALM": "eu0",
    "WEBSITE_SITE_NAME": "FunctionWebSiteName",
    "Location": "West Europe",
    "WEBSITE_RESOURCE_GROUP": "TheResourceGroup",
    "WEBSITE_OWNER_NAME": "subscription-id+anotherstring"
}
BAD_ENVVARS = ENVVARS.copy()
BAD_ENVVARS.pop("SIGNALFX_AUTH_TOKEN")
BAD_ENVVARS.pop("WEBSITE_RESOURCE_GROUP")
BAD_ENVVARS.pop("WEBSITE_OWNER_NAME")


@unittest.mock.patch.dict("os.environ", ENVVARS, clear=True)
class AzureFunctionPythonMetricsTestCase(unittest.TestCase):
    def test_emit_metrics(self):
        with requests_mock.Mocker() as m:
            m.post(requests_mock.ANY, status_code=200)

            @metrics.emit_metrics()
            def main(req, context):
                return None

            main(req="aaaa", context=CONTEXT)
            req_realm = m.last_request.netloc.split(".")[1]

            content = gzip.GzipFile(fileobj=io.BytesIO(m.last_request.body)).read()
            message, typedef = blackboxprotobuf.decode_message(content)
            message_dimensions = message["1"]["6"]
            dp_dimensions = helpers.pbuf_dimensions_to_namespace(message_dimensions)

            # Check if history request contains azure.function.invocations
            # and azure.function.duration which must be sent when everything
            # is ok
            req_history = m.request_history
            metric_names = list()
            for hist in req_history:
                decoded_msg = helpers.decode_sfx_request(hist.body)
                # print(decoded_msg)
                metric_name = decoded_msg["1"]["2"]
                metric_names.append(metric_name)

            self.assertEqual(req_realm, os.environ.get("SIGNALFX_REALM"))
            self.assertEqual(dp_dimensions.azure_region, utils.REGIONS[ENVVARS["Location"]])
            self.assertEqual(dp_dimensions.azure_function_name, CONTEXT.function_name)
            self.assertEqual(dp_dimensions.azure_resource_name, ENVVARS["WEBSITE_SITE_NAME"])
            self.assertEqual(dp_dimensions.function_wrapper_version, f"{version.name}-{version.version}")
            self.assertEqual(dp_dimensions.is_Azure_Function, "true")
            self.assertEqual(dp_dimensions.metric_source, "azure_function_wrapper")
            self.assertEqual(dp_dimensions.resource_group, ENVVARS["WEBSITE_RESOURCE_GROUP"])
            self.assertEqual(dp_dimensions.subscription_id, ENVVARS["WEBSITE_OWNER_NAME"].split('+')[0])
            self.assertIn(b"azure.function.duration", metric_names)
            self.assertIn(b"azure.function.invocations", metric_names)
            self.assertNotIn(b"azure.function.errors", metric_names)

            m.reset_mock()

    def test_emit_metrics_with_extra_dimensions(self):
        with requests_mock.Mocker() as m:
            m.post(requests_mock.ANY, status_code=200)

            @metrics.emit_metrics(extra_dimensions={"extraDim1": "valueOfExtraDim1", "extraDim2": "valueOfExtraDim2"})
            def main(req, context):
                return None

            main(req="aaaaaa", context=CONTEXT)

            content = gzip.GzipFile(fileobj=io.BytesIO(m.last_request.body)).read()
            message, typedef = blackboxprotobuf.decode_message(content)
            message_dimensions = message["1"]["6"]
            dp_dimensions = helpers.pbuf_dimensions_to_namespace(message_dimensions)

            self.assertTrue(hasattr(dp_dimensions, "extraDim1"))
            self.assertTrue(hasattr(dp_dimensions, "extraDim2"))
            self.assertEqual(dp_dimensions.extraDim1, "valueOfExtraDim1")
            self.assertEqual(dp_dimensions.extraDim2, "valueOfExtraDim2")


@unittest.mock.patch.dict("os.environ", BAD_ENVVARS, clear=True)
class AzureFunctionPythonMetricsFailuresTestCase(unittest.TestCase):
    def test_emit_metrics_mainfunc_failure(self):
        @metrics.emit_metrics()
        def main(req, context):
            return None

        with self.assertRaises(ValueError) as err:
            main(req="aaaaa", context=CONTEXT)
        self.assertEqual(err.exception.args[0], "Missing SIGNALFX_AUTH_TOKEN")

    @unittest.mock.patch.dict("os.environ", dict(BAD_ENVVARS,
                                                 **{"SIGNALFX_AUTH_TOKEN": "jskljfsqmlfjskq"}),
                              clear=True)
    def test_emit_metrics_missing_dim(self):

        @metrics.emit_metrics()
        def main(req, context):
            return None

        with requests_mock.Mocker() as m:
            m.post(requests_mock.ANY, status_code=200)

            main(req="blabla", context=CONTEXT)

            content = gzip.GzipFile(fileobj=io.BytesIO(m.last_request.body)).read()
            message, typedef = blackboxprotobuf.decode_message(content)
            message_dimensions = message["1"]["6"]
            dp_dimensions = helpers.pbuf_dimensions_to_namespace(message_dimensions)
            self.assertEqual(dp_dimensions.subscription_id, "Unknown")
            self.assertEqual(dp_dimensions.resource_group, "Unknown")

