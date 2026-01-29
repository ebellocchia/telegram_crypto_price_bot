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

import time
from typing import Any, List, Union

import pyrogram

from telegram_crypto_price_bot.logger.logger import Logger


class MessageSenderConst:
    """Constants for message sender configuration."""

    MSG_MAX_LEN: int = 4096
    SEND_MSG_SLEEP_TIME_SEC: float = 0.1


class MessageSender:
    """Class for sending Telegram messages with automatic splitting."""

    client: pyrogram.Client
    logger: Logger

    def __init__(self,
                 client: pyrogram.Client,
                 logger: Logger) -> None:
        """Initialize the message sender.

        Args:
            client: Pyrogram client instance
            logger: Logger instance
        """
        self.client = client
        self.logger = logger

    def SendMessage(self,
                    receiver: Union[pyrogram.types.Chat, pyrogram.types.User],
                    topic_id: int,
                    msg: str,
                    **kwargs: Any) -> List[pyrogram.types.Message]:
        """Send a message, automatically splitting if it exceeds maximum length.

        Args:
            receiver: Chat or user to send message to
            topic_id: Topic to send message to
            msg: Message text to send
            **kwargs: Additional keyword arguments

        Returns:
            List of sent message objects
        """
        self.logger.GetLogger().info(f"Sending message (length: {len(msg)}):\n{msg}")
        return self.__SendSplitMessage(receiver, topic_id, self.__SplitMessage(msg), **kwargs)

    def SendPhoto(self,
                  receiver: Union[pyrogram.types.Chat, pyrogram.types.User],
                  topic_id: int,
                  photo: str,
                  **kwargs: Any) -> pyrogram.types.Message:
        """Send a photo message.

        Args:
            receiver: Chat or user to send photo to
            topic_id: Topic to send photo to
            photo: Path to photo file
            **kwargs: Additional keyword arguments

        Returns:
            Sent message object
        """
        return self.client.send_photo(receiver.id, photo, message_thread_id=topic_id, **kwargs)     # type: ignore

    def __SendSplitMessage(self,
                           receiver: Union[pyrogram.types.Chat, pyrogram.types.User],
                           topic_id: int,
                           split_msg: List[str],
                           **kwargs) -> List[pyrogram.types.Message]:
        """Send multiple message parts with delay between sends.

        Args:
            receiver: Chat or user to send messages to
            topic_id: Topic to send messages to
            split_msg: List of message parts to send
            **kwargs: Additional keyword arguments

        Returns:
            List of sent message objects
        """
        sent_msgs = []

        for msg_part in split_msg:
            sent_msgs.append(
                self.client.send_message(receiver.id, msg_part, message_thread_id=topic_id, **kwargs)
            )
            time.sleep(MessageSenderConst.SEND_MSG_SLEEP_TIME_SEC)

        return sent_msgs    # type: ignore

    def __SplitMessage(self,
                       msg: str) -> List[str]:
        """Split a message into parts respecting maximum length.

        Args:
            msg: Message to split

        Returns:
            List of message parts
        """
        msg_parts = []

        while len(msg) > 0:
            if len(msg) <= MessageSenderConst.MSG_MAX_LEN:
                msg_parts.append(msg)
                break

            curr_part = msg[:MessageSenderConst.MSG_MAX_LEN]
            idx = curr_part.rfind("\n")

            if idx != -1:
                msg_parts.append(curr_part[:idx])
                msg = msg[idx + 1:]
            else:
                msg_parts.append(curr_part)
                msg = msg[MessageSenderConst.MSG_MAX_LEN + 1:]

        self.logger.GetLogger().info(f"Message split into {len(msg_parts)} part(s)")

        return msg_parts
