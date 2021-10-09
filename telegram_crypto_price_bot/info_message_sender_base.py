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
from typing import Any, Optional
from telegram_crypto_price_bot.coingecko_price_api import CoinGeckoPriceApi
from telegram_crypto_price_bot.config import Config
from telegram_crypto_price_bot.logger import Logger
from telegram_crypto_price_bot.message_deleter import MessageDeleter
from telegram_crypto_price_bot.message_sender import MessageSender


#
# Classes
#

# Info message sender base class
class InfoMessageSenderBase(ABC):

    last_sent_msg: Optional[pyrogram.types.Message]
    coingecko_api: CoinGeckoPriceApi
    message_deleter: MessageDeleter
    message_sender: MessageSender

    # Constructor
    def __init__(self,
                 client: pyrogram.Client,
                 config: Config,
                 logger: Logger) -> None:
        self.last_sent_msg = None
        self.coingecko_api = CoinGeckoPriceApi()
        self.message_deleter = MessageDeleter(client, logger)
        self.message_sender = MessageSender(client, config, logger)

    # Send message
    def SendMessage(self,
                    chat: pyrogram.types.Chat,
                    *args: Any,
                    **kwargs: Any) -> None:
        self.last_sent_msg = self._SendMessage(chat, *args, **kwargs)

    # Delete last sent message
    def DeleteLastSentMessage(self) -> None:
        if self.last_sent_msg is not None:
            self.message_deleter.DeleteMessage(self.last_sent_msg)

        self.last_sent_msg = None

    # Get CoinGecko API
    def _CoinGeckoPriceApi(self) -> CoinGeckoPriceApi:
        return self.coingecko_api

    # Get message sender
    def _MessageSender(self) -> MessageSender:
        return self.message_sender

    # Send message (to be implemented by children classes)
    @abstractmethod
    def _SendMessage(self,
                     chat: pyrogram.types.Chat,
                     *args: Any,
                     **kwargs: Any) -> pyrogram.types.Message:
        pass
