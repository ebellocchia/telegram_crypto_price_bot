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
from telegram_crypto_price_bot.chart_info_message_sender import ChartInfoMessageSender
from telegram_crypto_price_bot.chart_price_info_message_sender import ChartPriceInfoMessageSender
from telegram_crypto_price_bot.coingecko_price_api import CoinGeckoPriceApiError
from telegram_crypto_price_bot.config import ConfigTypes, Config
from telegram_crypto_price_bot.logger import Logger
from telegram_crypto_price_bot.message_sender import MessageSender
from telegram_crypto_price_bot.price_info_message_sender import PriceInfoMessageSender
from telegram_crypto_price_bot.translation_loader import TranslationLoader


#
# Classes
#

# Coin info message sender class
class CoinInfoMessageSender:

    config: Config
    logger: Logger
    translator: TranslationLoader
    delete_last_sent_msg: bool
    send_in_same_msg: bool
    chart_price_info_msg_sender: ChartPriceInfoMessageSender
    chart_info_msg_sender: ChartInfoMessageSender
    price_info_msg_sender: PriceInfoMessageSender
    msg_sender: MessageSender

    # Constructor
    def __init__(self,
                 client: pyrogram.Client,
                 config: Config,
                 logger: Logger,
                 translator: TranslationLoader) -> None:
        self.config = config
        self.logger = logger
        self.translator = translator
        self.delete_last_sent_msg = True
        self.send_in_same_msg = True
        self.chart_price_info_msg_sender = ChartPriceInfoMessageSender(client, config, logger, translator)
        self.chart_info_msg_sender = ChartInfoMessageSender(client, config, logger, translator)
        self.price_info_msg_sender = PriceInfoMessageSender(client, config, logger, translator)
        self.msg_sender = MessageSender(client, logger)

    # Set delete last sent message
    def DeleteLastSentMessage(self,
                              flag: bool) -> None:
        self.delete_last_sent_msg = flag

    # Set send in same message
    def SendInSameMessage(self,
                          flag: bool) -> None:
        self.send_in_same_msg = flag

    # Send message
    def SendMessage(self,
                    chat: pyrogram.types.Chat,
                    coin_id: str,
                    coin_vs: str,
                    last_days: int) -> None:
        if self.delete_last_sent_msg:
            self.chart_info_msg_sender.DeleteLastSentMessage()
            self.chart_price_info_msg_sender.DeleteLastSentMessage()
            self.price_info_msg_sender.DeleteLastSentMessage()

        try:
            # Chart and price information in the same message
            if self.send_in_same_msg and self.config.GetValue(ConfigTypes.CHART_DISPLAY):
                self.chart_price_info_msg_sender.SendMessage(chat, coin_id, coin_vs, last_days)
            # Chart and price information in the different messages
            else:
                self.price_info_msg_sender.SendMessage(chat, coin_id, coin_vs)

                if self.config.GetValue(ConfigTypes.CHART_DISPLAY):
                    self.chart_info_msg_sender.SendMessage(chat, coin_id, coin_vs, last_days)
        except CoinGeckoPriceApiError:
            self.logger.GetLogger().exception(
                f"Coingecko API error when retrieving data for coin {coin_id}/{coin_vs}"
            )
            self.msg_sender.SendMessage(
                chat,
                self.translator.GetSentence("API_ERR_MSG",
                                            coin_id=coin_id,
                                            coin_vs=coin_vs)
            )
