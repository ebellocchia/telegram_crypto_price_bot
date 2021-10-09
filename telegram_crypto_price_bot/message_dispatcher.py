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
from typing import Any
from telegram_crypto_price_bot.config import Config
from telegram_crypto_price_bot.logger import Logger
from telegram_crypto_price_bot.message_sender import MessageSender
from telegram_crypto_price_bot.translation_loader import TranslationLoader


#
# Classes
#

# Message dispatcher class
class MessageDispatcher:

    config: Config
    logger: Logger
    translator: TranslationLoader

    # Constructor
    def __init__(self,
                 config: Config,
                 logger: Logger,
                 translator: TranslationLoader) -> None:
        self.config = config
        self.logger = logger
        self.translator = translator

    # Dispatch command
    def Dispatch(self,
                 client: pyrogram.Client,
                 message: pyrogram.types.Message,
                 **kwargs: Any) -> None:
        # New chat created
        if message.group_chat_created is not None:
            self.__OnCreatedChat(client, message, **kwargs)
        # A member left the chat
        if message.left_chat_member is not None:
            self.__OnLeftMember(client, message, **kwargs)
        # A member joined the chat
        if message.new_chat_members is not None:
            self.__OnJoinedMember(client, message, **kwargs)

    # Function called when a new chat is created
    def __OnCreatedChat(self,
                        client,
                        message: pyrogram.types.Message,
                        **kwargs: Any) -> None:
        # Send the welcome message
        MessageSender(client, self.config, self.logger).SendMessage(
            message.chat,
            self.translator.GetSentence("BOT_WELCOME_MSG")
        )

    # Function called when a member left the chat
    def __OnLeftMember(self,
                       client,
                       message: pyrogram.types.Message,
                       **kwargs: Any) -> None:
        # If the member is the bot itself, remove the chat from the scheduler
        if message.left_chat_member.is_self:
            kwargs["coin_info_scheduler"].ChatLeft(message.chat)

    # Function called when a member joined the chat
    def __OnJoinedMember(self,
                         client,
                         message: pyrogram.types.Message,
                         **kwargs: Any) -> None:
        # If the member is the bot itself, send the welcome message
        for member in message.new_chat_members:
            if member.is_self:
                MessageSender(client, self.config, self.logger).SendMessage(
                    message.chat,
                    self.translator.GetSentence("BOT_WELCOME_MSG")
                )
                break
