# SignaFX Python Azure Function Wrapper
SignalFx Python Azure Function Wrapper.

## Usage
The SignalFx Python Azure Function Wrapper is a wrapper around a decorator used to instrument the execution of the function and send metrics to SignalFx

### Installation

Use the github package
```shell
pip install git+https://github.com/claranet/signalfx-azure-function-python@vx.x.x#egg=signalfx-azure-function-python
```

Wrap your function handler

````python
import signalfx_azure_function_python.metrics
import azure.functions as func


@signalfx_azure_function_python.metrics.emit_metrics()
def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    return func.HttpResponse(
        "Hello World"
    )
````

* The context parameter is mandatory to retrieve the function name.
* You can pass extra_dimensions in parameters of emit_metrics decorator.

### Mandatory environment variables

```shell
SIGNALFX_AUTH_TOKEN=xxxxxxx
```

### Optional environment variables

```shell
SIGNALFX_SEND_TIMEOUT=milliseconds for signalfx client timeout. Default 1000
SIGNALFX_REALM=EndPoint Realm. Default: us0
```

### Metrics and dimensions sent by the wrapper

The function wrapper sends the following metrics to SignalFx:

|Metric Name|Type|Description|
|-----------|----|-----------|
| azure.function.invocations | Counter | Count number of function invocations |
| azure.function.errors | Counter | Count number of errors from underlying function handler |
| azure.function.duration | Gauge | Milliseconds in execution time of underlying function handler |

The function wrapper adds the following dimensions to all data points sent to SignalFx:

| Dimension | Description |
|-----------|-------------|
| azure_region | Azure region where the function is executed |
| azure_function_name | Name of the function |
| azure_resource_name | Name of the function app where the function is running |
| function_wrapper_version | SignalFx function wrapper qualifier (e.g. signalfx-azurefunction-0.1.0) |
| is_Azure_Function | Used to differentiate between Azure App Service and Azure Function metrics |
| metric_source | The literal value of 'azure_function_wrapper' |
| resource_group | Name of the resource_group who host the function app |
| subscription_id | Azure subscription ID in which is the function app |

### Deployment

Add the following in your requirements.txt
```
git+https://github.com/claranet/signalfx-azure-function-python@vx.x.x#egg=signalfx-azure-function-python
```

### Testing locally

1) Set up the local Azure Function runtime: https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local

2) Add the environment variables described above to your `local.settings.json`

3) Wrap function as stated above, run the runtime.

### License

Apache Software License v2. Copyright © 2014-2021 Claranet