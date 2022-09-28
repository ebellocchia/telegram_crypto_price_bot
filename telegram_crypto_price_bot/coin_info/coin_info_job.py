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

from telegram_crypto_price_bot.config.config_object import ConfigObject
from telegram_crypto_price_bot.info_message_sender.coin_info_message_sender import CoinInfoMessageSender
from telegram_crypto_price_bot.logger.logger import Logger
from telegram_crypto_price_bot.misc.helpers import ChatHelper
from telegram_crypto_price_bot.translation.translation_loader import TranslationLoader


#
# Classes
#

# Coin info job class
class CoinInfoJobData:

    chat: pyrogram.types.Chat
    period_hours: int
    start_hour: int
    coin_id: str
    coin_vs: str
    last_days: int
    running: bool

    # Constructor
    def __init__(self,
                 chat: pyrogram.types.Chat,
                 period_hours: int,
                 start_hour: int,
                 coin_id: str,
                 coin_vs: str,
                 last_days: int) -> None:
        self.chat = chat
        self.period_hours = period_hours
        self.start_hour = start_hour
        self.coin_id = coin_id
        self.coin_vs = coin_vs
        self.last_days = last_days
        self.running = True

    # Get chat
    def Chat(self) -> pyrogram.types.Chat:
        return self.chat

    # Get period hours
    def PeriodHours(self) -> int:
        return self.period_hours

    # Get start hour
    def StartHour(self) -> int:
        return self.start_hour

    # Get coin ID
    def CoinId(self) -> str:
        return self.coin_id

    # Get coin VS
    def CoinVs(self) -> str:
        return self.coin_vs

    # Get last days
    def LastDays(self) -> int:
        return self.last_days

    # Set if running
    def SetRunning(self,
                   flag: bool) -> None:
        self.running = flag

    # Get if running
    def IsRunning(self) -> bool:
        return self.running


# Coin info job class
class CoinInfoJob:

    data: CoinInfoJobData
    logger: Logger
    coin_info_msg_sender: CoinInfoMessageSender

    # Constructor
    def __init__(self,
                 client: pyrogram.Client,
                 config: ConfigObject,
                 logger: Logger,
                 translator: TranslationLoader,
                 data: CoinInfoJobData) -> None:
        self.data = data
        self.logger = logger
        self.coin_info_msg_sender = CoinInfoMessageSender(client, config, logger, translator)

    # Get data
    def Data(self) -> CoinInfoJobData:
        return self.data

    # Set if running
    def SetRunning(self,
                   flag: bool) -> None:
        self.data.SetRunning(flag)

    # Set delete last sent message
    def DeleteLastSentMessage(self,
                              flag: bool) -> None:
        self.coin_info_msg_sender.DeleteLastSentMessage(flag)

    # Set send in same message
    def SendInSameMessage(self,
                          flag: bool) -> None:
        self.coin_info_msg_sender.SendInSameMessage(flag)

    # Do job
    def DoJob(self,
              chat: pyrogram.types.Chat,
              coin_id: str,
              coin_vs: str,
              last_days: int) -> None:
        self.logger.GetLogger().info(f"Coin job started in chat {ChatHelper.GetTitleOrId(chat)}")
        self.coin_info_msg_sender.SendMessage(chat, coin_id, coin_vs, last_days)
