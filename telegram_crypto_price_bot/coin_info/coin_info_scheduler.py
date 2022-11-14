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


#
# Classes
#

# Job already existent error
class CoinInfoJobAlreadyExistentError(Exception):
    pass


# Job not existent error
class CoinInfoJobNotExistentError(Exception):
    pass


# Job invalid period error
class CoinInfoJobInvalidPeriodError(Exception):
    pass


# Job invalid start error
class CoinInfoJobInvalidStartError(Exception):
    pass


# Job maximum number error
class CoinInfoJobMaxNumError(Exception):
    pass


# Constants for coin info scheduler
class CoinInfoSchedulerConst:
    # Minimum/Maximum start hour
    MIN_START_HOUR: int = 0
    MAX_START_HOUR: int = 23
    # Minimum/Maximum periods
    MIN_PERIOD_HOURS: int = 1
    MAX_PERIOD_HOURS: int = 24


# Coin info jobs list class
class CoinInfoJobsList(WrappedList):

    translator: TranslationLoader

    # Constructor
    def __init__(self,
                 translator: TranslationLoader) -> None:
        super().__init__()
        self.translator = translator

    # Convert to string
    def ToString(self) -> str:
        return "\n".join(
            [self.translator.GetSentence("SINGLE_TASK_INFO_MSG",
                                         coin_id=job_data.CoinId(),
                                         coin_vs=job_data.CoinVs(),
                                         period=job_data.PeriodHours(),
                                         start=job_data.StartHour(),
                                         last_days=job_data.LastDays(),
                                         state=(self.translator.GetSentence("TASK_RUNNING_MSG")
                                                if job_data.IsRunning()
                                                else self.translator.GetSentence("TASK_PAUSED_MSG"))
                                         )
             for job_data in self.list_elements]
        )

    # Convert to string
    def __str__(self) -> str:
        return self.ToString()


# Coin info scheduler class
class CoinInfoScheduler:

    client: pyrogram.Client
    config: ConfigObject
    logger: Logger
    translator: TranslationLoader
    jobs: Dict[int, Dict[str, CoinInfoJob]]
    scheduler: BackgroundScheduler

    # Constructor
    def __init__(self,
                 client: pyrogram.Client,
                 config: ConfigObject,
                 logger: Logger,
                 translator: TranslationLoader) -> None:
        self.client = client
        self.config = config
        self.logger = logger
        self.translator = translator
        self.jobs = {}
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()

    # Get the list of active jobs in chat
    def GetJobsInChat(self,
                      chat: pyrogram.types.Chat) -> CoinInfoJobsList:
        jobs_list = CoinInfoJobsList(self.translator)
        jobs_list.AddMultiple(
            [job.Data() for (_, job) in self.jobs[chat.id].items()] if chat.id in self.jobs else []
        )

        return jobs_list

    # Get if job is active in chat
    def IsActiveInChat(self,
                       chat: pyrogram.types.Chat,
                       coin_id: str,
                       coin_vs: str) -> bool:
        job_id = self.__GetJobId(chat, coin_id, coin_vs)
        return (chat.id in self.jobs and
                job_id in self.jobs[chat.id] and
                self.scheduler.get_job(job_id) is not None)

    # Start job
    def Start(self,
              chat: pyrogram.types.Chat,
              period_hours: int,
              start_hour: int,
              coin_id: str,
              coin_vs: str,
              last_days: int) -> None:
        job_id = self.__GetJobId(chat, coin_id, coin_vs)

        # Check if existent
        if self.IsActiveInChat(chat, coin_id, coin_vs):
            self.logger.GetLogger().error(
                f"Job \"{job_id}\" already active in chat {ChatHelper.GetTitleOrId(chat)}, cannot start it"
            )
            raise CoinInfoJobAlreadyExistentError()

        # Check period
        if period_hours < CoinInfoSchedulerConst.MIN_PERIOD_HOURS or period_hours > CoinInfoSchedulerConst.MAX_PERIOD_HOURS:
            self.logger.GetLogger().error(
                f"Invalid period {period_hours} for job \"{job_id}\", cannot start it"
            )
            raise CoinInfoJobInvalidPeriodError()

        # Check start
        if start_hour < CoinInfoSchedulerConst.MIN_START_HOUR or start_hour > CoinInfoSchedulerConst.MAX_START_HOUR:
            self.logger.GetLogger().error(
                f"Invalid start hour {start_hour} for job \"{job_id}\", cannot start it"
            )
            raise CoinInfoJobInvalidStartError()

        # Check total jobs number
        tot_job_cnt = self.__GetTotalJobCount()
        if tot_job_cnt >= self.config.GetValue(BotConfigTypes.TASKS_MAX_NUM):
            self.logger.GetLogger().error("Maximum number of jobs reached, cannot start a new one")
            raise CoinInfoJobMaxNumError()

        # Create job
        self.__CreateJob(job_id, chat, period_hours, start_hour, coin_id, coin_vs, last_days)
        # Add job
        self.__AddJob(job_id, chat, period_hours, start_hour, coin_id, coin_vs, last_days)

    # Stop job
    def Stop(self,
             chat: pyrogram.types.Chat,
             coin_id: str,
             coin_vs: str) -> None:
        job_id = self.__GetJobId(chat, coin_id, coin_vs)

        if not self.IsActiveInChat(chat, coin_id, coin_vs):
            self.logger.GetLogger().error(
                f"Job \"{job_id}\" not active in chat {ChatHelper.GetTitleOrId(chat)}, cannot stop it"
            )
            raise CoinInfoJobNotExistentError()

        del self.jobs[chat.id][job_id]
        self.scheduler.remove_job(job_id)
        self.logger.GetLogger().info(
            f"Stopped job \"{job_id}\" in chat {ChatHelper.GetTitleOrId(chat)}, "
            f"number of active jobs: {self.__GetTotalJobCount()}"
        )

    # Stop all jobs
    def StopAll(self,
                chat: pyrogram.types.Chat) -> None:
        # Check if there are jobs to stop
        if chat.id not in self.jobs:
            self.logger.GetLogger().info(
                f"No job to stop in chat {ChatHelper.GetTitleOrId(chat)}, exiting..."
            )
            return

        # Stop all jobs
        for job_id in self.jobs[chat.id].keys():
            self.scheduler.remove_job(job_id)
            self.logger.GetLogger().info(
                f"Stopped job \"{job_id}\" in chat {ChatHelper.GetTitleOrId(chat)}"
            )
        # Delete entry
        del self.jobs[chat.id]
        # Log
        self.logger.GetLogger().info(
            f"Removed all jobs in chat {ChatHelper.GetTitleOrId(chat)}, number of active jobs: {self.__GetTotalJobCount()}"
        )

    # Called when chat is left by the bot
    def ChatLeft(self,
                 chat: pyrogram.types.Chat) -> None:
        self.logger.GetLogger().info(
            f"Left chat {ChatHelper.GetTitleOrId(chat)}, stopping all chat jobs..."
        )
        self.StopAll(chat)

    # Pause job
    def Pause(self,
              chat: pyrogram.types.Chat,
              coin_id: str,
              coin_vs: str) -> None:
        job_id = self.__GetJobId(chat, coin_id, coin_vs)

        if not self.IsActiveInChat(chat, coin_id, coin_vs):
            self.logger.GetLogger().error(
                f"Job \"{job_id}\" not active in chat {ChatHelper.GetTitleOrId(chat)}, cannot pause it"
            )
            raise CoinInfoJobNotExistentError()

        self.jobs[chat.id][job_id].SetRunning(False)
        self.scheduler.pause_job(job_id)
        self.logger.GetLogger().info(
            f"Paused job \"{job_id}\" in chat {ChatHelper.GetTitleOrId(chat)}"
        )

    # Resume job
    def Resume(self,
               chat: pyrogram.types.Chat,
               coin_id: str,
               coin_vs: str) -> None:
        job_id = self.__GetJobId(chat, coin_id, coin_vs)

        if not self.IsActiveInChat(chat, coin_id, coin_vs):
            self.logger.GetLogger().error(
                f"Job \"{job_id}\" not active in chat {ChatHelper.GetTitleOrId(chat)}, cannot resume it"
            )
            raise CoinInfoJobNotExistentError()

        self.jobs[chat.id][job_id].SetRunning(True)
        self.scheduler.resume_job(job_id)
        self.logger.GetLogger().info(
            f"Resumed job \"{job_id}\" in chat {ChatHelper.GetTitleOrId(chat)}"
        )

    # Set send in same message flag
    def SendInSameMessage(self,
                          chat: pyrogram.types.Chat,
                          coin_id: str,
                          coin_vs: str,
                          flag: bool) -> None:
        job_id = self.__GetJobId(chat, coin_id, coin_vs)

        if not self.IsActiveInChat(chat, coin_id, coin_vs):
            self.logger.GetLogger().error(
                f"Job \"{job_id}\" not active in chat {ChatHelper.GetTitleOrId(chat)}"
            )
            raise CoinInfoJobNotExistentError()

        self.jobs[chat.id][job_id].SendInSameMessage(flag)
        self.logger.GetLogger().info(
            f"Set send in same message to {flag} for job \"{job_id}\" in chat {ChatHelper.GetTitleOrId(chat)}"
        )

    # Set delete last sent message flag
    def DeleteLastSentMessage(self,
                              chat: pyrogram.types.Chat,
                              coin_id: str,
                              coin_vs: str,
                              flag: bool) -> None:
        job_id = self.__GetJobId(chat, coin_id, coin_vs)

        if not self.IsActiveInChat(chat, coin_id, coin_vs):
            self.logger.GetLogger().error(
                f"Job \"{job_id}\" not active in chat {ChatHelper.GetTitleOrId(chat)}"
            )
            raise CoinInfoJobNotExistentError()

        self.jobs[chat.id][job_id].DeleteLastSentMessage(flag)
        self.logger.GetLogger().info(
            f"Set delete last message to {flag} for job \"{job_id}\" in chat {ChatHelper.GetTitleOrId(chat)}"
        )

    # Create tak
    def __CreateJob(self,
                    job_id: str,
                    chat: pyrogram.types.Chat,
                    period: int,
                    start: int,
                    coin_id: str,
                    coin_vs: str,
                    last_days: int) -> None:
        if chat.id not in self.jobs:
            self.jobs[chat.id] = {}

        self.jobs[chat.id][job_id] = CoinInfoJob(self.client,
                                                 self.config,
                                                 self.logger,
                                                 self.translator,
                                                 CoinInfoJobData(chat, period, start, coin_id, coin_vs, last_days))

    # Add job
    def __AddJob(self,
                 job_id: str,
                 chat: pyrogram.types.Chat,
                 period: int,
                 start: int,
                 coin_id: str,
                 coin_vs: str,
                 last_days: int) -> None:
        is_test_mode = self.config.GetValue(BotConfigTypes.APP_TEST_MODE)
        cron_str = self.__BuildCronString(period, start, is_test_mode)
        if is_test_mode:
            self.scheduler.add_job(self.jobs[chat.id][job_id].DoJob,
                                   "cron",
                                   args=(chat, coin_id, coin_vs, last_days),
                                   minute=cron_str,
                                   id=job_id)
        else:
            self.scheduler.add_job(self.jobs[chat.id][job_id].DoJob,
                                   "cron",
                                   args=(chat, coin_id, coin_vs, last_days),
                                   hour=cron_str,
                                   id=job_id)
        # Log
        per_sym = "minute(s)" if is_test_mode else "hour(s)"
        self.logger.GetLogger().info(
            f"Started job \"{job_id}\" in chat {ChatHelper.GetTitleOrId(chat)} [parameters: {period} {per_sym}, "
            f"{coin_id}, {coin_vs}, {last_days}], number of active jobs: {self.__GetTotalJobCount()}, cron: {cron_str}"
        )

    # Get job ID
    @staticmethod
    def __GetJobId(chat: pyrogram.types.Chat,
                   coin_id: str,
                   coin_vs: str) -> str:
        return f"{chat.id}-{coin_id}-{coin_vs}"

    # Get total job count
    def __GetTotalJobCount(self) -> int:
        return sum([len(jobs) for (_, jobs) in self.jobs.items()])

    # Build cron string
    @staticmethod
    def __BuildCronString(period: int,
                          start_val: int,
                          is_test_mode: bool) -> str:
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
