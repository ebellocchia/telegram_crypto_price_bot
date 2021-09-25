# Copyright (c) 2021 Emanuele Bellocchia
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

#
# Imports
#
import functools
from threading import Lock
from typing import Any, Callable


#
# Decorators
#

# Decorator for synchronized functions or methods
def Synchronized(lock: Lock()):
    def _decorator(wrapped: Callable[..., Any]):
        @functools.wraps(wrapped)
        def _wrapper(*args: Any,
                     **kwargs: Any):
            with lock:
                return wrapped(*args, **kwargs)
        return _wrapper
    return _decorator


#
# Classes
#

# Wrapper for utility functions
class Utils:
    # Convert string to bool
    @staticmethod
    def StrToBool(s: str) -> bool:
        s = s.lower()
        if s in ["true", "on", "yes", "y"]:
            return True
        elif s in ["false", "off", "no", "n"]:
            return False
        else:
            raise ValueError("Invalid string")

    # Convert string to integer
    @staticmethod
    def StrToInt(s: str) -> int:
        return int(s)

    # Convert string to float
    @staticmethod
    def StrToFloat(s: str) -> float:
        return float(s)
