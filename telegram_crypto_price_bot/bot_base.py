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
import pyrogram
from abc import ABC, abstractmethod
from pyrogram import Client
from typing import Any
from telegram_crypto_price_bot.command_dispatcher import CommandDispatcher, CommandTypes
from telegram_crypto_price_bot.config import ConfigTypes
from telegram_crypto_price_bot.config_loader import ConfigLoader
from telegram_crypto_price_bot.logger import Logger
from telegram_crypto_price_bot.message_dispatcher import MessageDispatcher
from telegram_crypto_price_bot.translation_loader import TranslationLoader


#
# Classes
#

# Bot base class
class BotBase(ABC):
    # Constructor
    def __init__(self,
                 config_file: str) -> None:
        # Load configuration
        config_ldr = ConfigLoader(config_file)
        config_ldr.Load()
        self.config = config_ldr.GetConfig()
        # Initialize logger
        self.logger = Logger(self.config)
        # Initialize translations
        self.translator = TranslationLoader(self.logger)
        self.translator.Load(self.config.GetValue(ConfigTypes.APP_LANG_FILE))
        # Initialize client
        self.client = Client(self.config.GetValue(ConfigTypes.SESSION_NAME),
                             config_file=config_file)
        # Initialize helper classes
        self.cmd_dispatcher = CommandDispatcher(self.config, self.logger, self.translator)
        self.msg_dispatcher = MessageDispatcher(self.config, self.logger, self.translator)
        # Setup handlers
        self._SetupHandlers()
        # Log
        self.logger.GetLogger().info("Bot initialization completed")

    # Run bot
    def Run(self) -> None:
        # Print
        self.logger.GetLogger().info("Bot started!\n")
        # Run client
        self.client.run()

    # Dispatch command
    def _DispatchCommand(self,
                         client: pyrogram.Client,
                         message: pyrogram.types.Message,
                         cmd_type: CommandTypes,
                         **kwargs: Any) -> None:
        self.cmd_dispatcher.Dispatch(client, message, cmd_type, **kwargs)

    # Handle message
    def _HandleMessage(self,
                       client: pyrogram.Client,
                       message: pyrogram.types.Message,
                       **kwargs: Any) -> None:
        self.msg_dispatcher.Dispatch(client, message, **kwargs)

    # Setup handlers
    @abstractmethod
    def _SetupHandlers(self) -> None:
        pass
