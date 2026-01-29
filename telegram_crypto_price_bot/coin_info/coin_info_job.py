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

from telegram_crypto_price_bot.config.config_object import ConfigObject
from telegram_crypto_price_bot.info_message_sender.coin_info_message_sender import CoinInfoMessageSender
from telegram_crypto_price_bot.logger.logger import Logger
from telegram_crypto_price_bot.misc.helpers import ChatHelper
from telegram_crypto_price_bot.translation.translation_loader import TranslationLoader


class CoinInfoJobData:
    """Data class for storing coin information job parameters."""

    chat: pyrogram.types.Chat
    period_hours: int
    start_hour: int
    coin_id: str
    coin_vs: str
    last_days: int
    running: bool

    def __init__(self,
                 chat: pyrogram.types.Chat,
                 period_hours: int,
                 start_hour: int,
                 coin_id: str,
                 coin_vs: str,
                 last_days: int) -> None:
        """Initialize coin info job data.

        Args:
            chat: Telegram chat where the job will run
            period_hours: Period in hours between job executions
            start_hour: Starting hour for the job
            coin_id: Cryptocurrency coin identifier
            coin_vs: Currency to compare against
            last_days: Number of days of historical data to display
        """
        self.chat = chat
        self.period_hours = period_hours
        self.start_hour = start_hour
        self.coin_id = coin_id
        self.coin_vs = coin_vs
        self.last_days = last_days
        self.running = True

    def Chat(self) -> pyrogram.types.Chat:
        """Get the chat associated with this job.

        Returns:
            The Telegram chat object
        """
        return self.chat

    def PeriodHours(self) -> int:
        """Get the period in hours between job executions.

        Returns:
            Period in hours
        """
        return self.period_hours

    def StartHour(self) -> int:
        """Get the starting hour for the job.

        Returns:
            Starting hour
        """
        return self.start_hour

    def CoinId(self) -> str:
        """Get the cryptocurrency coin identifier.

        Returns:
            Coin identifier
        """
        return self.coin_id

    def CoinVs(self) -> str:
        """Get the currency to compare against.

        Returns:
            Comparison currency
        """
        return self.coin_vs

    def LastDays(self) -> int:
        """Get the number of days of historical data.

        Returns:
            Number of days
        """
        return self.last_days

    def SetRunning(self, flag: bool) -> None:
        """Set the running status of the job.

        Args:
            flag: True if job is running, False otherwise
        """
        self.running = flag

    def IsRunning(self) -> bool:
        """Check if the job is currently running.

        Returns:
            True if running, False otherwise
        """
        return self.running


class CoinInfoJob:
    """Class for managing and executing coin information jobs."""

    data: CoinInfoJobData
    logger: Logger
    coin_info_msg_sender: CoinInfoMessageSender

    def __init__(self,
                 client: pyrogram.Client,
                 config: ConfigObject,
                 logger: Logger,
                 translator: TranslationLoader,
                 data: CoinInfoJobData) -> None:
        """Initialize coin info job.

        Args:
            client: Pyrogram client instance
            config: Configuration object
            logger: Logger instance
            translator: Translation loader
            data: Job data containing job parameters
        """
        self.data = data
        self.logger = logger
        self.coin_info_msg_sender = CoinInfoMessageSender(client, config, logger, translator)

    def Data(self) -> CoinInfoJobData:
        """Get the job data.

        Returns:
            Job data object
        """
        return self.data

    def SetRunning(self, flag: bool) -> None:
        """Set the running status of the job.

        Args:
            flag: True if job is running, False otherwise
        """
        self.data.SetRunning(flag)

    def DeleteLastSentMessage(self, flag: bool) -> None:
        """Set whether to delete the last sent message.

        Args:
            flag: True to delete last message, False otherwise
        """
        self.coin_info_msg_sender.DeleteLastSentMessage(flag)

    def SendInSameMessage(self, flag: bool) -> None:
        """Set whether to send updates in the same message.

        Args:
            flag: True to send in same message, False otherwise
        """
        self.coin_info_msg_sender.SendInSameMessage(flag)

    def DoJob(self,
              chat: pyrogram.types.Chat,
              coin_id: str,
              coin_vs: str,
              last_days: int) -> None:
        """Execute the job by sending coin information to the chat.

        Args:
            chat: Telegram chat to send the message to
            coin_id: Cryptocurrency coin identifier
            coin_vs: Currency to compare against
            last_days: Number of days of historical data to display
        """
        self.logger.GetLogger().info(f"Coin job started in chat {ChatHelper.GetTitleOrId(chat)}")
        self.coin_info_msg_sender.SendMessage(chat, coin_id, coin_vs, last_days)
