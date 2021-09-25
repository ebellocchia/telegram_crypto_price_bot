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
from typing import Any, Callable, Optional, Union
from telegram_crypto_price_bot.utils import Utils
from telegram_crypto_price_bot.wrapped_list import WrappedList


#
# Classes
#

# Command parameter error class
class CommandParameterError(Exception):
    pass


# Command parameters list class
class CommandParametersList(WrappedList):
    # Get parameter as bool
    def GetAsBool(self,
                  idx: int,
                  def_val: Optional[bool] = None) -> bool:
        return self.__GetGenericParam(Utils.StrToBool, idx, def_val)

    # Get parameter as int
    def GetAsInt(self,
                 idx: int,
                 def_val: Optional[int] = None) -> int:
        return self.__GetGenericParam(Utils.StrToInt, idx, def_val)

    # Get parameter as string
    def GetAsString(self,
                    idx: int,
                    def_val: Optional[str] = None) -> str:
        return self.__GetGenericParam(str, idx, def_val)

    # Check if last parameter is the specified value
    def IsLast(self,
               value: Union[int, str]) -> bool:
        try:
            return value == self.list_elements[self.Count() - 1]
        except IndexError:
            return False

    # Check if value is present
    def IsValue(self,
                value: Union[int, str]) -> bool:
        return value in self.list_elements

    # Get generic parameter
    def __GetGenericParam(self,
                          conv_fct: Callable[[str], Any],
                          idx: int,
                          def_val: Optional[Any]) -> Any:
        try:
            return conv_fct(self.list_elements[idx])
        except (ValueError, IndexError):
            if def_val is not None:
                return def_val
            else:
                raise CommandParameterError(f"Invalid command parameter #{idx}")


# Command data
class CommandData:
    def __init__(self,
                 message: pyrogram.types.Message) -> None:
        self.cmd_name = message.command[0]
        self.cmd_params = CommandParametersList()
        self.cmd_params.AddMultiple(message.command[1:])
        self.cmd_chat = message.chat
        self.cmd_user = message.from_user

    # Get name
    def Name(self) -> str:
        return self.cmd_name

    # Get chat
    def Chat(self) -> pyrogram.types.Chat:
        return self.cmd_chat

    # Get user
    def User(self) -> pyrogram.types.User:
        return self.cmd_user

    # Get parameters
    def Params(self) -> CommandParametersList:
        return self.cmd_params
