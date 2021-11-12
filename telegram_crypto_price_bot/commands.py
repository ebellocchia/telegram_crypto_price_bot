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
from typing import Any, Callable
from telegram_crypto_price_bot.coin_info_message_sender import CoinInfoMessageSender
from telegram_crypto_price_bot.coin_info_scheduler import (
    CoinInfoJobAlreadyExistentError, CoinInfoJobNotExistentError,
    CoinInfoJobInvalidPeriodError, CoinInfoJobInvalidStartError,
    CoinInfoJobMaxNumError
)
from telegram_crypto_price_bot.command_base import CommandBase
from telegram_crypto_price_bot.command_data import CommandParameterError
from telegram_crypto_price_bot.config import ConfigTypes
from telegram_crypto_price_bot.helpers import UserHelper


#
# Decorators
#

# Decorator for group-only commands
def GroupChatOnly(exec_cmd_fct: Callable[..., None]) -> Callable[..., None]:
    def decorated(self,
                  **kwargs: Any):
        # Check if private chat
        if self._IsPrivateChat():
            self._SendMessage(self.translator.GetSentence("GROUP_ONLY_ERR_MSG"))
        else:
            exec_cmd_fct(self, **kwargs)

    return decorated


#
# Classes
#

#
# Command for getting help
#
class HelpCmd(CommandBase):
    # Execute command
    def _ExecuteCommand(self,
                        **kwargs: Any) -> None:
        self._SendMessage(
            self.translator.GetSentence("HELP_CMD",
                                        name=UserHelper.GetName(self.cmd_data.User()))
        )


#
# Command for checking if bot is alive
#
class AliveCmd(CommandBase):
    # Execute command
    def _ExecuteCommand(self,
                        **kwargs: Any) -> None:
        self._SendMessage(self.translator.GetSentence("ALIVE_CMD"))


#
# Command for setting test mode
#
class SetTestModeCmd(CommandBase):
    # Execute command
    @GroupChatOnly
    def _ExecuteCommand(self,
                        **kwargs: Any) -> None:
        try:
            # Get parameters
            flag = self.cmd_data.Params().GetAsBool(0)
        except CommandParameterError:
            self._SendMessage(self.translator.GetSentence("PARAM_ERR_MSG"))
        else:
            # Set test mode
            self.config.SetValue(ConfigTypes.APP_TEST_MODE, flag)

            # Send message
            if self.config.GetValue(ConfigTypes.APP_TEST_MODE):
                self._SendMessage(self.translator.GetSentence("SET_TEST_MODE_EN_CMD"))
            else:
                self._SendMessage(self.translator.GetSentence("SET_TEST_MODE_DIS_CMD"))


#
# Command for checking if test mode
#
class IsTestModeCmd(CommandBase):
    # Execute command
    def _ExecuteCommand(self,
                        **kwargs: Any) -> None:
        if self.config.GetValue(ConfigTypes.APP_TEST_MODE):
            self._SendMessage(self.translator.GetSentence("IS_TEST_MODE_EN_CMD"))
        else:
            self._SendMessage(self.translator.GetSentence("IS_TEST_MODE_DIS_CMD"))


#
# Get single price command
#
class PriceGetSingleCmd(CommandBase):
    # Execute command
    def _ExecuteCommand(self,
                        **kwargs: Any) -> None:
        # Get parameters
        try:
            coin_id = self.cmd_data.Params().GetAsString(0)
            coin_vs = self.cmd_data.Params().GetAsString(1)
            last_days = self.cmd_data.Params().GetAsInt(2)
            same_msg = self.cmd_data.Params().GetAsBool(3, True)
        except CommandParameterError:
            self._SendMessage(self.translator.GetSentence("PARAM_ERR_MSG"))
        else:
            coin_info_sender = CoinInfoMessageSender(self.client, self.config, self.logger, self.translator)
            coin_info_sender.SendInSameMessage(same_msg)
            coin_info_sender.SendMessage(self.cmd_data.Chat(), coin_id, coin_vs, last_days)


#
# Price task start command
#
class PriceTaskStartCmd(CommandBase):
    # Execute command
    @GroupChatOnly
    def _ExecuteCommand(self,
                        **kwargs: Any) -> None:
        # Get parameters
        try:
            period_hours = self.cmd_data.Params().GetAsInt(0)
            start_hour = self.cmd_data.Params().GetAsInt(1)
            coin_id = self.cmd_data.Params().GetAsString(2)
            coin_vs = self.cmd_data.Params().GetAsString(3)
            last_days = self.cmd_data.Params().GetAsInt(4)
        except CommandParameterError:
            self._SendMessage(self.translator.GetSentence("PARAM_ERR_MSG"))
        else:
            try:
                kwargs["coin_info_scheduler"].Start(self.cmd_data.Chat(), period_hours, start_hour, coin_id, coin_vs, last_days)
                self._SendMessage(
                    self.translator.GetSentence("PRICE_TASK_START_OK_CMD",
                                                period=period_hours,
                                                start=start_hour,
                                                coin_id=coin_id,
                                                coin_vs=coin_vs,
                                                last_days=last_days)
                )
            except CoinInfoJobInvalidPeriodError:
                self._SendMessage(self.translator.GetSentence("TASK_PERIOD_ERR_MSG"))
            except CoinInfoJobInvalidStartError:
                self._SendMessage(self.translator.GetSentence("TASK_START_ERR_MSG"))
            except CoinInfoJobMaxNumError:
                self._SendMessage(self.translator.GetSentence("MAX_TASK_ERR_MSG"))
            except CoinInfoJobAlreadyExistentError:
                self._SendMessage(
                    self.translator.GetSentence("TASK_EXISTENT_ERR_MSG",
                                                coin_id=coin_id,
                                                coin_vs=coin_vs)
                )


#
# Price task stop command
#
class PriceTaskStopCmd(CommandBase):
    # Execute command
    @GroupChatOnly
    def _ExecuteCommand(self,
                        **kwargs: Any) -> None:
        # Get parameters
        try:
            coin_id = self.cmd_data.Params().GetAsString(0)
            coin_vs = self.cmd_data.Params().GetAsString(1)
        except CommandParameterError:
            self._SendMessage(self.translator.GetSentence("PARAM_ERR_MSG"))
        else:
            try:
                kwargs["coin_info_scheduler"].Stop(self.cmd_data.Chat(), coin_id, coin_vs)
                self._SendMessage(
                    self.translator.GetSentence("PRICE_TASK_STOP_OK_CMD",
                                                coin_id=coin_id,
                                                coin_vs=coin_vs)
                )
            except CoinInfoJobNotExistentError:
                self._SendMessage(
                    self.translator.GetSentence("TASK_NOT_EXISTENT_ERR_MSG",
                                                coin_id=coin_id,
                                                coin_vs=coin_vs)
                )


#
# Price task stop all command
#
class PriceTaskStopAllCmd(CommandBase):
    # Execute command
    @GroupChatOnly
    def _ExecuteCommand(self,
                        **kwargs: Any) -> None:
        kwargs["coin_info_scheduler"].StopAll(self.cmd_data.Chat())
        self._SendMessage(
            self.translator.GetSentence("PRICE_TASK_STOP_ALL_CMD")
        )


#
# Price task pause command
#
class PriceTaskPauseCmd(CommandBase):
    # Execute command
    @GroupChatOnly
    def _ExecuteCommand(self,
                        **kwargs: Any) -> None:
        # Get parameters
        try:
            coin_id = self.cmd_data.Params().GetAsString(0)
            coin_vs = self.cmd_data.Params().GetAsString(1)
        except CommandParameterError:
            self._SendMessage(self.translator.GetSentence("PARAM_ERR_MSG"))
        else:
            try:
                kwargs["coin_info_scheduler"].Pause(self.cmd_data.Chat(), coin_id, coin_vs)
                self._SendMessage(
                    self.translator.GetSentence("PRICE_TASK_PAUSE_OK_CMD",
                                                coin_id=coin_id,
                                                coin_vs=coin_vs)
                )
            except CoinInfoJobNotExistentError:
                self._SendMessage(
                    self.translator.GetSentence("TASK_NOT_EXISTENT_ERR_MSG",
                                                coin_id=coin_id,
                                                coin_vs=coin_vs)
                )


#
# Price task resume command
#
class PriceTaskResumeCmd(CommandBase):
    # Execute command
    @GroupChatOnly
    def _ExecuteCommand(self,
                        **kwargs: Any) -> None:
        # Get parameters
        try:
            coin_id = self.cmd_data.Params().GetAsString(0)
            coin_vs = self.cmd_data.Params().GetAsString(1)
        except CommandParameterError:
            self._SendMessage(self.translator.GetSentence("PARAM_ERR_MSG"))
        else:
            try:
                kwargs["coin_info_scheduler"].Resume(self.cmd_data.Chat(), coin_id, coin_vs)
                self._SendMessage(
                    self.translator.GetSentence("PRICE_TASK_RESUME_OK_CMD",
                                                coin_id=coin_id,
                                                coin_vs=coin_vs)
                )
            except CoinInfoJobNotExistentError:
                self._SendMessage(
                    self.translator.GetSentence("TASK_NOT_EXISTENT_ERR_MSG",
                                                coin_id=coin_id,
                                                coin_vs=coin_vs)
                )


#
# Price task send in same message command
#
class PriceTaskSendInSameMsgCmd(CommandBase):
    # Execute command
    @GroupChatOnly
    def _ExecuteCommand(self,
                        **kwargs: Any) -> None:
        # Get parameters
        try:
            coin_id = self.cmd_data.Params().GetAsString(0)
            coin_vs = self.cmd_data.Params().GetAsString(1)
            flag = self.cmd_data.Params().GetAsBool(2)
        except CommandParameterError:
            self._SendMessage(self.translator.GetSentence("PARAM_ERR_MSG"))
        else:
            try:
                kwargs["coin_info_scheduler"].SendInSameMessage(self.cmd_data.Chat(), coin_id, coin_vs, flag)
                self._SendMessage(
                    self.translator.GetSentence("PRICE_TASK_SEND_IN_SAME_MSG_OK_CMD",
                                                coin_id=coin_id,
                                                coin_vs=coin_vs,
                                                flag=flag)
                )
            except CoinInfoJobNotExistentError:
                self._SendMessage(
                    self.translator.GetSentence("TASK_NOT_EXISTENT_ERR_MSG",
                                                coin_id=coin_id,
                                                coin_vs=coin_vs)
                )


#
# Price task delete last message command
#
class PriceTaskDeleteLastMsgCmd(CommandBase):
    # Execute command
    @GroupChatOnly
    def _ExecuteCommand(self,
                        **kwargs: Any) -> None:
        # Get parameters
        try:
            coin_id = self.cmd_data.Params().GetAsString(0)
            coin_vs = self.cmd_data.Params().GetAsString(1)
            flag = self.cmd_data.Params().GetAsBool(2)
        except CommandParameterError:
            self._SendMessage(self.translator.GetSentence("PARAM_ERR_MSG"))
        else:
            try:
                kwargs["coin_info_scheduler"].DeleteLastSentMessage(self.cmd_data.Chat(), coin_id, coin_vs, flag)
                self._SendMessage(
                    self.translator.GetSentence("PRICE_TASK_DELETE_LAST_MSG_OK_CMD",
                                                coin_id=coin_id,
                                                coin_vs=coin_vs,
                                                flag=flag)
                )
            except CoinInfoJobNotExistentError:
                self._SendMessage(
                    self.translator.GetSentence("TASK_NOT_EXISTENT_ERR_MSG",
                                                coin_id=coin_id,
                                                coin_vs=coin_vs)
                )


#
# Price task info command
#
class PriceTaskInfoCmd(CommandBase):
    # Execute command
    @GroupChatOnly
    def _ExecuteCommand(self,
                        **kwargs: Any) -> None:
        jobs_list = kwargs["coin_info_scheduler"].GetJobsInChat(self.cmd_data.Chat())

        if jobs_list.Any():
            self._SendMessage(
                self.translator.GetSentence("PRICE_TASK_INFO_CMD",
                                            tasks_num=jobs_list.Count(),
                                            tasks_list=str(jobs_list))
            )
        else:
            self._SendMessage(self.translator.GetSentence("PRICE_TASK_INFO_NO_TASK_CMD"))
