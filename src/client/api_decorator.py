from functools import wraps

from src.client.api_client import ApiClient
from src.common.server_api import ServerApi


def _format_call(name, args, kwargs):
    parts = [repr(a) for a in args] + [f"{k}={v!r}" for k, v in kwargs.items()]
    return f"{name}(" + ", ".join(parts) + ")"


def delegate_abstract_methods(cls):
    """Create concrete delegating wrappers for any abstract methods in the MRO."""
    abstract_names = set()
    for base in cls.__mro__:
        abstract_names |= getattr(base, "__abstractmethods__", set())

    for name in abstract_names:
        # If not implemented on this class, synthesize a delegating method
        if name not in cls.__dict__:

            def make_wrapper(method_name):
                @wraps(
                    getattr(
                        next(b for b in cls.__mro__ if hasattr(b, method_name)),
                        method_name,
                        None,
                    ),
                )
                def wrapper(self, *args, **kwargs):
                    target = getattr(self.server_api, method_name)
                    # print(f"Calling {_format_call(method_name, args, kwargs)}")
                    return target(*args, **kwargs)
                    # print(f" -> {result!r}")

                return wrapper

            setattr(cls, name, make_wrapper(name))

    # Clear abstract flags so the class becomes instantiable
    cls.__abstractmethods__ = frozenset()
    return cls


@delegate_abstract_methods
class ApiDecorator(ApiClient):

    def __init__(self, server_api: ServerApi) -> None:
        self.server_api: ServerApi = server_api

    # Optional: still forward unknown attributes generically (non-abstract helpers, props, etc.)
    def __getattr__(self, name):
        attr = getattr(self.server_api, name)
        if callable(attr):

            @wraps(attr)
            def wrapper(*args, **kwargs):
                # print(f"Calling {_format_call(name, args, kwargs)}")
                return attr(*args, **kwargs)
                # print(f" -> {result!r}")

            return wrapper
        return attr
