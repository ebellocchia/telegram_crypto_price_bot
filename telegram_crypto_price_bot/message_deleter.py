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
import pyrogram.errors.exceptions as pyrogram_ex
from typing import List
from telegram_crypto_price_bot.logger import Logger


#
# Classes
#

# Message deleter class
class MessageDeleter:

    client: pyrogram.Client
    logger: Logger

    # Constructor
    def __init__(self,
                 client: pyrogram.Client,
                 logger: Logger) -> None:
        self.client = client
        self.logger = logger

    # Delete message
    def DeleteMessage(self,
                      message: pyrogram.types.Message) -> bool:
        try:
            self.client.delete_messages(message.chat.id, message.message_id)
            return True
        except pyrogram_ex.forbidden_403.MessageDeleteForbidden:
            self.logger.GetLogger().exception(f"Unable to delete message {message.message_id}")
            return False

    # Delete messages
    def DeleteMessages(self,
                       messages: List[pyrogram.types.Message]) -> None:
        for message in messages:
            self.DeleteMessage(message)
