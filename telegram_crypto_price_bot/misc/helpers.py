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

from typing import Optional

import pyrogram
from pyrogram.enums import ChatType


class ChatHelper:
    """Helper class for Telegram chat operations."""

    @staticmethod
    def IsChannel(chat: pyrogram.types.Chat) -> bool:
        """Check if the chat is a channel.

        Args:
            chat: Chat object to check

        Returns:
            True if chat is a channel, False otherwise
        """
        return chat.type == ChatType.CHANNEL

    @staticmethod
    def GetTitle(chat: pyrogram.types.Chat) -> str:
        """Get the chat title.

        Args:
            chat: Chat object to get title from

        Returns:
            Chat title or empty string if no title
        """
        return chat.title if chat.title is not None else ""

    @staticmethod
    def GetTitleOrId(chat: pyrogram.types.Chat) -> str:
        """Get the chat title with ID or just ID if no title.

        Args:
            chat: Chat object to get information from

        Returns:
            Chat title with ID or just ID
        """
        return f"'{chat.title}' (ID: {chat.id})" if chat.title is not None else f"{chat.id}"

    @staticmethod
    def IsPrivateChat(chat: pyrogram.types.Chat,
                      user: pyrogram.types.User):
        """Check if the chat is a private chat with the user.

        Args:
            chat: Chat object to check
            user: User object to compare with

        Returns:
            True if chat is private with the user, False otherwise
        """
        if ChatHelper.IsChannel(chat):
            return False
        return chat.id == user.id


class UserHelper:
    """Helper class for Telegram user operations."""

    @staticmethod
    def GetNameOrId(user: Optional[pyrogram.types.User]) -> str:
        """Get user's name or ID with username if available.

        Args:
            user: User object to get information from, or None

        Returns:
            User information string with name, username, and ID
        """
        if user is None:
            return "Anonymous user"

        if user.username is not None:
            return f"@{user.username} ({UserHelper.GetName(user)} - ID: {user.id})"

        name = UserHelper.GetName(user)
        return f"{name} (ID: {user.id})" if name is not None else f"ID: {user.id}"

    @staticmethod
    def GetName(user: Optional[pyrogram.types.User]) -> str:
        """Get user's full name.

        Args:
            user: User object to get name from, or None

        Returns:
            User's full name or "Anonymous user" if None
        """
        if user is None:
            return "Anonymous user"

        if user.first_name is not None:
            return f"{user.first_name} {user.last_name}" if user.last_name is not None else f"{user.first_name}"
        return user.last_name if user.last_name is not None else ""
