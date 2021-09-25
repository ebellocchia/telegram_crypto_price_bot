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
from apscheduler.schedulers.background import BackgroundScheduler
from telegram_crypto_price_bot.coin_info_message_sender import CoinInfoMessageSender
from telegram_crypto_price_bot.config import ConfigTypes, Config
from telegram_crypto_price_bot.logger import Logger
from telegram_crypto_price_bot.translation_loader import TranslationLoader
from telegram_crypto_price_bot.wrapped_list import WrappedList


#
# Classes
#

# Task already existent error
class CoinInfoTaskAlreadyExistentError(Exception):
    pass


# Task not existent error
class CoinInfoTaskNotExistentError(Exception):
    pass


# Task invalid period error
class CoinInfoTaskInvalidPeriodError(Exception):
    pass


# Task maximum number error
class CoinInfoTaskMaxNumError(Exception):
    pass


# Constants for coin info task
class CoinInfoTaskConst:
    # Minimum/Maximum periods
    MIN_PERIOD_HOURS: int = 1
    MAX_PERIOD_HOURS: int = 24


# Coin info task class
class CoinInfoTaskData:
    # Constructor
    def __init__(self,
                 chat: pyrogram.types.Chat,
                 period_hours: int,
                 coin_id: str,
                 coin_vs: str,
                 last_days: int) -> None:
        self.chat = chat
        self.period_hours = period_hours
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


# Coin info task list class
class CoinInfoTasksList(WrappedList):
    # Constructor
    def __init__(self,
                 translator: TranslationLoader) -> None:
        super().__init__()
        self.translator = translator

    # Convert to string
    def ToString(self) -> str:
        return "\n".join(
            [self.translator.GetSentence("SINGLE_TASK_INFO_MSG",
                                         coin_id=task_data.CoinId(),
                                         coin_vs=task_data.CoinVs(),
                                         period=task_data.PeriodHours(),
                                         last_days=task_data.LastDays())
             for task_data in self.list_elements]
        )

    # Convert to string
    def __str__(self) -> str:
        return self.ToString()


# Coin info tasks class
class CoinInfoTasks:
    # Constructor
    def __init__(self,
                 client: pyrogram.Client,
                 config: Config,
                 logger: Logger,
                 translator: TranslationLoader) -> None:
        self.client = client
        self.config = config
        self.logger = logger
        self.translator = translator
        self.tasks = {}
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()

    # Get the list of active tasks in chat
    def GetTasksInChat(self,
                       chat: pyrogram.types.Chat) -> CoinInfoTasksList:
        tasks_list = CoinInfoTasksList(self.translator)
        tasks_list.AddMultiple(
            [task["data"] for (_, task) in self.tasks[chat.id].items()] if chat.id in self.tasks else []
        )

        return tasks_list

    # Get if task is active in chat
    def IsActiveInChat(self,
                       chat: pyrogram.types.Chat,
                       coin_id: str,
                       coin_vs: str) -> bool:
        task_id = self.__GetTaskId(chat, coin_id, coin_vs)
        return (chat.id in self.tasks and
                task_id in self.tasks[chat.id] and
                self.scheduler.get_job(task_id) is not None)

    # Start task
    def Start(self,
              chat: pyrogram.types.Chat,
              period_hours: int,
              coin_id: str,
              coin_vs: str,
              last_days: int) -> None:
        task_id = self.__GetTaskId(chat, coin_id, coin_vs)

        # Check if existent
        if self.IsActiveInChat(chat, coin_id, coin_vs):
            self.logger.GetLogger().error(f"Task {task_id} already active in chat {chat.id}, cannot start it")
            raise CoinInfoTaskAlreadyExistentError()

        # Check period
        if period_hours < CoinInfoTaskConst.MIN_PERIOD_HOURS or period_hours > CoinInfoTaskConst.MAX_PERIOD_HOURS:
            self.logger.GetLogger().error(f"Invalid period {period_hours} for task {task_id}, cannot start it")
            raise CoinInfoTaskInvalidPeriodError()

        # Check total tasks number
        tot_task_cnt = self.__GetTotalTaskCount()
        if tot_task_cnt >= self.config.GetValue(ConfigTypes.TASKS_MAX_NUM):
            self.logger.GetLogger().error(f"Maximum number of tasks reached, cannot start a new one")
            raise CoinInfoTaskMaxNumError()

        # Create task
        self.__CreateTask(task_id, chat, period_hours, coin_id, coin_vs, last_days)
        # Add task
        self.__AddTask(task_id, chat, period_hours, coin_id, coin_vs, last_days)

    # Stop task
    def Stop(self,
             chat: pyrogram.types.Chat,
             coin_id: str,
             coin_vs: str) -> None:
        task_id = self.__GetTaskId(chat, coin_id, coin_vs)

        if not self.IsActiveInChat(chat, coin_id, coin_vs):
            self.logger.GetLogger().error(f"Task {task_id} not active in chat {chat.id}, cannot stop it")
            raise CoinInfoTaskNotExistentError()

        del self.tasks[chat.id][task_id]
        self.scheduler.remove_job(task_id)
        self.logger.GetLogger().info(
            f"Stopped task {task_id} in chat {chat.id}, number of active tasks: {self.__GetTotalTaskCount()}"
        )

    # Pause task
    def Pause(self,
              chat: pyrogram.types.Chat,
              coin_id: str,
              coin_vs: str) -> None:
        task_id = self.__GetTaskId(chat, coin_id, coin_vs)

        if not self.IsActiveInChat(chat, coin_id, coin_vs):
            self.logger.GetLogger().error(f"Task {task_id} not active in chat {chat.id}, cannot pause it")
            raise CoinInfoTaskNotExistentError()

        self.tasks[chat.id][task_id]["data"].SetRunning(False)
        self.scheduler.pause_job(task_id)
        self.logger.GetLogger().info(f"Paused task {task_id} in chat {chat.id}")

    # Resume task
    def Resume(self,
               chat: pyrogram.types.Chat,
               coin_id: str,
               coin_vs: str) -> None:
        task_id = self.__GetTaskId(chat, coin_id, coin_vs)

        if not self.IsActiveInChat(chat, coin_id, coin_vs):
            self.logger.GetLogger().error(f"Task {task_id} not active in chat {chat.id}, cannot resume it")
            raise CoinInfoTaskNotExistentError()

        self.tasks[chat.id][task_id]["data"].SetRunning(True)
        self.scheduler.resume_job(task_id)
        self.logger.GetLogger().info(f"Resumed task {task_id} in chat {chat.id}")

    # Set send in same message flag
    def SendInSameMessage(self,
                          chat: pyrogram.types.Chat,
                          coin_id: str,
                          coin_vs: str,
                          flag: bool) -> None:
        task_id = self.__GetTaskId(chat, coin_id, coin_vs)

        if not self.IsActiveInChat(chat, coin_id, coin_vs):
            self.logger.GetLogger().error(f"Task {task_id} not active in chat {chat.id}")
            raise CoinInfoTaskNotExistentError()

        self.tasks[chat.id][task_id]["sender"].SendInSameMessage(flag)
        self.logger.GetLogger().info(f"Set send in same message to {flag} for task {task_id} in chat {chat.id}")

    # Set delete last sent message flag
    def DeleteLastSentMessage(self,
                              chat: pyrogram.types.Chat,
                              coin_id: str,
                              coin_vs: str,
                              flag: bool) -> None:
        task_id = self.__GetTaskId(chat, coin_id, coin_vs)

        if not self.IsActiveInChat(chat, coin_id, coin_vs):
            self.logger.GetLogger().error(f"Task {task_id} not active in chat {chat.id}")
            raise CoinInfoTaskNotExistentError()

        self.tasks[chat.id][task_id]["sender"].DeleteLastSentMessage(flag)
        self.logger.GetLogger().info(f"Set delete last message to {flag} for task {task_id} in chat {chat.id}")

    # Create tak
    def __CreateTask(self,
                     task_id: str,
                     chat: pyrogram.types.Chat,
                     period: int,
                     coin_id: str,
                     coin_vs: str,
                     last_days: int) -> None:
        if chat.id not in self.tasks:
            self.tasks[chat.id] = {}

        self.tasks[chat.id][task_id] = {
            "data": CoinInfoTaskData(chat, period, coin_id, coin_vs, last_days),
            "sender": CoinInfoMessageSender(self.client, self.config, self.logger, self.translator)
        }

    # Add task
    def __AddTask(self,
                  task_id: str,
                  chat: pyrogram.types.Chat,
                  period: int,
                  coin_id: str,
                  coin_vs: str,
                  last_days: int) -> None:
        is_test_mode = self.config.GetValue(ConfigTypes.APP_TEST_MODE)
        if is_test_mode:
            self.scheduler.add_job(self.tasks[chat.id][task_id]["sender"].SendMessage,
                                   "cron",
                                   args=(chat, coin_id, coin_vs, last_days),
                                   minute=self.__BuildCronString(period, is_test_mode),
                                   id=task_id)
        else:
            self.scheduler.add_job(self.tasks[chat.id][task_id]["sender"].SendMessage,
                                   "cron",
                                   args=(chat, coin_id, coin_vs, last_days),
                                   hour=self.__BuildCronString(period, is_test_mode),
                                   id=task_id)
        # Log
        per_sym = "minute(s)" if is_test_mode else "hour(s)"
        self.logger.GetLogger().info(
            f"Started task {task_id} in chat {chat.id} ({period} {per_sym}, "
            f"{coin_id}, {coin_vs}, {last_days}), number of active tasks: {self.__GetTotalTaskCount()}"
        )

    # Get task ID
    @staticmethod
    def __GetTaskId(chat: pyrogram.types.Chat,
                    coin_id: str,
                    coin_vs: str) -> str:
        return f"{chat.id}-{coin_id}-{coin_vs}"

    # Get total task count
    def __GetTotalTaskCount(self) -> int:
        return sum([len(tasks) for (_, tasks) in self.tasks.items()])

    # Build cron string
    @staticmethod
    def __BuildCronString(period: int,
                          is_test_mode: bool) -> str:
        max_val = 24 if not is_test_mode else 60

        cron_str = ""
        for i in range(0, max_val, period):
            cron_str += f"{i},"

        return cron_str[:-1]
