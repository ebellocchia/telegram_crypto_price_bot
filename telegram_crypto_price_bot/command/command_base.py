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
from abc import ABC, abstractmethod
from typing import Any
import pyrogram
from pyrogram.errors import RPCError
from telegram_crypto_price_bot.command.command_data import CommandData
from telegram_crypto_price_bot.config.configurable_object import ConfigurableObject
from telegram_crypto_price_bot.logger.logger import Logger
from telegram_crypto_price_bot.message.message_sender import MessageSender
from telegram_crypto_price_bot.misc.chat_members import ChatMembersGetter
from telegram_crypto_price_bot.misc.helpers import ChatHelper, UserHelper
from telegram_crypto_price_bot.translation.translation_loader import TranslationLoader


#
# Classes
#

#
# Generic command base class
#
class CommandBase(ABC):

    client: pyrogram.Client
    config: ConfigurableObject
    logger: Logger
    translator: TranslationLoader
    message: pyrogram.types.Message
    cmd_data: CommandData
    message_sender: MessageSender

    # Constructor
    def __init__(self,
                 client: pyrogram.Client,
                 config: ConfigurableObject,
                 logger: Logger,
                 translator: TranslationLoader) -> None:
        self.client = client
        self.config = config
        self.logger = logger
        self.translator = translator
        # Helper classes
        self.message_sender = MessageSender(client, logger)

    # Execute command
    def Execute(self,
                message: pyrogram.types.Message,
                **kwargs: Any) -> None:
        self.message = message
        self.cmd_data = CommandData(message)

        # Log command
        self.__LogCommand()

        # Check if user is authorized
        if self._IsUserAuthorized():
            # Try to execute command
            try:
                self._ExecuteCommand(**kwargs)
            except RPCError:
                self._SendMessage(self.translator.GetSentence("GENERIC_ERR_MSG"))
                self.logger.GetLogger().exception(
                    f"An error occurred while executing command {self.cmd_data.Name()}"
                )
        else:
            if self._IsPrivateChat():
                self._SendMessage(self.translator.GetSentence("AUTH_ONLY_ERR_MSG"))

            self.logger.GetLogger().warning(
                f"User {UserHelper.GetNameOrId(self.cmd_data.User())} tried to execute the command but it's not authorized"
            )

    # Send message
    def _SendMessage(self,
                     msg: str) -> None:
        self.message_sender.SendMessage(self.cmd_data.Chat(), msg)

    # Get if user is authorized
    def _IsUserAuthorized(self) -> bool:
        if ChatHelper.IsPrivateChat(self.cmd_data.Chat(), self.cmd_data.User()):
            return True

        admin_members = ChatMembersGetter(self.client).GetAdmins(self.cmd_data.Chat())
        return any((self.cmd_data.User().id == member.user.id for member in admin_members))

    # Get if chat is private
    def _IsPrivateChat(self) -> bool:
        return ChatHelper.IsPrivateChat(self.cmd_data.Chat(), self.cmd_data.User())

    # Log command
    def __LogCommand(self) -> None:
        self.logger.GetLogger().info(f"Command: {self.cmd_data.Name()}")
        self.logger.GetLogger().info(f"Executed by user: {UserHelper.GetNameOrId(self.cmd_data.User())}")
        self.logger.GetLogger().debug(f"Received message: {self.message}")

    # Execute command - Abstract method
    @abstractmethod
    def _ExecuteCommand(self,
                        **kwargs: Any) -> None:
        pass
