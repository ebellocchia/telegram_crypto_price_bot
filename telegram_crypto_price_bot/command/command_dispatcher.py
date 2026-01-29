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

from enum import Enum, auto, unique
from typing import Any, Dict, Type

import pyrogram

from telegram_crypto_price_bot.command.command_base import CommandBase
from telegram_crypto_price_bot.command.commands import (
    AliveCmd,
    HelpCmd,
    IsTestModeCmd,
    PriceGetSingleCmd,
    PriceTaskDeleteLastMsgCmd,
    PriceTaskInfoCmd,
    PriceTaskPauseCmd,
    PriceTaskResumeCmd,
    PriceTaskSendInSameMsgCmd,
    PriceTaskStartCmd,
    PriceTaskStopAllCmd,
    PriceTaskStopCmd,
    SetTestModeCmd,
    VersionCmd,
)
from telegram_crypto_price_bot.config.config_object import ConfigObject
from telegram_crypto_price_bot.logger.logger import Logger
from telegram_crypto_price_bot.translation.translation_loader import TranslationLoader


@unique
class CommandTypes(Enum):
    """Enumeration of available command types."""

    START_CMD = auto()
    HELP_CMD = auto()
    ALIVE_CMD = auto()
    SET_TEST_MODE_CMD = auto()
    IS_TEST_MODE_CMD = auto()
    VERSION_CMD = auto()
    PRICE_GET_SINGLE_CMD = auto()
    PRICE_TASK_START_CMD = auto()
    PRICE_TASK_STOP_CMD = auto()
    PRICE_TASK_STOP_ALL_CMD = auto()
    PRICE_TASK_PAUSE_CMD = auto()
    PRICE_TASK_RESUME_CMD = auto()
    PRICE_TASK_SEND_IN_SAME_MSG_CMD = auto()
    PRICE_TASK_DELETE_LAST_MSG_CMD = auto()
    PRICE_TASK_INFO_CMD = auto()


class CommandDispatcherConst:
    """Constants for command dispatcher class."""

    CMD_TYPE_TO_CLASS: Dict[CommandTypes, Type[CommandBase]] = {
        CommandTypes.START_CMD: HelpCmd,
        CommandTypes.HELP_CMD: HelpCmd,
        CommandTypes.ALIVE_CMD: AliveCmd,
        CommandTypes.SET_TEST_MODE_CMD: SetTestModeCmd,
        CommandTypes.IS_TEST_MODE_CMD: IsTestModeCmd,
        CommandTypes.VERSION_CMD: VersionCmd,
        CommandTypes.PRICE_GET_SINGLE_CMD: PriceGetSingleCmd,
        CommandTypes.PRICE_TASK_START_CMD: PriceTaskStartCmd,
        CommandTypes.PRICE_TASK_STOP_CMD: PriceTaskStopCmd,
        CommandTypes.PRICE_TASK_STOP_ALL_CMD: PriceTaskStopAllCmd,
        CommandTypes.PRICE_TASK_PAUSE_CMD: PriceTaskPauseCmd,
        CommandTypes.PRICE_TASK_RESUME_CMD: PriceTaskResumeCmd,
        CommandTypes.PRICE_TASK_SEND_IN_SAME_MSG_CMD: PriceTaskSendInSameMsgCmd,
        CommandTypes.PRICE_TASK_DELETE_LAST_MSG_CMD: PriceTaskDeleteLastMsgCmd,
        CommandTypes.PRICE_TASK_INFO_CMD: PriceTaskInfoCmd,
    }


class CommandDispatcher:
    """Dispatcher for routing command types to their respective command classes."""

    config: ConfigObject
    logger: Logger
    translator: TranslationLoader

    def __init__(self,
                 config: ConfigObject,
                 logger: Logger,
                 translator: TranslationLoader) -> None:
        """Initialize the command dispatcher.

        Args:
            config: Configuration object
            logger: Logger instance
            translator: Translation loader
        """
        self.config = config
        self.logger = logger
        self.translator = translator

    def Dispatch(self,
                 client: pyrogram.Client,
                 message: pyrogram.types.Message,
                 cmd_type: CommandTypes,
                 **kwargs: Any) -> None:
        """Dispatch a command to its corresponding handler.

        Args:
            client: Pyrogram client instance
            message: Telegram message containing the command
            cmd_type: Type of command to dispatch
            **kwargs: Additional keyword arguments for the command

        Raises:
            TypeError: If cmd_type is not a CommandTypes enumeration
        """
        if not isinstance(cmd_type, CommandTypes):
            raise TypeError("Command type is not an enumerative of CommandTypes")

        self.logger.GetLogger().info(f"Dispatching command type: {cmd_type}")

        if cmd_type in CommandDispatcherConst.CMD_TYPE_TO_CLASS:
            cmd_class = CommandDispatcherConst.CMD_TYPE_TO_CLASS[cmd_type](client, self.config, self.logger, self.translator)
            cmd_class.Execute(message, **kwargs)
