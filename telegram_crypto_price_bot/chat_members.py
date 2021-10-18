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
from typing import Callable, Optional
from telegram_crypto_price_bot.config import Config
from telegram_crypto_price_bot.helpers import UserHelper
from telegram_crypto_price_bot.wrapped_list import WrappedList


#
# Classes
#

# Chat members list class
class ChatMembersList(WrappedList):
    # Get by ID
    def GetById(self,
                user_id: int) -> Optional[pyrogram.types.ChatMember]:
        res = [member for member in self.list_elements if user_id == member.user.id]
        return res[0] if len(res) > 0 else None

    # Get by username
    def GetByUsername(self,
                      username: str) -> Optional[pyrogram.types.ChatMember]:
        res = [member for member in self.list_elements if username == member.user.username]
        return res[0] if len(res) > 0 else None

    # Get if ID is present
    def IsUsernameId(self,
                     user_id: int) -> bool:
        return self.GetById(user_id) is not None

    # Get if username is present
    def IsUsernamePresent(self,
                          username: str) -> bool:
        return self.GetByUsername(username) is not None

    # Convert to string
    def ToString(self) -> str:
        return "\n".join(
            [f"- {UserHelper.GetNameOrId(member.user)}" for member in self.list_elements]
        )

    # Convert to string
    def __str__(self) -> str:
        return self.ToString()


# Chat members getter class
class ChatMembersGetter:

    client: pyrogram.Client
    config: Config

    # Constructor
    def __init__(self,
                 client: pyrogram.Client,
                 config: Config) -> None:
        self.client = client
        self.config = config

    # Get the list of chat members by applying the specified filter
    def FilterMembers(self,
                      chat: pyrogram.types.Chat,
                      filter_fct: Callable[[pyrogram.types.ChatMember], bool]) -> ChatMembersList:
        # Filter members
        filtered_members = [member for member in self.client.iter_chat_members(chat.id) if filter_fct(member)]
        # Order filtered members
        filtered_members.sort(
            key=lambda member: member.user.username.lower() if member.user.username is not None else str(member.user.id))

        # Build chat members
        chat_members = ChatMembersList()
        chat_members.AddMultiple(filtered_members)

        return chat_members

    # Get all
    def GetAll(self,
               chat: pyrogram.types.Chat) -> ChatMembersList:
        return self.FilterMembers(chat, lambda member: True)

    # Get admins
    def GetAdmins(self,
                  chat: pyrogram.types.Chat) -> ChatMembersList:
        return self.FilterMembers(chat,
                                  lambda member: member.status in ["administrator", "creator"])
