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
from typing import Any

import pyrogram
from pyrogram import Client

from telegram_crypto_price_bot.bot.bot_config_types import BotConfigTypes
from telegram_crypto_price_bot.bot.bot_handlers_config_typing import BotHandlersConfigType
from telegram_crypto_price_bot.command.command_dispatcher import CommandDispatcher, CommandTypes
from telegram_crypto_price_bot.config.config_file_sections_loader import ConfigFileSectionsLoader
from telegram_crypto_price_bot.config.config_object import ConfigObject
from telegram_crypto_price_bot.config.config_typing import ConfigSectionsType
from telegram_crypto_price_bot.logger.logger import Logger
from telegram_crypto_price_bot.message.message_dispatcher import MessageDispatcher, MessageTypes
from telegram_crypto_price_bot.translation.translation_loader import TranslationLoader


#
# Classes
#


# Bot base class
class BotBase:

    config: ConfigObject
    logger: Logger
    translator: TranslationLoader
    client: pyrogram.Client
    cmd_dispatcher: CommandDispatcher
    msg_dispatcher: MessageDispatcher

    # Constructor
    def __init__(self,
                 config_file: str,
                 config_sections: ConfigSectionsType,
                 handlers_config: BotHandlersConfigType) -> None:
        # Load configuration
        self.config = ConfigFileSectionsLoader.Load(config_file, config_sections)
        # Initialize logger
        self.logger = Logger(self.config)
        # Initialize translations
        self.translator = TranslationLoader(self.logger)
        self.translator.Load(self.config.GetValue(BotConfigTypes.APP_LANG_FILE))
        # Initialize client
        self.client = Client(
            self.config.GetValue(BotConfigTypes.SESSION_NAME),
            api_id=self.config.GetValue(BotConfigTypes.API_ID),
            api_hash=self.config.GetValue(BotConfigTypes.API_HASH),
            bot_token=self.config.GetValue(BotConfigTypes.BOT_TOKEN)
        )
        # Initialize helper classes
        self.cmd_dispatcher = CommandDispatcher(self.config, self.logger, self.translator)
        self.msg_dispatcher = MessageDispatcher(self.config, self.logger, self.translator)
        # Setup handlers
        self._SetupHandlers(handlers_config)
        # Log
        self.logger.GetLogger().info("Bot initialization completed")

    # Run bot
    def Run(self) -> None:
        # Print
        self.logger.GetLogger().info("Bot started!\n")
        # Run client
        self.client.run()

    # Setup handlers
    def _SetupHandlers(self,
                       handlers_config: BotHandlersConfigType) -> None:
        def create_handler(handler_type, handler_cfg):
            return handler_type(
                lambda client, message: handler_cfg["callback"](self, client, message),
                handler_cfg["filters"]
            )

        # Add all configured handlers
        for curr_hnd_type, curr_hnd_cfg in handlers_config.items():
            for handler_cfg in curr_hnd_cfg:
                self.client.add_handler(
                    create_handler(curr_hnd_type, handler_cfg)
                )
        # Log
        self.logger.GetLogger().info("Bot handlers set")

    # Dispatch command
    def DispatchCommand(self,
                        client: pyrogram.Client,
                        message: pyrogram.types.Message,
                        cmd_type: CommandTypes,
                        **kwargs: Any) -> None:
        self.cmd_dispatcher.Dispatch(client, message, cmd_type, **kwargs)

    # Handle message
    def HandleMessage(self,
                      client: pyrogram.Client,
                      message: pyrogram.types.Message,
                      msg_type: MessageTypes,
                      **kwargs: Any) -> None:
        self.msg_dispatcher.Dispatch(client, message, msg_type, **kwargs)
