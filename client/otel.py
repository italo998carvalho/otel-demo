from functools import wraps
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Status, StatusCode
from opentelemetry.propagate import extract

resource = Resource.create({
    'service.name': 'application-client'
})

provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="http://localhost:4318/v1/traces"))
provider.add_span_processor(processor)

trace.set_tracer_provider(provider)

tracer = trace.get_tracer('application.client')

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
