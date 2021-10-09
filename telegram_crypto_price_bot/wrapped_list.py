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
import typing
from typing import Iterator, List
from abc import ABC


#
# Classes
#

# Wrapped list class
class WrappedList(ABC):

    list_elements: List[typing.Any]

    # Constructor
    def __init__(self) -> None:
        self.list_elements = []

    # Add single element
    def AddSingle(self,
                  element: typing.Any) -> None:
        self.list_elements.append(element)

    # Add multiple elements
    def AddMultiple(self,
                    elements: List[typing.Any]) -> None:
        self.list_elements.extend(elements)

    # Remove single element
    def RemoveSingle(self,
                     element: typing.Any) -> None:
        self.list_elements.remove(element)

    # Get if element is present
    def IsElem(self,
               element: typing.Any) -> bool:
        return element in self.list_elements

    # Clear element
    def Clear(self) -> None:
        self.list_elements.clear()

    # Get elements count
    def Count(self) -> int:
        return len(self.list_elements)

    # Get if any
    def Any(self) -> bool:
        return self.Count() > 0

    # Get if empty
    def Empty(self) -> bool:
        return self.Count() == 0

    # Get list
    def GetList(self) -> List[typing.Any]:
        return self.list_elements

    # Get iterator
    def __iter__(self) -> Iterator[typing.Any]:
        yield from self.list_elements
