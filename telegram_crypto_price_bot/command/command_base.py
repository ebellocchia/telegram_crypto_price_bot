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

from abc import ABC, abstractmethod
from typing import Any

import pyrogram
from pyrogram.errors import RPCError

from telegram_crypto_price_bot.command.command_data import CommandData
from telegram_crypto_price_bot.config.config_object import ConfigObject
from telegram_crypto_price_bot.logger.logger import Logger
from telegram_crypto_price_bot.message.message_sender import MessageSender
from telegram_crypto_price_bot.misc.chat_members import ChatMembersGetter
from telegram_crypto_price_bot.misc.helpers import ChatHelper, UserHelper
from telegram_crypto_price_bot.translation.translation_loader import TranslationLoader


class CommandBase(ABC):
    """Abstract base class for implementing bot commands."""

    client: pyrogram.Client
    config: ConfigObject
    logger: Logger
    translator: TranslationLoader
    message: pyrogram.types.Message
    cmd_data: CommandData
    message_sender: MessageSender

    def __init__(self,
                 client: pyrogram.Client,
                 config: ConfigObject,
                 logger: Logger,
                 translator: TranslationLoader) -> None:
        """Initialize the command base.

        Args:
            client: Pyrogram client instance
            config: Configuration object
            logger: Logger instance
            translator: Translation loader
        """
        self.client = client
        self.config = config
        self.logger = logger
        self.translator = translator
        self.message_sender = MessageSender(client, logger)

    def Execute(self,
                message: pyrogram.types.Message,
                **kwargs: Any) -> None:
        """Execute the command with authorization and error handling.

        Args:
            message: Telegram message containing the command
            **kwargs: Additional keyword arguments for the command
        """
        self.message = message
        self.cmd_data = CommandData(message)

        self.__LogCommand()

        if self._IsUserAnonymous() and not self._IsChannel():
            self.logger.GetLogger().warning("An anonymous user tried to execute the command, exiting")
            return

        if not self._IsUserAuthorized():
            if self._IsPrivateChat():
                self._SendMessage(self.translator.GetSentence("AUTH_ONLY_ERR_MSG"))

            self.logger.GetLogger().warning(
                f"User {UserHelper.GetNameOrId(self.cmd_data.User())} tried to execute the command but it's not authorized"
            )
            return

        try:
            self._ExecuteCommand(**kwargs)
        except RPCError:
            self._SendMessage(self.translator.GetSentence("GENERIC_ERR_MSG"))
            self.logger.GetLogger().exception(f"An error occurred while executing command {self.cmd_data.Name()}")

    def _SendMessage(self,
                     msg: str) -> None:
        """Send a message to the chat or user.

        Args:
            msg: Message text to send
        """
        self.message_sender.SendMessage(self.cmd_data.Chat(), self.message.message_thread_id, msg)

    def _IsChannel(self) -> bool:
        """Check if the chat is a channel.

        Returns:
            True if channel, False otherwise
        """
        return ChatHelper.IsChannel(self.cmd_data.Chat())

    def _IsUserAnonymous(self) -> bool:
        """Check if the user is anonymous.

        Returns:
            True if anonymous, False otherwise
        """
        return self.cmd_data.User() is None

    def _IsUserAuthorized(self) -> bool:
        """Check if the user is authorized to execute the command.

        Returns:
            True if authorized, False otherwise
        """
        if self._IsChannel():
            return True

        cmd_user = self.cmd_data.User()
        if cmd_user is None:
            return False
        if ChatHelper.IsPrivateChat(self.cmd_data.Chat(), cmd_user):
            return True
        admin_members = ChatMembersGetter(self.client).GetAdmins(self.cmd_data.Chat())
        return any(cmd_user.id == member.user.id for member in admin_members if member.user is not None)

    def _IsPrivateChat(self) -> bool:
        """Check if the chat is a private chat.

        Returns:
            True if private chat, False otherwise
        """
        cmd_user = self.cmd_data.User()
        if cmd_user is None:
            return False
        return ChatHelper.IsPrivateChat(self.cmd_data.Chat(), cmd_user)

    def __LogCommand(self) -> None:
        """Log command execution details."""
        self.logger.GetLogger().info(f"Command: {self.cmd_data.Name()}")
        self.logger.GetLogger().info(f"Executed by user: {UserHelper.GetNameOrId(self.cmd_data.User())}")
        self.logger.GetLogger().debug(f"Received message: {self.message}")

    @abstractmethod
    def _ExecuteCommand(self, **kwargs: Any) -> None:
        """Execute the command implementation.

        Args:
            **kwargs: Additional keyword arguments for the command
        """
        pass
