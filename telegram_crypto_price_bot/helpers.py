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
from typing import Optional


#
# Classes
#

# Chat helper class
class ChatHelper:
    # Get title
    @staticmethod
    def GetTitle(chat: pyrogram.types.Chat) -> str:
        return chat.title if chat.title is not None else ""

    # Get title or ID
    @staticmethod
    def GetTitleOrId(chat: pyrogram.types.Chat) -> str:
        return f"'{chat.title}' (ID: {chat.id})" if chat.title is not None else f"{chat.id}"

    # Get if private chat
    @staticmethod
    def IsPrivateChat(chat: pyrogram.types.Chat,
                      user: pyrogram.types.User):
        return chat.id == user.id


# User helper class
class UserHelper:
    # Get user name or ID
    @staticmethod
    def GetNameOrId(user: pyrogram.types.User) -> str:
        if user.username is not None:
            return f"@{user.username} ({UserHelper.GetName(user)} - ID: {user.id})"
        else:
            name = UserHelper.GetName(user)
            if name is not None:
                return f"{name} (ID: {user.id})"
            else:
                return f"ID: {user.id}"

    # Get user name
    @staticmethod
    def GetName(user: pyrogram.types.User) -> Optional[str]:
        if user.first_name is not None:
            if user.last_name is not None:
                return f"{user.first_name} {user.last_name}"
            else:
                return f"{user.first_name}"
        else:
            return user.last_name
