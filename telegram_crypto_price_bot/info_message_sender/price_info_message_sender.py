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

from telegram_crypto_price_bot.config.config_object import ConfigObject
from telegram_crypto_price_bot.info_message_sender.info_message_sender_base import InfoMessageSenderBase
from telegram_crypto_price_bot.logger.logger import Logger
from telegram_crypto_price_bot.price_info.price_info_builder import PriceInfoBuilder
from telegram_crypto_price_bot.translation.translation_loader import TranslationLoader


class PriceInfoMessageSender(InfoMessageSenderBase):
    """Message sender for price information in a single message."""

    price_info_builder: PriceInfoBuilder

    def __init__(self,
                 client: pyrogram.Client,
                 config: ConfigObject,
                 logger: Logger,
                 translator: TranslationLoader) -> None:
        """Initialize the price info message sender.

        Args:
            client: Pyrogram client instance
            config: Configuration object
            logger: Logger instance
            translator: Translation loader
        """
        super().__init__(client, config, logger)
        self.price_info_builder = PriceInfoBuilder(config, translator)

    async def _SendMessage(self,
                           chat: pyrogram.types.Chat,
                           topic_id: int,
                           *args: Any,
                           **kwargs: Any) -> pyrogram.types.Message:
        """Send price information message.

        Args:
            chat: Telegram chat to send message to
            topic_id: Telegram topic to send message to
            *args: Arguments containing coin_id, coin_vs
            **kwargs: Additional keyword arguments

        Returns:
            Sent message object
        """
        price_info = self._CoinGeckoPriceApi().GetPriceInfo(args[0], args[1])
        price_info_str = self.price_info_builder.Build(price_info)

        return (await self._MessageSender().SendMessage(chat, topic_id, price_info_str))[0]
