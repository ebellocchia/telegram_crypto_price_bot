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
from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from typing import Any
from telegram_crypto_price_bot.command_dispatcher import CommandDispatcher, CommandTypes
from telegram_crypto_price_bot.coin_info_tasks import CoinInfoTasks
from telegram_crypto_price_bot.config import ConfigTypes
from telegram_crypto_price_bot.config_loader import ConfigLoader
from telegram_crypto_price_bot.logger import Logger
from telegram_crypto_price_bot.translation_loader import TranslationLoader


#
# Classes
#

# Price bot class
class PriceBot:
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
        # Initialize coin info tasks
        self.coin_info_tasks = CoinInfoTasks(self.client,
                                             self.config,
                                             self.logger,
                                             self.translator)
        # Initialize helper classes
        self.cmd_dispatcher = CommandDispatcher(self.config, self.logger, self.translator)
        # Setup handlers
        self.__SetupHandlers()
        # Log
        self.logger.GetLogger().info("Bot initialization completed")

    # Run bot
    def Run(self) -> None:
        # Print
        self.logger.GetLogger().info("Telegram Price Bot started!\n")
        # Run client
        self.client.run()

    # Setup handlers
    def __SetupHandlers(self) -> None:
        # Start command
        self.client.add_handler(MessageHandler(
            lambda client, message: self.__DispatchCommand(client, message, CommandTypes.START_CMD),
            filters.private & filters.command(["start"])))
        # Help command
        self.client.add_handler(MessageHandler(
            lambda client, message: self.__DispatchCommand(client, message, CommandTypes.HELP_CMD),
            filters.command(["help"])))
        # Alive command
        self.client.add_handler(MessageHandler(
            lambda client, message: self.__DispatchCommand(client, message, CommandTypes.ALIVE_CMD),
            filters.command(["alive"])))
        # Set test mode command
        self.client.add_handler(MessageHandler(
            lambda client, message: self.__DispatchCommand(client, message, CommandTypes.SET_TEST_MODE_CMD),
            filters.command(["set_test_mode"])))
        # Check test mode command
        self.client.add_handler(MessageHandler(
            lambda client, message: self.__DispatchCommand(client, message, CommandTypes.IS_TEST_MODE_CMD),
            filters.command(["is_test_mode"])))
        # Get single price command
        self.client.add_handler(MessageHandler(
            lambda client, message: self.__DispatchCommand(client, message, CommandTypes.PRICE_GET_SINGLE_CMD),
            filters.command(["price_get_single"])))
        # Price task start command
        self.client.add_handler(MessageHandler(
            lambda client, message: self.__DispatchCommand(client,
                                                           message,
                                                           CommandTypes.PRICE_TASK_START_CMD,
                                                           coin_info_tasks=self.coin_info_tasks),
            filters.command(["price_task_start"])))
        # Price task start command
        self.client.add_handler(MessageHandler(
            lambda client, message: self.__DispatchCommand(client,
                                                           message,
                                                           CommandTypes.PRICE_TASK_STOP_CMD,
                                                           coin_info_tasks=self.coin_info_tasks),
            filters.command(["price_task_stop"])))
        # Price task pause command
        self.client.add_handler(MessageHandler(
            lambda client, message: self.__DispatchCommand(client,
                                                           message,
                                                           CommandTypes.PRICE_TASK_PAUSE_CMD,
                                                           coin_info_tasks=self.coin_info_tasks),
            filters.command(["price_task_pause"])))
        # Price task resume command
        self.client.add_handler(MessageHandler(
            lambda client, message: self.__DispatchCommand(client,
                                                           message,
                                                           CommandTypes.PRICE_TASK_RESUME_CMD,
                                                           coin_info_tasks=self.coin_info_tasks),
            filters.command(["price_task_resume"])))
        # Price task send in same message command
        self.client.add_handler(MessageHandler(
            lambda client, message: self.__DispatchCommand(client,
                                                           message,
                                                           CommandTypes.PRICE_TASK_SEND_IN_SAME_MSG_CMD,
                                                           coin_info_tasks=self.coin_info_tasks),
            filters.command(["price_task_send_in_same_msg"])))
        # Price task delete last message command
        self.client.add_handler(MessageHandler(
            lambda client, message: self.__DispatchCommand(client,
                                                           message,
                                                           CommandTypes.PRICE_TASK_DELETE_LAST_MSG_CMD,
                                                           coin_info_tasks=self.coin_info_tasks),
            filters.command(["price_task_delete_last_msg"])))
        # Price task info command
        self.client.add_handler(MessageHandler(
            lambda client, message: self.__DispatchCommand(client,
                                                           message,
                                                           CommandTypes.PRICE_TASK_INFO_CMD,
                                                           coin_info_tasks=self.coin_info_tasks),
            filters.command(["price_task_info"])))
        # Print
        self.logger.GetLogger().info("Bot handlers set")

    # Dispatch command
    def __DispatchCommand(self,
                          client: pyrogram.Client,
                          message: pyrogram.types.Message,
                          cmd_type: CommandTypes,
                          **kwargs: Any) -> None:
        self.cmd_dispatcher.Dispatch(client, message, cmd_type, **kwargs)
