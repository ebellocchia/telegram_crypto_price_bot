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

import logging
import logging.handlers
import os
from typing import Union

from telegram_crypto_price_bot.bot.bot_config_types import BotConfigTypes
from telegram_crypto_price_bot.config.config_object import ConfigObject


class LoggerConst:
    """Constants for logger configuration."""

    LOGGER_NAME: str = ""
    LOG_CONSOLE_FORMAT: str = "%(asctime)-15s %(levelname)s - %(message)s"
    LOG_FILE_FORMAT: str = "%(asctime)-15s %(levelname)s - [%(name)s.%(funcName)s:%(lineno)d] %(message)s"


class Logger:
    """Logger class for managing application logging to console and file."""

    config: ConfigObject
    logger: logging.Logger

    def __init__(self,
                 config: ConfigObject) -> None:
        """
        Initialize the logger with configuration.

        Args:
            config: Configuration object containing logging settings.
        """
        self.config = config
        self.logger = logging.getLogger(LoggerConst.LOGGER_NAME)
        self.__Init()

    def GetLogger(self) -> logging.Logger:
        """
        Get the logger instance.

        Returns:
            Logger instance.
        """
        return self.logger

    def __Init(self) -> None:
        """Initialize logger with configured handlers."""
        self.__ConfigureRootLogger()
        self.__ConfigureConsoleLogger()
        self.__ConfigureFileLogger()
        self.logger.info("Logger initialized")

    def __ConfigureRootLogger(self) -> None:
        """Configure the root logger level."""
        self.logger.setLevel(self.config.GetValue(BotConfigTypes.LOG_LEVEL))

    def __ConfigureConsoleLogger(self) -> None:
        """Configure console logging handler if enabled."""
        if self.config.GetValue(BotConfigTypes.LOG_CONSOLE_ENABLED):
            ch = logging.StreamHandler()
            ch.setLevel(self.config.GetValue(BotConfigTypes.LOG_LEVEL))
            ch.setFormatter(logging.Formatter(LoggerConst.LOG_CONSOLE_FORMAT))
            self.logger.addHandler(ch)

    def __ConfigureFileLogger(self) -> None:
        """Configure file logging handler if enabled."""
        if self.config.GetValue(BotConfigTypes.LOG_FILE_ENABLED):
            log_file_name = self.config.GetValue(BotConfigTypes.LOG_FILE_NAME)
            self.__MakeLogDir(log_file_name)

            fh: Union[logging.handlers.RotatingFileHandler, logging.FileHandler]
            if self.config.GetValue(BotConfigTypes.LOG_FILE_USE_ROTATING):
                fh = logging.handlers.RotatingFileHandler(log_file_name,
                                                          maxBytes=self.config.GetValue(BotConfigTypes.LOG_FILE_MAX_BYTES),
                                                          backupCount=self.config.GetValue(BotConfigTypes.LOG_FILE_BACKUP_CNT),
                                                          encoding="utf-8")
            else:
                fh = logging.FileHandler(log_file_name,
                                         mode="a" if self.config.GetValue(BotConfigTypes.LOG_FILE_APPEND) else "w",
                                         encoding="utf-8")

            fh.setLevel(self.config.GetValue(BotConfigTypes.LOG_LEVEL))
            fh.setFormatter(logging.Formatter(LoggerConst.LOG_FILE_FORMAT))
            self.logger.addHandler(fh)

    @staticmethod
    def __MakeLogDir(file_name: str) -> None:
        """
        Create log directory if it doesn't exist.

        Args:
            file_name: Path to the log file.
        """
        try:
            os.makedirs(os.path.dirname(file_name))
        except FileExistsError:
            pass
