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

from typing import Any, Callable, Coroutine

from telegram_crypto_price_bot._version import __version__
from telegram_crypto_price_bot.bot.bot_config_types import BotConfigTypes
from telegram_crypto_price_bot.coin_info.coin_info_scheduler import (
    CoinInfoJobAlreadyExistentError,
    CoinInfoJobInvalidPeriodError,
    CoinInfoJobInvalidStartError,
    CoinInfoJobMaxNumError,
    CoinInfoJobNotExistentError,
)
from telegram_crypto_price_bot.command.command_base import CommandBase
from telegram_crypto_price_bot.command.command_data import CommandParameterError
from telegram_crypto_price_bot.info_message_sender.coin_info_message_sender import CoinInfoMessageSender
from telegram_crypto_price_bot.misc.helpers import UserHelper


def GroupChatOnly(exec_cmd_fct: Callable[..., Coroutine[Any, Any, None]]) -> Callable[..., Coroutine[Any, Any, None]]:
    """Decorator to restrict commands to group chats only.

    Args:
        exec_cmd_fct: Command execution function to decorate

    Returns:
        Decorated function that checks for group chat before execution
    """

    async def decorated(self: Any, **kwargs: Any) -> None:
        if self._IsPrivateChat():
            await self._SendMessage(self.translator.GetSentence("GROUP_ONLY_ERR_MSG"))
        else:
            await exec_cmd_fct(self, **kwargs)

    return decorated


class HelpCmd(CommandBase):
    """Command to display help information."""

    async def _ExecuteCommand(self,
                              **kwargs: Any) -> None:
        """Execute the help command."""
        await self._SendMessage(self.translator.GetSentence("HELP_CMD", name=UserHelper.GetName(self.cmd_data.User())))


class AliveCmd(CommandBase):
    """Command to check if the bot is alive and responding."""

    async def _ExecuteCommand(self,
                              **kwargs: Any) -> None:
        """Execute the alive command."""
        await self._SendMessage(self.translator.GetSentence("ALIVE_CMD"))


class SetTestModeCmd(CommandBase):
    """Command to enable or disable test mode."""

    @GroupChatOnly
    async def _ExecuteCommand(self,
                              **kwargs: Any) -> None:
        """Execute the set test mode command."""
        try:
            flag = self.cmd_data.Params().GetAsBool(0)
        except CommandParameterError:
            await self._SendMessage(self.translator.GetSentence("PARAM_ERR_MSG"))
        else:
            self.config.SetValue(BotConfigTypes.APP_TEST_MODE, flag)

            if self.config.GetValue(BotConfigTypes.APP_TEST_MODE):
                await self._SendMessage(self.translator.GetSentence("SET_TEST_MODE_EN_CMD"))
            else:
                await self._SendMessage(self.translator.GetSentence("SET_TEST_MODE_DIS_CMD"))


class IsTestModeCmd(CommandBase):
    """Command to check if test mode is enabled."""

    async def _ExecuteCommand(self,
                              **kwargs: Any) -> None:
        """Execute the is test mode command."""
        if self.config.GetValue(BotConfigTypes.APP_TEST_MODE):
            await self._SendMessage(self.translator.GetSentence("IS_TEST_MODE_EN_CMD"))
        else:
            await self._SendMessage(self.translator.GetSentence("IS_TEST_MODE_DIS_CMD"))


class VersionCmd(CommandBase):
    """Command to display bot version."""

    async def _ExecuteCommand(self,
                              **kwargs: Any) -> None:
        """Execute the version command."""
        await self._SendMessage(self.translator.GetSentence("VERSION_CMD", version=__version__))


class PriceGetSingleCmd(CommandBase):
    """Command to get cryptocurrency price information once."""

    @GroupChatOnly
    async def _ExecuteCommand(self,
                              **kwargs: Any) -> None:
        """Execute the get single price command."""
        try:
            coin_id = self.cmd_data.Params().GetAsString(0)
            coin_vs = self.cmd_data.Params().GetAsString(1)
            last_days = self.cmd_data.Params().GetAsInt(2)
            same_msg = self.cmd_data.Params().GetAsBool(3, True)
        except CommandParameterError:
            await self._SendMessage(self.translator.GetSentence("PARAM_ERR_MSG"))
        else:
            coin_info_sender = CoinInfoMessageSender(self.client, self.config, self.logger, self.translator)
            coin_info_sender.SendInSameMessage(same_msg)
            await coin_info_sender.SendMessage(self.cmd_data.Chat(), self.message.message_thread_id, coin_id, coin_vs, last_days)


class PriceTaskStartCmd(CommandBase):
    """Command to start a scheduled cryptocurrency price task."""

    @GroupChatOnly
    async def _ExecuteCommand(self,
                              **kwargs: Any) -> None:
        """Execute the price task start command."""
        try:
            period_hours = self.cmd_data.Params().GetAsInt(0)
            start_hour = self.cmd_data.Params().GetAsInt(1)
            coin_id = self.cmd_data.Params().GetAsString(2)
            coin_vs = self.cmd_data.Params().GetAsString(3)
            last_days = self.cmd_data.Params().GetAsInt(4)
        except CommandParameterError:
            await self._SendMessage(self.translator.GetSentence("PARAM_ERR_MSG"))
        else:
            try:
                kwargs["coin_info_scheduler"].Start(self.cmd_data.Chat(),
                                                    self.message.message_thread_id,
                                                    period_hours,
                                                    start_hour,
                                                    coin_id,
                                                    coin_vs,
                                                    last_days)
                await self._SendMessage(
                    self.translator.GetSentence(
                        "PRICE_TASK_START_OK_CMD",
                        period=period_hours,
                        start=start_hour,
                        coin_id=coin_id,
                        coin_vs=coin_vs,
                        last_days=last_days,
                    )
                )
            except CoinInfoJobInvalidPeriodError:
                await self._SendMessage(self.translator.GetSentence("TASK_PERIOD_ERR_MSG"))
            except CoinInfoJobInvalidStartError:
                await self._SendMessage(self.translator.GetSentence("TASK_START_ERR_MSG"))
            except CoinInfoJobMaxNumError:
                await self._SendMessage(self.translator.GetSentence("MAX_TASK_ERR_MSG"))
            except CoinInfoJobAlreadyExistentError:
                await self._SendMessage(self.translator.GetSentence("TASK_EXISTENT_ERR_MSG", coin_id=coin_id, coin_vs=coin_vs))


class PriceTaskStopCmd(CommandBase):
    """Command to stop a scheduled cryptocurrency price task."""

    @GroupChatOnly
    async def _ExecuteCommand(self,
                              **kwargs: Any) -> None:
        """Execute the price task stop command."""
        try:
            coin_id = self.cmd_data.Params().GetAsString(0)
            coin_vs = self.cmd_data.Params().GetAsString(1)
        except CommandParameterError:
            await self._SendMessage(self.translator.GetSentence("PARAM_ERR_MSG"))
        else:
            try:
                kwargs["coin_info_scheduler"].Stop(self.cmd_data.Chat(), self.message.message_thread_id, coin_id, coin_vs)
                await self._SendMessage(self.translator.GetSentence("PRICE_TASK_STOP_OK_CMD", coin_id=coin_id, coin_vs=coin_vs))
            except CoinInfoJobNotExistentError:
                await self._SendMessage(self.translator.GetSentence("TASK_NOT_EXISTENT_ERR_MSG", coin_id=coin_id, coin_vs=coin_vs))


class PriceTaskStopAllCmd(CommandBase):
    """Command to stop all scheduled cryptocurrency price tasks in a chat."""

    @GroupChatOnly
    async def _ExecuteCommand(self,
                              **kwargs: Any) -> None:
        """Execute the price task stop all command."""
        kwargs["coin_info_scheduler"].StopAll(self.cmd_data.Chat())
        await self._SendMessage(self.translator.GetSentence("PRICE_TASK_STOP_ALL_CMD"))


class PriceTaskPauseCmd(CommandBase):
    """Command to pause a scheduled cryptocurrency price task."""

    @GroupChatOnly
    async def _ExecuteCommand(self,
                              **kwargs: Any) -> None:
        """Execute the price task pause command."""
        try:
            coin_id = self.cmd_data.Params().GetAsString(0)
            coin_vs = self.cmd_data.Params().GetAsString(1)
        except CommandParameterError:
            await self._SendMessage(self.translator.GetSentence("PARAM_ERR_MSG"))
        else:
            try:
                kwargs["coin_info_scheduler"].Pause(self.cmd_data.Chat(), self.message.message_thread_id, coin_id, coin_vs)
                await self._SendMessage(self.translator.GetSentence("PRICE_TASK_PAUSE_OK_CMD", coin_id=coin_id, coin_vs=coin_vs))
            except CoinInfoJobNotExistentError:
                await self._SendMessage(self.translator.GetSentence("TASK_NOT_EXISTENT_ERR_MSG", coin_id=coin_id, coin_vs=coin_vs))


class PriceTaskResumeCmd(CommandBase):
    """Command to resume a paused cryptocurrency price task."""

    @GroupChatOnly
    async def _ExecuteCommand(self,
                              **kwargs: Any) -> None:
        """Execute the price task resume command."""
        try:
            coin_id = self.cmd_data.Params().GetAsString(0)
            coin_vs = self.cmd_data.Params().GetAsString(1)
        except CommandParameterError:
            await self._SendMessage(self.translator.GetSentence("PARAM_ERR_MSG"))
        else:
            try:
                kwargs["coin_info_scheduler"].Resume(self.cmd_data.Chat(), self.message.message_thread_id, coin_id, coin_vs)
                await self._SendMessage(self.translator.GetSentence("PRICE_TASK_RESUME_OK_CMD", coin_id=coin_id, coin_vs=coin_vs))
            except CoinInfoJobNotExistentError:
                await self._SendMessage(self.translator.GetSentence("TASK_NOT_EXISTENT_ERR_MSG", coin_id=coin_id, coin_vs=coin_vs))


class PriceTaskSendInSameMsgCmd(CommandBase):
    """Command to configure whether task updates are sent in the same message."""

    @GroupChatOnly
    async def _ExecuteCommand(self,
                              **kwargs: Any) -> None:
        """Execute the price task send in same message command."""
        try:
            coin_id = self.cmd_data.Params().GetAsString(0)
            coin_vs = self.cmd_data.Params().GetAsString(1)
            flag = self.cmd_data.Params().GetAsBool(2)
        except CommandParameterError:
            await self._SendMessage(self.translator.GetSentence("PARAM_ERR_MSG"))
        else:
            try:
                kwargs["coin_info_scheduler"].SendInSameMessage(self.cmd_data.Chat(),
                                                                self.message.message_thread_id,
                                                                coin_id,
                                                                coin_vs,
                                                                flag)
                await self._SendMessage(
                    self.translator.GetSentence("PRICE_TASK_SEND_IN_SAME_MSG_OK_CMD", coin_id=coin_id, coin_vs=coin_vs, flag=flag)
                )
            except CoinInfoJobNotExistentError:
                await self._SendMessage(self.translator.GetSentence("TASK_NOT_EXISTENT_ERR_MSG", coin_id=coin_id, coin_vs=coin_vs))


class PriceTaskDeleteLastMsgCmd(CommandBase):
    """Command to configure whether the last sent message should be deleted."""

    @GroupChatOnly
    async def _ExecuteCommand(self,
                              **kwargs: Any) -> None:
        """Execute the price task delete last message command."""
        try:
            coin_id = self.cmd_data.Params().GetAsString(0)
            coin_vs = self.cmd_data.Params().GetAsString(1)
            flag = self.cmd_data.Params().GetAsBool(2)
        except CommandParameterError:
            await self._SendMessage(self.translator.GetSentence("PARAM_ERR_MSG"))
        else:
            try:
                kwargs["coin_info_scheduler"].DeleteLastSentMessage(self.cmd_data.Chat(),
                                                                    self.message.message_thread_id,
                                                                    coin_id,
                                                                    coin_vs,
                                                                    flag)
                await self._SendMessage(
                    self.translator.GetSentence("PRICE_TASK_DELETE_LAST_MSG_OK_CMD", coin_id=coin_id, coin_vs=coin_vs, flag=flag)
                )
            except CoinInfoJobNotExistentError:
                await self._SendMessage(self.translator.GetSentence("TASK_NOT_EXISTENT_ERR_MSG", coin_id=coin_id, coin_vs=coin_vs))


class PriceTaskInfoCmd(CommandBase):
    """Command to display information about active price tasks in a chat."""

    @GroupChatOnly
    async def _ExecuteCommand(self,
                              **kwargs: Any) -> None:
        """Execute the price task info command."""
        jobs_list = kwargs["coin_info_scheduler"].GetJobsInChat(self.cmd_data.Chat())

        if jobs_list.Any():
            await self._SendMessage(
                self.translator.GetSentence("PRICE_TASK_INFO_CMD", tasks_num=jobs_list.Count(), tasks_list=str(jobs_list))
            )
        else:
            await self._SendMessage(self.translator.GetSentence("PRICE_TASK_INFO_NO_TASK_CMD"))
