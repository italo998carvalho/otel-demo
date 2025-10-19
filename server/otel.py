from functools import wraps
from opentelemetry import trace, metrics
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter, PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
)
from opentelemetry.trace import Status, StatusCode
from opentelemetry.propagate import extract

resource = Resource.create({
    'service.name': 'application-server'
})

tracer_provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="http://localhost:4318/v1/traces"))
tracer_provider.add_span_processor(processor)

trace.set_tracer_provider(tracer_provider)

tracer = trace.get_tracer('application.server')

# =================
metric_reader = PeriodicExportingMetricReader(ConsoleMetricExporter())
provider = MeterProvider(metric_readers=[metric_reader])

# Sets the global default meter provider
metrics.set_meter_provider(provider)

# Creates a meter from the global meter provider
meter = metrics.get_meter("my.meter.name")

def start_span(name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            tracer = trace.get_tracer(__name__)
            ctx = _extract_context(kwargs)
            with tracer.start_as_current_span(name, context=ctx) as span:
                result = func(*args, **kwargs)
                if span.status.status_code == StatusCode.UNSET:
                    span.set_status(Status(StatusCode.OK))
                return result
        return wrapper
    return decorator

def _extract_context(wrapper_args):
    request = wrapper_args.get('request', None)
    if request is not None:
        return extract(request.headers)
    else:
        return {}
