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
from typing import Any

import pyrogram

from telegram_crypto_price_bot.config.config_object import ConfigObject
from telegram_crypto_price_bot.logger.logger import Logger
from telegram_crypto_price_bot.message.message_sender import MessageSender
from telegram_crypto_price_bot.translation.translation_loader import TranslationLoader


@unique
class MessageTypes(Enum):
    """Enumeration of message types for bot events."""

    GROUP_CHAT_CREATED = auto()
    LEFT_CHAT_MEMBER = auto()
    NEW_CHAT_MEMBERS = auto()


class MessageDispatcher:
    """Dispatcher for routing message types to their respective handlers."""

    config: ConfigObject
    logger: Logger
    translator: TranslationLoader

    def __init__(self,
                 config: ConfigObject,
                 logger: Logger,
                 translator: TranslationLoader) -> None:
        """Initialize the message dispatcher.

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
                 msg_type: MessageTypes,
                 **kwargs: Any) -> None:
        """Dispatch a message to its corresponding handler.

        Args:
            client: Pyrogram client instance
            message: Telegram message to dispatch
            msg_type: Type of message to dispatch
            **kwargs: Additional keyword arguments

        Raises:
            TypeError: If msg_type is not a MessageTypes enumeration
        """
        if not isinstance(msg_type, MessageTypes):
            raise TypeError("Message type is not an enumerative of MessageTypes")

        self.logger.GetLogger().info(f"Dispatching message type: {msg_type}")

        if msg_type == MessageTypes.GROUP_CHAT_CREATED:
            self.__OnCreatedChat(client, message, **kwargs)
        elif msg_type == MessageTypes.LEFT_CHAT_MEMBER:
            self.__OnLeftMember(client, message, **kwargs)
        elif msg_type == MessageTypes.NEW_CHAT_MEMBERS:
            self.__OnJoinedMember(client, message, **kwargs)

    def __OnCreatedChat(self,
                        client,
                        message: pyrogram.types.Message,
                        **kwargs: Any) -> None:
        """Handle new chat creation event.

        Args:
            client: Pyrogram client instance
            message: Message containing chat creation info
            **kwargs: Additional keyword arguments
        """
        if message.chat is None:
            return

        MessageSender(client, self.logger).SendMessage(
            message.chat,
            self.translator.GetSentence("BOT_WELCOME_MSG")
        )

    def __OnLeftMember(self,
                       client,
                       message: pyrogram.types.Message,
                       **kwargs: Any) -> None:
        """Handle member leaving chat event.

        Args:
            client: Pyrogram client instance
            message: Message containing member left info
            **kwargs: Additional keyword arguments
        """
        if message.left_chat_member is not None and message.left_chat_member.is_self:
            kwargs["coin_info_scheduler"].ChatLeft(message.chat)

    def __OnJoinedMember(self,
                         client,
                         message: pyrogram.types.Message,
                         **kwargs: Any) -> None:
        """Handle member joining chat event.

        Args:
            client: Pyrogram client instance
            message: Message containing new members info
            **kwargs: Additional keyword arguments
        """
        if message.new_chat_members is None or message.chat is None:
            return

        for member in message.new_chat_members:
            if member.is_self:
                MessageSender(client, self.logger).SendMessage(
                    message.chat,
                    self.translator.GetSentence("BOT_WELCOME_MSG")
                )
                break
