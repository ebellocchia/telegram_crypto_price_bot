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
from typing import Any, Dict, List
import pyrogram
from pyrogram import Client
from telegram_crypto_price_bot.bot.bot_config import BotConfigTypes, BotConfig
from telegram_crypto_price_bot.config.configurable_object import ConfigurableObject
from telegram_crypto_price_bot.command.command_dispatcher import CommandTypes, CommandDispatcher
from telegram_crypto_price_bot.config.config_loader import ConfigCfgType, ConfigLoader
from telegram_crypto_price_bot.logger.logger import Logger
from telegram_crypto_price_bot.message.message_dispatcher import MessageTypes, MessageDispatcher
from telegram_crypto_price_bot.translation.translation_loader import TranslationLoader


#
# Types
#

# Handlers configuration type
HandlersCfgType = Dict[Any, List[Dict[str, Any]]]


#
# Classes
#


# Bot base class
class BotBase:

    config: ConfigurableObject
    logger: Logger
    translator: TranslationLoader
    client: pyrogram.Client
    cmd_dispatcher: CommandDispatcher
    msg_dispatcher: MessageDispatcher

    # Constructor
    def __init__(self,
                 config_file: str,
                 config_cfg: ConfigCfgType,
                 handlers_cfg: HandlersCfgType) -> None:
        # Load configuration
        config_ldr = ConfigLoader(BotConfig(), config_cfg)
        config_ldr.Load(config_file)
        self.config = config_ldr.GetLoadedObject()
        # Initialize logger
        self.logger = Logger(self.config)
        # Initialize translations
        self.translator = TranslationLoader(self.logger)
        self.translator.Load(self.config.GetValue(BotConfigTypes.APP_LANG_FILE))
        # Initialize client
        self.client = Client(self.config.GetValue(BotConfigTypes.SESSION_NAME),
                             config_file=config_file)
        # Initialize helper classes
        self.cmd_dispatcher = CommandDispatcher(self.config, self.logger, self.translator)
        self.msg_dispatcher = MessageDispatcher(self.config, self.logger, self.translator)
        # Setup handlers
        self._SetupHandlers(handlers_cfg)
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
                       handlers_cfg: HandlersCfgType) -> None:
        # Add all configured handlers
        for curr_hnd_type, curr_hnd_cfg in handlers_cfg.items():
            for handler_cfg in curr_hnd_cfg:
                self.client.add_handler(
                    # Little "hack" to keep a local scope for current configuration
                    (
                        lambda curr_type=curr_hnd_type, curr_cfg=handler_cfg:
                            curr_type(lambda client, message: curr_cfg["callback"](self, client, message),
                                      curr_cfg["filters"])
                    )()
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
