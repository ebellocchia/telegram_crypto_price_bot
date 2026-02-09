# Copyright (c) 2026 Emanuele Bellocchia
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import functools
from threading import Lock
from typing import Any, Callable, Optional


def Synchronized(lock: Lock):
    """
    Decorator for thread-safe synchronization of functions or methods.

    Args:
        lock: Threading lock to use for synchronization.

    Returns:
        Decorated function with lock protection.
    """
    def _decorator(wrapped: Callable[..., Any]):
        @functools.wraps(wrapped)
        def _wrapper(*args: Any,
                     **kwargs: Any):
            with lock:
                return wrapped(*args, **kwargs)
        return _wrapper
    return _decorator


class Utils:
    """Utility class with static helper methods for type conversions."""

    @staticmethod
    def StrToBool(s: str) -> bool:
        """
        Convert a string to boolean value.

        Args:
            s: String to convert.

        Returns:
            Boolean value.

        Raises:
            ValueError: If string is not a valid boolean representation.
        """
        s = s.lower()
        if s in ["true", "on", "yes", "y"]:
            res = True
        elif s in ["false", "off", "no", "n"]:
            res = False
        else:
            raise ValueError(f"Invalid boolean string: {s}")
        return res

    @staticmethod
    def StrToInt(s: Optional[str]) -> int:
        """
        Convert a string to integer, returning 0 if None.

        Args:
            s: String to convert, or None.

        Returns:
            Integer value, or 0 if input is None.
        """
        if s is None:
            return 0
        return int(s)

    @staticmethod
    def StrToFloat(s: Optional[str]) -> float:
        """
        Convert a string to float, returning 0.0 if None.

        Args:
            s: String to convert, or None.

        Returns:
            Float value, or 0.0 if input is None.
        """
        if s is None:
            return 0.0
        return float(s)
