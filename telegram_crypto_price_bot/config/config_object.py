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

from enum import Enum
from typing import Any, Dict


class ConfigTypes(Enum):
    """Base enumeration for configuration types."""


class ConfigObject:
    """Object for storing and accessing configuration values."""

    config: Dict[ConfigTypes, Any]

    def __init__(self) -> None:
        """Initialize an empty configuration object."""
        self.config = {}

    def GetValue(self,
                 config_type: ConfigTypes) -> Any:
        """Get a configuration value.

        Args:
            config_type: Configuration type to retrieve

        Returns:
            Configuration value for the specified type

        Raises:
            TypeError: If config_type is not a ConfigTypes enumeration
        """
        if not isinstance(config_type, ConfigTypes):
            raise TypeError("BotConfig type is not an enumerative of ConfigTypes")
        return self.config[config_type]

    def SetValue(self,
                 config_type: ConfigTypes,
                 value: Any) -> None:
        """Set a configuration value.

        Args:
            config_type: Configuration type to set
            value: Value to set for the configuration type

        Raises:
            TypeError: If config_type is not a ConfigTypes enumeration
        """
        if not isinstance(config_type, ConfigTypes):
            raise TypeError("BotConfig type is not an enumerative of ConfigTypes")
        self.config[config_type] = value

    def IsValueSet(self,
                   config_type: ConfigTypes) -> bool:
        """Check if a configuration value is set.

        Args:
            config_type: Configuration type to check

        Returns:
            True if the value is set, False otherwise
        """
        return config_type in self.config
