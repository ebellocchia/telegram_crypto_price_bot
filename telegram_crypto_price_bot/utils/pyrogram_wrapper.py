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

from typing import Iterator

import pyrogram

from telegram_crypto_price_bot.utils.utils import Utils


if int(pyrogram.__version__[0]) == 2:
    from pyrogram.enums import ChatMembersFilter, ChatType
else:
    from enum import Enum

    class ChatMembersFilter(Enum):  # type: ignore
        """Fake enum for backward compatibility with Pyrogram v1."""
        pass


class PyrogramWrapper:
    """Wrapper for Pyrogram to handle different versions (v1 and v2)."""

    @staticmethod
    def MessageId(message: pyrogram.types.Message) -> int:
        """Get the message ID from a Pyrogram message object.

        Args:
            message: Pyrogram message object

        Returns:
            Message ID

        Raises:
            RuntimeError: If Pyrogram version is not supported
        """
        if PyrogramWrapper.__Version() == 2:
            return message.id
        if PyrogramWrapper.__Version() == 1:
            return message.message_id
        raise RuntimeError("Unsupported pyrogram version")

    @staticmethod
    def IsChannel(chat: pyrogram.types.Chat) -> bool:
        """Check if a chat is a channel.

        Args:
            chat: Pyrogram chat object

        Returns:
            True if the chat is a channel, False otherwise

        Raises:
            RuntimeError: If Pyrogram version is not supported
        """
        if PyrogramWrapper.__Version() == 2:
            return chat.type == ChatType.CHANNEL
        if PyrogramWrapper.__Version() == 1:
            return chat["type"] == "channel"
        raise RuntimeError("Unsupported pyrogram version")

    @staticmethod
    def GetChatMembers(client: pyrogram.Client,
                       chat: pyrogram.types.Chat,
                       filter_str: str) -> Iterator[pyrogram.types.ChatMember]:
        """Get chat members with the specified filter.

        Args:
            client: Pyrogram client instance
            chat: Pyrogram chat object
            filter_str: Filter string (e.g., "all", "banned", "bots", "restricted", "administrators")

        Returns:
            Iterator of chat members

        Raises:
            RuntimeError: If Pyrogram version is not supported
        """
        if PyrogramWrapper.__Version() == 2:
            return client.get_chat_members(chat.id, filter=PyrogramWrapper.__StrToChatMembersFilter(filter_str))
        if PyrogramWrapper.__Version() == 1:
            return client.iter_chat_members(chat.id, filter=filter_str)
        raise RuntimeError("Unsupported pyrogram version")

    @staticmethod
    def __StrToChatMembersFilter(filter_str: str) -> ChatMembersFilter:
        """Convert a filter string to ChatMembersFilter enum.

        Args:
            filter_str: Filter string

        Returns:
            ChatMembersFilter enum value
        """
        str_to_enum = {
            "all": ChatMembersFilter.SEARCH,
            "banned": ChatMembersFilter.BANNED,
            "bots": ChatMembersFilter.BOTS,
            "restricted": ChatMembersFilter.RESTRICTED,
            "administrators": ChatMembersFilter.ADMINISTRATORS,
        }

        return str_to_enum[filter_str]

    @staticmethod
    def __Version() -> int:
        """Get the Pyrogram major version number.

        Returns:
            Pyrogram major version as an integer
        """
        return Utils.StrToInt(pyrogram.__version__[0])
