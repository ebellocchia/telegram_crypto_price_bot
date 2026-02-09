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

import typing
from abc import ABC
from typing import Iterator, List


class WrappedList(ABC):
    """Abstract base class wrapping a list with additional functionality."""

    list_elements: List[typing.Any]

    def __init__(self) -> None:
        """Initialize an empty wrapped list."""
        self.list_elements = []

    def AddSingle(self,
                  element: typing.Any) -> None:
        """
        Add a single element to the list.

        Args:
            element: Element to add.
        """
        self.list_elements.append(element)

    def AddMultiple(self,
                    elements: List[typing.Any]) -> None:
        """
        Add multiple elements to the list.

        Args:
            elements: List of elements to add.
        """
        self.list_elements.extend(elements)

    def RemoveSingle(self,
                     element: typing.Any) -> None:
        """
        Remove a single element from the list.

        Args:
            element: Element to remove.
        """
        self.list_elements.remove(element)

    def IsElem(self,
               element: typing.Any) -> bool:
        """
        Check if an element is present in the list.

        Args:
            element: Element to check.

        Returns:
            True if element is present, False otherwise.
        """
        return element in self.list_elements

    def Clear(self) -> None:
        """Clear all elements from the list."""
        self.list_elements.clear()

    def Count(self) -> int:
        """
        Get the number of elements in the list.

        Returns:
            Number of elements.
        """
        return len(self.list_elements)

    def Any(self) -> bool:
        """
        Check if the list contains any elements.

        Returns:
            True if list is not empty, False otherwise.
        """
        return self.Count() > 0

    def Empty(self) -> bool:
        """
        Check if the list is empty.

        Returns:
            True if list is empty, False otherwise.
        """
        return self.Count() == 0

    def GetList(self) -> List[typing.Any]:
        """
        Get the underlying list.

        Returns:
            The wrapped list.
        """
        return self.list_elements

    def __iter__(self) -> Iterator[typing.Any]:
        """
        Get an iterator over the list elements.

        Returns:
            Iterator over list elements.
        """
        yield from self.list_elements
