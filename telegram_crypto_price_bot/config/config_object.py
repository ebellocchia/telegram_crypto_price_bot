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
from enum import Enum
from typing import Any, Dict


#
# Enumerations
#

# Configuration types
class ConfigTypes(Enum):
    pass


#
# Classes
#

# Configuration object class
class ConfigObject:

    config: Dict[ConfigTypes, Any]

    # Constructor
    def __init__(self) -> None:
        self.config = {}

    # Get value
    def GetValue(self,
                 config_type: ConfigTypes) -> Any:
        if not isinstance(config_type, ConfigTypes):
            raise TypeError("BotConfig type is not an enumerative of ConfigTypes")

        return self.config[config_type]

    # Set value
    def SetValue(self,
                 config_type: ConfigTypes,
                 value: Any) -> None:
        if not isinstance(config_type, ConfigTypes):
            raise TypeError("BotConfig type is not an enumerative of ConfigTypes")

        self.config[config_type] = value

    # Get if value is set
    def IsValueSet(self,
                   config_type: ConfigTypes) -> bool:
        return config_type in self.config

    # Convert to string
    def ToString(self) -> str:
        return "\n".join(
            f"{field}: {val}" for field, val in self.config.values()
        )

    # Convert to string
    def __str__(self) -> str:
        return self.ToString()
