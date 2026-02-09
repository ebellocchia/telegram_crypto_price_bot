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

from typing import Any

import pyrogram
from pyrogram import Client, idle

from telegram_crypto_price_bot.bot.bot_config_types import BotConfigTypes
from telegram_crypto_price_bot.bot.bot_handlers_config_typing import BotHandlersConfigType
from telegram_crypto_price_bot.command.command_dispatcher import CommandDispatcher, CommandTypes
from telegram_crypto_price_bot.config.config_file_sections_loader import ConfigFileSectionsLoader
from telegram_crypto_price_bot.config.config_object import ConfigObject
from telegram_crypto_price_bot.config.config_typing import ConfigSectionsType
from telegram_crypto_price_bot.logger.logger import Logger
from telegram_crypto_price_bot.message.message_dispatcher import MessageDispatcher, MessageTypes
from telegram_crypto_price_bot.translation.translation_loader import TranslationLoader


class BotBase:
    """Base class for Telegram bot using Pyrogram client."""

    config: ConfigObject
    logger: Logger
    translator: TranslationLoader
    client: pyrogram.Client
    cmd_dispatcher: CommandDispatcher
    msg_dispatcher: MessageDispatcher
    handlers_config: BotHandlersConfigType

    def __init__(self,
                 config_file: str,
                 config_sections: ConfigSectionsType,
                 handlers_config: BotHandlersConfigType) -> None:
        """
        Initialize the bot with configuration, logger, translator, and handlers.

        Args:
            config_file: Path to the configuration file.
            config_sections: Configuration sections to load.
            handlers_config: Handlers configuration for the bot.
        """
        self.config = ConfigFileSectionsLoader.Load(config_file, config_sections)
        self.logger = Logger(self.config)
        self.translator = TranslationLoader(self.logger)
        self.translator.Load(self.config.GetValue(BotConfigTypes.APP_LANG_FILE))
        self.handlers_config = handlers_config
        self.cmd_dispatcher = CommandDispatcher(self.config, self.logger, self.translator)
        self.msg_dispatcher = MessageDispatcher(self.config, self.logger, self.translator)
        self.logger.GetLogger().info("Bot initialization completed")
        self.client = Client(
            self.config.GetValue(BotConfigTypes.SESSION_NAME),
            api_id=self.config.GetValue(BotConfigTypes.API_ID),
            api_hash=self.config.GetValue(BotConfigTypes.API_HASH),
            bot_token=self.config.GetValue(BotConfigTypes.BOT_TOKEN),
        )
        self.__SetupHandlers(self.handlers_config)
        self.logger.GetLogger().info("Async initialization completed")

    async def Run(self) -> None:
        """Start the bot client."""
        self.logger.GetLogger().info("Bot started!\n")
        async with self.client:
            await idle()

    def __SetupHandlers(self,
                        handlers_config: BotHandlersConfigType) -> None:
        """
        Setup message handlers for the bot.

        Args:
            handlers_config: Dictionary containing handler configurations
        """

        def create_handler(handler_type, handler_cfg):
            async def async_callback(client, message):
                return await handler_cfg["callback"](self, client, message)
            return handler_type(async_callback, handler_cfg["filters"])

        for curr_hnd_type, curr_hnd_cfg in handlers_config.items():
            for handler_cfg in curr_hnd_cfg:
                self.client.add_handler(create_handler(curr_hnd_type, handler_cfg))
        self.logger.GetLogger().info("Bot handlers set")

    async def DispatchCommand(self,
                              client: pyrogram.Client,
                              message: pyrogram.types.Message,
                              cmd_type: CommandTypes,
                              **kwargs: Any) -> None:
        """
        Dispatch a command to the command dispatcher.

        Args:
            client: Pyrogram client instance
            message: Message containing the command
            cmd_type: Type of command to dispatch
            **kwargs: Additional keyword arguments for the command
        """
        await self.cmd_dispatcher.Dispatch(client, message, cmd_type, **kwargs)

    async def HandleMessage(self,
                            client: pyrogram.Client,
                            message: pyrogram.types.Message,
                            msg_type: MessageTypes,
                            **kwargs: Any) -> None:
        """
        Handle a message by dispatching it to the message dispatcher.

        Args:
            client: Pyrogram client instance
            message: Message to handle
            msg_type: Type of message
            **kwargs: Additional keyword arguments for the message handler
        """
        await self.msg_dispatcher.Dispatch(client, message, msg_type, **kwargs)
