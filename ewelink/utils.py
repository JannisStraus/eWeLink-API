import asyncio
import secrets
import string
from collections.abc import Callable, Coroutine
from typing import Any, TypeVar

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")
Callback = Callable[..., Coroutine[None, Any, T]]

NONCE_CHARS = string.ascii_lowercase + string.digits


def nonce(length: int = 8) -> str:
    return "".join(secrets.choice(NONCE_CHARS) for _ in range(length))


def main(*args: Any, **kwargs: Any) -> Callable[[Callback], T]:
    def decorator(f: Callback) -> T:
        return asyncio.get_event_loop().run_until_complete(f(*args, **kwargs))

    return decorator


def generics(*types: TypeVar):
    def decorator(f: Callable[..., U]) -> type:
        class _typedfn:
            def __init__(self, obj=None) -> None:
                self._types = tuple()
                self._obj = obj

            def __getitem__(self, _types: tuple[type[type]]):
                self._types: tuple[type[type], ...] = _types
                return self

            def __call__(self, *args: Any, **kwds: Any) -> f.__annotations__.get(
                "return", None
            ):
                kwds.update(
                    types=self._types
                    if isinstance(self._types, tuple)
                    else tuple([self._types])
                )
                if self._obj:
                    return f(self._obj, *args, **kwds)
                else:
                    return f(*args, **kwds)

        _typedfn.__qualname__ = f.__qualname__
        return _typedfn

    return decorator


# Should work but doesn't, still keeping it cause simpler implementation
"""
def generics(*types: TypeVar):
    def decorator(f: Callable[[T, ...], U]) -> type[type[types]]:
        class _typedfn(Generic[types]):
            @functools.wraps(f)
            def __new__(cls: type[V], *args, **kwargs) -> f.__annotations__.get('return', None):
                kwargs.update(types = get_args(cls))
                return f(*args, **kwargs)

        _typedfn.__qualname__ = f.__qualname__
        return _typedfn
    return decorator
"""
