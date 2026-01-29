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

import pyrogram

from telegram_crypto_price_bot.bot.bot_config_types import BotConfigTypes
from telegram_crypto_price_bot.coingecko.coingecko_price_api import CoinGeckoPriceApiError
from telegram_crypto_price_bot.config.config_object import ConfigObject
from telegram_crypto_price_bot.info_message_sender.chart_info_message_sender import ChartInfoMessageSender
from telegram_crypto_price_bot.info_message_sender.chart_price_info_message_sender import ChartPriceInfoMessageSender
from telegram_crypto_price_bot.info_message_sender.price_info_message_sender import PriceInfoMessageSender
from telegram_crypto_price_bot.logger.logger import Logger
from telegram_crypto_price_bot.message.message_sender import MessageSender
from telegram_crypto_price_bot.translation.translation_loader import TranslationLoader


class CoinInfoMessageSender:
    """Message sender for cryptocurrency information combining chart and price data."""

    config: ConfigObject
    logger: Logger
    translator: TranslationLoader
    delete_last_sent_msg: bool
    send_in_same_msg: bool
    chart_price_info_msg_sender: ChartPriceInfoMessageSender
    chart_info_msg_sender: ChartInfoMessageSender
    price_info_msg_sender: PriceInfoMessageSender
    msg_sender: MessageSender

    def __init__(self,
                 client: pyrogram.Client,
                 config: ConfigObject,
                 logger: Logger,
                 translator: TranslationLoader) -> None:
        """Initialize the coin info message sender.

        Args:
            client: Pyrogram client instance
            config: Configuration object
            logger: Logger instance
            translator: Translation loader
        """
        self.config = config
        self.logger = logger
        self.translator = translator
        self.delete_last_sent_msg = True
        self.send_in_same_msg = True
        self.chart_price_info_msg_sender = ChartPriceInfoMessageSender(client, config, logger, translator)
        self.chart_info_msg_sender = ChartInfoMessageSender(client, config, logger, translator)
        self.price_info_msg_sender = PriceInfoMessageSender(client, config, logger, translator)
        self.msg_sender = MessageSender(client, logger)

    def DeleteLastSentMessage(self,
                              flag: bool) -> None:
        """Set whether to delete the last sent message.

        Args:
            flag: True to delete last message, False otherwise
        """
        self.delete_last_sent_msg = flag

    def SendInSameMessage(self,
                          flag: bool) -> None:
        """Set whether to send chart and price in the same message.

        Args:
            flag: True to send in same message, False otherwise
        """
        self.send_in_same_msg = flag

    def SendMessage(self,
                    chat: pyrogram.types.Chat,
                    topic_id: int,
                    coin_id: str,
                    coin_vs: str,
                    last_days: int) -> None:
        """Send cryptocurrency information message to chat.

        Args:
            chat: Telegram chat to send message to
            topic_id: Telegram topic to send message to
            coin_id: Cryptocurrency coin identifier
            coin_vs: Currency to compare against
            last_days: Number of days of historical data
        """
        if self.delete_last_sent_msg:
            self.chart_info_msg_sender.DeleteLastSentMessage()
            self.chart_price_info_msg_sender.DeleteLastSentMessage()
            self.price_info_msg_sender.DeleteLastSentMessage()

        try:
            if self.send_in_same_msg and self.config.GetValue(BotConfigTypes.CHART_DISPLAY):
                self.chart_price_info_msg_sender.SendMessage(chat, topic_id, coin_id, coin_vs, last_days)
            else:
                self.price_info_msg_sender.SendMessage(chat, topic_id, coin_id, coin_vs)

                if self.config.GetValue(BotConfigTypes.CHART_DISPLAY):
                    self.chart_info_msg_sender.SendMessage(chat, topic_id, coin_id, coin_vs, last_days)
        except CoinGeckoPriceApiError:
            self.logger.GetLogger().exception(
                f"Coingecko API error when retrieving data for coin {coin_id}/{coin_vs}"
            )
            self.msg_sender.SendMessage(
                chat,
                topic_id,
                self.translator.GetSentence("API_ERR_MSG",
                                            coin_id=coin_id,
                                            coin_vs=coin_vs)
            )
