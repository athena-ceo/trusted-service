from abc import ABC, abstractmethod
from functools import wraps


class Api(ABC):
    @abstractmethod
    def f1(self, i: int):
        pass

    @abstractmethod
    def f2(self, s: str):
        pass

    @abstractmethod
    def f3(self, l: list[str], m: int):
        pass


#  Please implement a generic decoration/delegation mechanism to implement generically:

class ApiDecorator2(Api):
    def __init__(self, api: Api):
        self.api = api

    def f1(self, i: int):
        print(f"Calling f1(i={i})")
        r = self.api.f1(i)
        print(f" -> {r}")
        return r

    def f2(self, s: str):
        print(f"Calling f2(s={s})")
        r = self.api.f2(s)
        print(f" -> {r}")
        return r

    def f3(self, l: list[str], m: int):
        print(f"Calling f3(l={l}, m={m})")
        r = self.api.f3(l, m)
        print(f" -> {r}")
        return r


class MyApi(Api):
    def f1(self, i: int):
        return 2 * i

    def f2(self, s: str):
        return len(s)

    def f3(self, l: list[str], m: int):
        return len(l) * m


my_api = MyApi()

print(my_api.f1(10))

print(my_api.f2("abc"))

print(my_api.f3(["abc", "def", "ghi"], 3))






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
                @wraps(getattr(next(b for b in cls.__mro__ if hasattr(b, method_name)), method_name, None))
                def wrapper(self, *args, **kwargs):
                    target = getattr(self._api, method_name)
                    print(f"Calling {_format_call(method_name, args, kwargs)}")
                    result = target(*args, **kwargs)
                    print(f" -> {result!r}")
                    return result
                return wrapper
            setattr(cls, name, make_wrapper(name))

    # Clear abstract flags so the class becomes instantiable
    cls.__abstractmethods__ = frozenset()
    return cls


@delegate_abstract_methods
class ApiDecorator(Api):
    def __init__(self, api: Api):
        self._api = api

    # Optional: still forward unknown attributes generically (non-abstract helpers, props, etc.)
    def __getattr__(self, name):
        attr = getattr(self._api, name)
        if callable(attr):
            @wraps(attr)
            def wrapper(*args, **kwargs):
                print(f"Calling {_format_call(name, args, kwargs)}")
                result = attr(*args, **kwargs)
                print(f" -> {result!r}")
                return result
            return wrapper
        return attr

my_api = ApiDecorator(my_api)

print(my_api.f1(10))

print(my_api.f2("abc"))

print(my_api.f3(["abc", "def", "ghi"], 3))
