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
from enum import Enum, auto, unique
from typing import Any, Dict


#
# Enumerations
#

# Configuration types
@unique
class ConfigTypes(Enum):
    SESSION_NAME = auto()
    # App
    APP_TEST_MODE = auto()
    APP_LANG_FILE = auto()
    # Task
    TASKS_MAX_NUM = auto()
    # Chart
    CHART_DISPLAY = auto()
    CHART_DATE_FORMAT = auto()
    CHART_BACKGROUND_COLOR = auto()
    CHART_TITLE_COLOR = auto()
    CHART_FRAME_COLOR = auto()
    CHART_AXES_COLOR = auto()
    CHART_LINE_COLOR = auto()
    CHART_LINE_STYLE = auto()
    CHART_LINE_WIDTH = auto()
    CHART_DISPLAY_GRID = auto()
    CHART_GRID_MAX_SIZE = auto()
    CHART_GRID_COLOR = auto()
    CHART_GRID_LINE_STYLE = auto()
    CHART_GRID_LINE_WIDTH = auto()
    # Price
    PRICE_DISPLAY_MARKET_CAP = auto()
    PRICE_DISPLAY_MARKET_CAP_RANK = auto()
    # Logging
    LOG_LEVEL = auto()
    LOG_CONSOLE_ENABLED = auto()
    LOG_FILE_ENABLED = auto()
    LOG_FILE_NAME = auto()
    LOG_FILE_USE_ROTATING = auto()
    LOG_FILE_APPEND = auto()
    LOG_FILE_MAX_BYTES = auto()
    LOG_FILE_BACKUP_CNT = auto()


#
# Classes
#

# Configuration error class
class ConfigError(Exception):
    pass


# Configuration class
class Config:

    config: Dict[ConfigTypes, Any]

    # Constructor
    def __init__(self) -> None:
        self.config = {}

    # Get value
    def GetValue(self,
                 config_type: ConfigTypes) -> Any:
        if not isinstance(config_type, ConfigTypes):
            raise TypeError("Config type is not an enumerative of ConfigTypes")

        return self.config[config_type]

    # Set value
    def SetValue(self,
                 config_type: ConfigTypes,
                 value: Any) -> None:
        if not isinstance(config_type, ConfigTypes):
            raise TypeError("Config type is not an enumerative of ConfigTypes")

        self.config[config_type] = value

    # Get if value is set
    def IsValueSet(self,
                   config_type: ConfigTypes) -> bool:
        return config_type in self.config
