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
from typing import Any, Dict, Type
import pyrogram
from telegram_crypto_price_bot.command_base import CommandBase
from telegram_crypto_price_bot.commands import (
    HelpCmd, AliveCmd, SetTestModeCmd, IsTestModeCmd,
    PriceGetSingleCmd,
    PriceTaskStartCmd, PriceTaskStopCmd, PriceTaskStopAllCmd, PriceTaskPauseCmd, PriceTaskResumeCmd,
    PriceTaskSendInSameMsgCmd, PriceTaskDeleteLastMsgCmd, PriceTaskInfoCmd
)
from telegram_crypto_price_bot.config import Config
from telegram_crypto_price_bot.logger import Logger
from telegram_crypto_price_bot.translation_loader import TranslationLoader


#
# Enumerations
#

# Command types
@unique
class CommandTypes(Enum):
    START_CMD = auto()
    HELP_CMD = auto()
    ALIVE_CMD = auto()
    SET_TEST_MODE_CMD = auto()
    IS_TEST_MODE_CMD = auto()
    PRICE_GET_SINGLE_CMD = auto()
    PRICE_TASK_START_CMD = auto()
    PRICE_TASK_STOP_CMD = auto()
    PRICE_TASK_STOP_ALL_CMD = auto()
    PRICE_TASK_PAUSE_CMD = auto()
    PRICE_TASK_RESUME_CMD = auto()
    PRICE_TASK_SEND_IN_SAME_MSG_CMD = auto()
    PRICE_TASK_DELETE_LAST_MSG_CMD = auto()
    PRICE_TASK_INFO_CMD = auto()


#
# Classes
#

# Comstant for command dispatcher class
class CommandDispatcherConst:
    # Command to class map
    CMD_TYPE_TO_CLASS: Dict[CommandTypes, Type[CommandBase]] = {
        CommandTypes.START_CMD: HelpCmd,
        CommandTypes.HELP_CMD: HelpCmd,
        CommandTypes.ALIVE_CMD: AliveCmd,
        CommandTypes.SET_TEST_MODE_CMD: SetTestModeCmd,
        CommandTypes.IS_TEST_MODE_CMD: IsTestModeCmd,
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


# Command dispatcher class
class CommandDispatcher:

    config: Config
    logger: Logger
    translator: TranslationLoader

    # Constructor
    def __init__(self,
                 config: Config,
                 logger: Logger,
                 translator: TranslationLoader) -> None:
        self.config = config
        self.logger = logger
        self.translator = translator

    # Dispatch command
    def Dispatch(self,
                 client: pyrogram.Client,
                 message: pyrogram.types.Message,
                 cmd_type: CommandTypes,
                 **kwargs: Any) -> None:
        if not isinstance(cmd_type, CommandTypes):
            raise TypeError("Command type is not an enumerative of CommandTypes")

        # Log
        self.logger.GetLogger().info(f"Dispatching command type: {cmd_type}")

        # Create and execute command if existent
        if cmd_type in CommandDispatcherConst.CMD_TYPE_TO_CLASS:
            cmd_class = CommandDispatcherConst.CMD_TYPE_TO_CLASS[cmd_type](client,
                                                                           self.config,
                                                                           self.logger,
                                                                           self.translator)
            cmd_class.Execute(message, **kwargs)
