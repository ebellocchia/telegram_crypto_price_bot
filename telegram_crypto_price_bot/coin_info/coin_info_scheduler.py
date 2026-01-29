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

from typing import Dict

import pyrogram
from apscheduler.schedulers.background import BackgroundScheduler

from telegram_crypto_price_bot.bot.bot_config_types import BotConfigTypes
from telegram_crypto_price_bot.coin_info.coin_info_job import CoinInfoJob, CoinInfoJobData
from telegram_crypto_price_bot.config.config_object import ConfigObject
from telegram_crypto_price_bot.logger.logger import Logger
from telegram_crypto_price_bot.misc.helpers import ChatHelper
from telegram_crypto_price_bot.translation.translation_loader import TranslationLoader
from telegram_crypto_price_bot.utils.wrapped_list import WrappedList


class CoinInfoJobAlreadyExistentError(Exception):
    """Exception raised when attempting to create a job that already exists."""

    pass


class CoinInfoJobNotExistentError(Exception):
    """Exception raised when attempting to access a non-existent job."""

    pass


class CoinInfoJobInvalidPeriodError(Exception):
    """Exception raised when job period is invalid."""

    pass


class CoinInfoJobInvalidStartError(Exception):
    """Exception raised when job start hour is invalid."""

    pass


class CoinInfoJobMaxNumError(Exception):
    """Exception raised when maximum number of jobs is reached."""

    pass


class CoinInfoSchedulerConst:
    """Constants for coin info scheduler configuration."""

    MIN_START_HOUR: int = 0
    MAX_START_HOUR: int = 23
    MIN_PERIOD_HOURS: int = 1
    MAX_PERIOD_HOURS: int = 24


class CoinInfoJobsList(WrappedList):
    """List class for managing coin info jobs with string representation."""

    translator: TranslationLoader

    def __init__(self, translator: TranslationLoader) -> None:
        """Initialize the jobs list.

        Args:
            translator: Translation loader for formatting job information
        """
        super().__init__()
        self.translator = translator

    def ToString(self) -> str:
        """Convert the jobs list to a formatted string.

        Returns:
            Formatted string with all job information
        """
        return "\n".join(
            [
                self.translator.GetSentence(
                    "SINGLE_TASK_INFO_MSG",
                    coin_id=job_data.CoinId(),
                    coin_vs=job_data.CoinVs(),
                    period=job_data.PeriodHours(),
                    start=job_data.StartHour(),
                    last_days=job_data.LastDays(),
                    state=(
                        self.translator.GetSentence("TASK_RUNNING_MSG")
                        if job_data.IsRunning()
                        else self.translator.GetSentence("TASK_PAUSED_MSG")
                    ),
                )
                for job_data in self.list_elements
            ]
        )

    def __str__(self) -> str:
        """Convert the jobs list to a string.

        Returns:
            Formatted string with all job information
        """
        return self.ToString()


class CoinInfoScheduler:
    """Scheduler for managing scheduled coin information jobs."""

    client: pyrogram.Client
    config: ConfigObject
    logger: Logger
    translator: TranslationLoader
    jobs: Dict[int, Dict[str, CoinInfoJob]]
    scheduler: BackgroundScheduler

    def __init__(self,
                 client: pyrogram.Client,
                 config: ConfigObject,
                 logger: Logger,
                 translator: TranslationLoader) -> None:
        """Initialize the coin info scheduler.

        Args:
            client: Pyrogram client instance
            config: Configuration object
            logger: Logger instance
            translator: Translation loader
        """
        self.client = client
        self.config = config
        self.logger = logger
        self.translator = translator
        self.jobs = {}
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()

    def GetJobsInChat(self, chat: pyrogram.types.Chat) -> CoinInfoJobsList:
        """Get the list of active jobs in a chat.

        Args:
            chat: Telegram chat to get jobs for

        Returns:
            List of active jobs in the chat
        """
        jobs_list = CoinInfoJobsList(self.translator)
        jobs_list.AddMultiple([job.Data() for (_, job) in self.jobs[chat.id].items()] if chat.id in self.jobs else [])

        return jobs_list

    def IsActiveInChat(self,
                       chat: pyrogram.types.Chat,
                       coin_id: str,
                       coin_vs: str) -> bool:
        """Check if a job is active in a chat.

        Args:
            chat: Telegram chat to check
            coin_id: Cryptocurrency coin identifier
            coin_vs: Currency to compare against

        Returns:
            True if job is active, False otherwise
        """
        job_id = self.__GetJobId(chat, coin_id, coin_vs)
        return chat.id in self.jobs and job_id in self.jobs[chat.id] and self.scheduler.get_job(job_id) is not None

    def Start(self,
              chat: pyrogram.types.Chat,
              period_hours: int,
              start_hour: int,
              coin_id: str,
              coin_vs: str,
              last_days: int) -> None:
        """Start a new scheduled job.

        Args:
            chat: Telegram chat where the job will run
            period_hours: Period in hours between executions
            start_hour: Starting hour for the job
            coin_id: Cryptocurrency coin identifier
            coin_vs: Currency to compare against
            last_days: Number of days of historical data

        Raises:
            CoinInfoJobAlreadyExistentError: If job already exists
            CoinInfoJobInvalidPeriodError: If period is invalid
            CoinInfoJobInvalidStartError: If start hour is invalid
            CoinInfoJobMaxNumError: If maximum number of jobs reached
        """
        job_id = self.__GetJobId(chat, coin_id, coin_vs)

        if self.IsActiveInChat(chat, coin_id, coin_vs):
            self.logger.GetLogger().error(f'Job "{job_id}" already active in chat {ChatHelper.GetTitleOrId(chat)}, cannot start it')
            raise CoinInfoJobAlreadyExistentError()

        if period_hours < CoinInfoSchedulerConst.MIN_PERIOD_HOURS or period_hours > CoinInfoSchedulerConst.MAX_PERIOD_HOURS:
            self.logger.GetLogger().error(f'Invalid period {period_hours} for job "{job_id}", cannot start it')
            raise CoinInfoJobInvalidPeriodError()

        if start_hour < CoinInfoSchedulerConst.MIN_START_HOUR or start_hour > CoinInfoSchedulerConst.MAX_START_HOUR:
            self.logger.GetLogger().error(f'Invalid start hour {start_hour} for job "{job_id}", cannot start it')
            raise CoinInfoJobInvalidStartError()

        tot_job_cnt = self.__GetTotalJobCount()
        if tot_job_cnt >= self.config.GetValue(BotConfigTypes.TASKS_MAX_NUM):
            self.logger.GetLogger().error("Maximum number of jobs reached, cannot start a new one")
            raise CoinInfoJobMaxNumError()

        self.__CreateJob(job_id, chat, period_hours, start_hour, coin_id, coin_vs, last_days)
        self.__AddJob(job_id, chat, period_hours, start_hour, coin_id, coin_vs, last_days)

    def Stop(self,
             chat: pyrogram.types.Chat,
             coin_id: str,
             coin_vs: str) -> None:
        """Stop a scheduled job.

        Args:
            chat: Telegram chat where the job is running
            coin_id: Cryptocurrency coin identifier
            coin_vs: Currency to compare against

        Raises:
            CoinInfoJobNotExistentError: If job does not exist
        """
        job_id = self.__GetJobId(chat, coin_id, coin_vs)

        if not self.IsActiveInChat(chat, coin_id, coin_vs):
            self.logger.GetLogger().error(f'Job "{job_id}" not active in chat {ChatHelper.GetTitleOrId(chat)}, cannot stop it')
            raise CoinInfoJobNotExistentError()

        del self.jobs[chat.id][job_id]
        self.scheduler.remove_job(job_id)
        self.logger.GetLogger().info(
            f'Stopped job "{job_id}" in chat {ChatHelper.GetTitleOrId(chat)}, number of active jobs: {self.__GetTotalJobCount()}'
        )

    def StopAll(self, chat: pyrogram.types.Chat) -> None:
        """Stop all jobs in a chat.

        Args:
            chat: Telegram chat to stop all jobs in
        """
        if chat.id not in self.jobs:
            self.logger.GetLogger().info(f"No job to stop in chat {ChatHelper.GetTitleOrId(chat)}, exiting...")
            return

        for job_id in self.jobs[chat.id].keys():
            self.scheduler.remove_job(job_id)
            self.logger.GetLogger().info(f'Stopped job "{job_id}" in chat {ChatHelper.GetTitleOrId(chat)}')
        del self.jobs[chat.id]
        self.logger.GetLogger().info(
            f"Removed all jobs in chat {ChatHelper.GetTitleOrId(chat)}, number of active jobs: {self.__GetTotalJobCount()}"
        )

    def ChatLeft(self, chat: pyrogram.types.Chat) -> None:
        """Handle bot leaving a chat by stopping all jobs.

        Args:
            chat: Telegram chat that was left
        """
        self.logger.GetLogger().info(f"Left chat {ChatHelper.GetTitleOrId(chat)}, stopping all chat jobs...")
        self.StopAll(chat)

    def Pause(self,
              chat: pyrogram.types.Chat,
              coin_id: str,
              coin_vs: str) -> None:
        """Pause a scheduled job.

        Args:
            chat: Telegram chat where the job is running
            coin_id: Cryptocurrency coin identifier
            coin_vs: Currency to compare against

        Raises:
            CoinInfoJobNotExistentError: If job does not exist
        """
        job_id = self.__GetJobId(chat, coin_id, coin_vs)

        if not self.IsActiveInChat(chat, coin_id, coin_vs):
            self.logger.GetLogger().error(f'Job "{job_id}" not active in chat {ChatHelper.GetTitleOrId(chat)}, cannot pause it')
            raise CoinInfoJobNotExistentError()

        self.jobs[chat.id][job_id].SetRunning(False)
        self.scheduler.pause_job(job_id)
        self.logger.GetLogger().info(f'Paused job "{job_id}" in chat {ChatHelper.GetTitleOrId(chat)}')

    def Resume(self,
               chat: pyrogram.types.Chat,
               coin_id: str,
               coin_vs: str) -> None:
        """Resume a paused job.

        Args:
            chat: Telegram chat where the job is running
            coin_id: Cryptocurrency coin identifier
            coin_vs: Currency to compare against

        Raises:
            CoinInfoJobNotExistentError: If job does not exist
        """
        job_id = self.__GetJobId(chat, coin_id, coin_vs)

        if not self.IsActiveInChat(chat, coin_id, coin_vs):
            self.logger.GetLogger().error(f'Job "{job_id}" not active in chat {ChatHelper.GetTitleOrId(chat)}, cannot resume it')
            raise CoinInfoJobNotExistentError()

        self.jobs[chat.id][job_id].SetRunning(True)
        self.scheduler.resume_job(job_id)
        self.logger.GetLogger().info(f'Resumed job "{job_id}" in chat {ChatHelper.GetTitleOrId(chat)}')

    def SendInSameMessage(self,
                          chat: pyrogram.types.Chat,
                          coin_id: str,
                          coin_vs: str,
                          flag: bool) -> None:
        """Set whether to send updates in the same message.

        Args:
            chat: Telegram chat where the job is running
            coin_id: Cryptocurrency coin identifier
            coin_vs: Currency to compare against
            flag: True to send in same message, False otherwise

        Raises:
            CoinInfoJobNotExistentError: If job does not exist
        """
        job_id = self.__GetJobId(chat, coin_id, coin_vs)

        if not self.IsActiveInChat(chat, coin_id, coin_vs):
            self.logger.GetLogger().error(f'Job "{job_id}" not active in chat {ChatHelper.GetTitleOrId(chat)}')
            raise CoinInfoJobNotExistentError()

        self.jobs[chat.id][job_id].SendInSameMessage(flag)
        self.logger.GetLogger().info(f'Set send in same message to {flag} for job "{job_id}" in chat {ChatHelper.GetTitleOrId(chat)}')

    def DeleteLastSentMessage(self,
                              chat: pyrogram.types.Chat,
                              coin_id: str,
                              coin_vs: str,
                              flag: bool) -> None:
        """Set whether to delete the last sent message.

        Args:
            chat: Telegram chat where the job is running
            coin_id: Cryptocurrency coin identifier
            coin_vs: Currency to compare against
            flag: True to delete last message, False otherwise

        Raises:
            CoinInfoJobNotExistentError: If job does not exist
        """
        job_id = self.__GetJobId(chat, coin_id, coin_vs)

        if not self.IsActiveInChat(chat, coin_id, coin_vs):
            self.logger.GetLogger().error(f'Job "{job_id}" not active in chat {ChatHelper.GetTitleOrId(chat)}')
            raise CoinInfoJobNotExistentError()

        self.jobs[chat.id][job_id].DeleteLastSentMessage(flag)
        self.logger.GetLogger().info(f'Set delete last message to {flag} for job "{job_id}" in chat {ChatHelper.GetTitleOrId(chat)}')

    def __CreateJob(self,
                    job_id: str,
                    chat: pyrogram.types.Chat,
                    period: int,
                    start: int,
                    coin_id: str,
                    coin_vs: str,
                    last_days: int) -> None:
        """Create a new job instance.

        Args:
            job_id: Unique identifier for the job
            chat: Telegram chat where the job will run
            period: Period in hours between executions
            start: Starting hour for the job
            coin_id: Cryptocurrency coin identifier
            coin_vs: Currency to compare against
            last_days: Number of days of historical data
        """
        if chat.id not in self.jobs:
            self.jobs[chat.id] = {}

        self.jobs[chat.id][job_id] = CoinInfoJob(
            self.client, self.config, self.logger, self.translator, CoinInfoJobData(chat, period, start, coin_id, coin_vs, last_days)
        )

    def __AddJob(self,
                 job_id: str,
                 chat: pyrogram.types.Chat,
                 period: int,
                 start: int,
                 coin_id: str,
                 coin_vs: str,
                 last_days: int) -> None:
        """Add a job to the scheduler.

        Args:
            job_id: Unique identifier for the job
            chat: Telegram chat where the job will run
            period: Period in hours between executions
            start: Starting hour for the job
            coin_id: Cryptocurrency coin identifier
            coin_vs: Currency to compare against
            last_days: Number of days of historical data
        """
        is_test_mode = self.config.GetValue(BotConfigTypes.APP_TEST_MODE)
        cron_str = self.__BuildCronString(period, start, is_test_mode)
        if is_test_mode:
            self.scheduler.add_job(
                self.jobs[chat.id][job_id].DoJob, "cron", args=(chat, coin_id, coin_vs, last_days), minute=cron_str, id=job_id
            )
        else:
            self.scheduler.add_job(
                self.jobs[chat.id][job_id].DoJob, "cron", args=(chat, coin_id, coin_vs, last_days), hour=cron_str, id=job_id
            )
        per_sym = "minute(s)" if is_test_mode else "hour(s)"
        self.logger.GetLogger().info(
            f'Started job "{job_id}" in chat {ChatHelper.GetTitleOrId(chat)} [parameters: {period} {per_sym}, '
            f"{coin_id}, {coin_vs}, {last_days}], number of active jobs: {self.__GetTotalJobCount()}, cron: {cron_str}"
        )

    @staticmethod
    def __GetJobId(chat: pyrogram.types.Chat,
                   coin_id: str,
                   coin_vs: str) -> str:
        """Generate a unique job identifier.

        Args:
            chat: Telegram chat
            coin_id: Cryptocurrency coin identifier
            coin_vs: Currency to compare against

        Returns:
            Unique job identifier string
        """
        return f"{chat.id}-{coin_id}-{coin_vs}"

    def __GetTotalJobCount(self) -> int:
        """Get the total number of active jobs across all chats.

        Returns:
            Total number of jobs
        """
        return sum([len(jobs) for (_, jobs) in self.jobs.items()])

    @staticmethod
    def __BuildCronString(period: int,
                          start_val: int,
                          is_test_mode: bool) -> str:
        """Build a cron expression string for job scheduling.

        Args:
            period: Period between executions
            start_val: Starting value (hour or minute)
            is_test_mode: True for test mode (minutes), False for production (hours)

        Returns:
            Cron expression string
        """
        max_val = 24 if not is_test_mode else 60

        cron_str = ""

        loop_cnt = max_val // period
        if max_val % period != 0:
            loop_cnt += 1

        t = start_val
        for _ in range(loop_cnt):
            cron_str += f"{t},"
            t = (t + period) % max_val

        return cron_str[:-1]
