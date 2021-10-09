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
from typing import Any
from telegram_crypto_price_bot.config import Config
from telegram_crypto_price_bot.logger import Logger
from telegram_crypto_price_bot.info_message_sender_base import InfoMessageSenderBase
from telegram_crypto_price_bot.price_info_builder import PriceInfoBuilder
from telegram_crypto_price_bot.translation_loader import TranslationLoader


#
# Classes
#

# Price info message sender class
class PriceInfoMessageSender(InfoMessageSenderBase):

    price_info_builder: PriceInfoBuilder

    # Constructor
    def __init__(self,
                 client: pyrogram.Client,
                 config: Config,
                 logger: Logger,
                 translator: TranslationLoader) -> None:
        super().__init__(client, config, logger)
        self.price_info_builder = PriceInfoBuilder(config, translator)

    # Send message
    def _SendMessage(self,
                     chat: pyrogram.types.Chat,
                     *args: Any,
                     **kwargs: Any) -> pyrogram.types.Message:
        # Get price information
        price_info = self._CoinGeckoPriceApi().GetPriceInfo(args[0], args[1])
        # Build price information string
        price_info_str = self.price_info_builder.Build(price_info)

        return self._MessageSender().SendMessage(chat, price_info_str)[0]
