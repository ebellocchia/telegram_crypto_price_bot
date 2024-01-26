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
from typing import Any

import pyrogram

from telegram_crypto_price_bot.chart_info.chart_info_file_saver import ChartInfoTmpFileSaver
from telegram_crypto_price_bot.config.config_object import ConfigObject
from telegram_crypto_price_bot.info_message_sender.info_message_sender_base import InfoMessageSenderBase
from telegram_crypto_price_bot.logger.logger import Logger
from telegram_crypto_price_bot.price_info.price_info_builder import PriceInfoBuilder
from telegram_crypto_price_bot.translation.translation_loader import TranslationLoader


#
# Classes
#

# Chart price info message sender class (chart and price in the same message)
class ChartPriceInfoMessageSender(InfoMessageSenderBase):

    config: ConfigObject
    logger: Logger
    translator: TranslationLoader
    price_info_builder: PriceInfoBuilder

    # Constructor
    def __init__(self,
                 client: pyrogram.Client,
                 config: ConfigObject,
                 logger: Logger,
                 translator: TranslationLoader) -> None:
        super().__init__(client, config, logger)
        self.config = config
        self.logger = logger
        self.translator = translator
        self.price_info_builder = PriceInfoBuilder(config, translator)

    # Send message
    def _SendMessage(self,
                     chat: pyrogram.types.Chat,
                     *args: Any,
                     **kwargs: Any) -> pyrogram.types.Message:
        # Get chart and price information
        chart_info = self._CoinGeckoPriceApi().GetChartInfo(args[0], args[1], args[2])
        price_info = self._CoinGeckoPriceApi().GetPriceInfo(args[0], args[1])

        # Build price information string
        price_info_str = self.price_info_builder.Build(price_info)
        # Save chart image
        chart_info_saver = ChartInfoTmpFileSaver(self.config, self.logger, self.translator)
        chart_info_saver.SaveToTmpFile(chart_info)
        # Get temporary file name
        tmp_file_name = chart_info_saver.TmpFileName()
        if tmp_file_name is None:
            raise RuntimeError("Unable to save chart to file")

        # Send chart image with price information as caption
        return self._MessageSender().SendPhoto(chat,
                                               tmp_file_name,
                                               caption=price_info_str,
                                               **kwargs)
