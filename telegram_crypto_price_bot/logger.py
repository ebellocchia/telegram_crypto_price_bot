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
import logging
import logging.handlers
import os
from typing import Union
from telegram_crypto_price_bot.config import ConfigTypes, Config


#
# Classes
#

# Constants for logger class
class LoggerConst:
    # Logger name
    LOGGER_NAME: str = ""
    # Log formats
    LOG_CONSOLE_FORMAT: str = "%(asctime)-15s %(levelname)s - %(message)s"
    LOG_FILE_FORMAT: str = "%(asctime)-15s %(levelname)s - [%(name)s.%(funcName)s:%(lineno)d] %(message)s"


# Logger class
class Logger:
    # Constructor
    def __init__(self,
                 config: Config) -> None:
        self.config = config
        self.logger = logging.getLogger(LoggerConst.LOGGER_NAME)
        self.__Init()

    # Get logger
    def GetLogger(self) -> logging.Logger:
        return self.logger

    # Initialize
    def __Init(self) -> None:
        # Configure loggers
        self.__ConfigureRootLogger()
        self.__ConfigureConsoleLogger()
        self.__ConfigureFileLogger()
        # Log
        self.logger.info("Logger initialized")

    # Configure root logger
    def __ConfigureRootLogger(self) -> None:
        self.logger.setLevel(self.config.GetValue(ConfigTypes.LOG_LEVEL))

    # Configure console logger
    def __ConfigureConsoleLogger(self) -> None:
        # Configure console handler if required
        if self.config.GetValue(ConfigTypes.LOG_CONSOLE_ENABLED):
            # Create handler
            ch = logging.StreamHandler()
            ch.setLevel(self.config.GetValue(ConfigTypes.LOG_LEVEL))
            ch.setFormatter(logging.Formatter(LoggerConst.LOG_CONSOLE_FORMAT))
            # Add handler
            self.logger.addHandler(ch)

    # Configure file logger
    def __ConfigureFileLogger(self) -> None:
        # Configure file handler if required
        if self.config.GetValue(ConfigTypes.LOG_FILE_ENABLED):
            # Get file name
            log_file_name = self.config.GetValue(ConfigTypes.LOG_FILE_NAME)
            # Create log directories if needed
            self.__MakeLogDir(log_file_name)

            # Create file handler
            fh: Union[logging.handlers.RotatingFileHandler, logging.FileHandler]
            if self.config.GetValue(ConfigTypes.LOG_FILE_USE_ROTATING):
                fh = logging.handlers.RotatingFileHandler(log_file_name,
                                                          maxBytes=self.config.GetValue(ConfigTypes.LOG_FILE_MAX_BYTES),
                                                          backupCount=self.config.GetValue(ConfigTypes.LOG_FILE_BACKUP_CNT),
                                                          encoding="utf-8")
            else:
                fh = logging.FileHandler(log_file_name,
                                         mode="a" if self.config.GetValue(ConfigTypes.LOG_FILE_APPEND) else "w",
                                         encoding="utf-8")

            fh.setLevel(self.config.GetValue(ConfigTypes.LOG_LEVEL))
            fh.setFormatter(logging.Formatter(LoggerConst.LOG_FILE_FORMAT))
            # Add handler
            self.logger.addHandler(fh)

    # Make log directories
    @staticmethod
    def __MakeLogDir(file_name: str) -> None:
        try:
            os.makedirs(os.path.dirname(file_name))
        except FileExistsError:
            pass
