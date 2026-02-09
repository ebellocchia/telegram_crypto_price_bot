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
from typing import Any, Optional

import pyrogram

from telegram_crypto_price_bot.coingecko.coingecko_price_api import CoinGeckoPriceApi
from telegram_crypto_price_bot.config.config_object import ConfigObject
from telegram_crypto_price_bot.logger.logger import Logger
from telegram_crypto_price_bot.message.message_deleter import MessageDeleter
from telegram_crypto_price_bot.message.message_sender import MessageSender


class InfoMessageSenderBase(ABC):
    """Abstract base class for information message senders."""

    last_sent_msg: Optional[pyrogram.types.Message]
    coingecko_api: CoinGeckoPriceApi
    message_deleter: MessageDeleter
    message_sender: MessageSender

    def __init__(self,
                 client: pyrogram.Client,
                 config: ConfigObject,
                 logger: Logger) -> None:
        """
        Initialize the info message sender base.

        Args:
            client: Pyrogram client instance.
            config: Configuration object.
            logger: Logger instance.
        """
        self.last_sent_msg = None
        self.coingecko_api = CoinGeckoPriceApi(config, logger)
        self.message_deleter = MessageDeleter(client, logger)
        self.message_sender = MessageSender(client, logger)

    async def SendMessage(self,
                          chat: pyrogram.types.Chat,
                          topic_id: int,
                          *args: Any,
                          **kwargs: Any) -> None:
        """
        Send message and store the last sent message.

        Args:
            chat: Telegram chat to send message to.
            topic_id: Telegram topic to send message to.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
        """
        self.last_sent_msg = await self._SendMessage(chat, topic_id, *args, **kwargs)

    async def DeleteLastSentMessage(self) -> None:
        """Delete the last sent message if it exists."""
        if self.last_sent_msg is not None:
            await self.message_deleter.DeleteMessage(self.last_sent_msg)

        self.last_sent_msg = None

    def _CoinGeckoPriceApi(self) -> CoinGeckoPriceApi:
        """
        Get the CoinGecko API instance.

        Returns:
            CoinGecko API instance.
        """
        return self.coingecko_api

    def _MessageSender(self) -> MessageSender:
        """
        Get the message sender instance.

        Returns:
            Message sender instance.
        """
        return self.message_sender

    @abstractmethod
    async def _SendMessage(self,
                           chat: pyrogram.types.Chat,
                           topic_id: int,
                           *args: Any,
                           **kwargs: Any) -> pyrogram.types.Message:
        """
        Send message implementation to be provided by subclasses.

        Args:
            chat: Telegram chat to send message to
            topic_id: Telegram topic to send message to
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments

        Returns:
            Sent message object
        """
