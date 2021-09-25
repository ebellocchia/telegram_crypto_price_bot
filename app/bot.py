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
import getopt
import sys
from typing import List
from telegram_crypto_price_bot import PriceBot, __version__

#
# Variables
#

# Default configuration file
DEF_CONFIG_FILE = "conf/config.ini"


#
# Classes
#

#
# Arguments
#
class Arguments:
    # Constructor
    def __init__(self) -> None:
        self.config_file = DEF_CONFIG_FILE

    # Get configuration file
    def GetConfigFile(self) -> str:
        return self.config_file

    # Set configuration file
    def SetConfigFile(self, config_file: str) -> None:
        self.config_file = config_file


#
# Argument parser
#
class ArgumentsParser:
    # Constructor
    def __init__(self) -> None:
        self.args = Arguments()

    # Parse arguments
    def Parse(self, argv: List[str]) -> None:
        # Parse arguments
        try:
            opts, _ = getopt.getopt(argv[1:], "c:", ["config="])
        # Handle error
        except getopt.GetoptError:
            return

        # Get arguments
        for opt, arg in opts:
            if opt in ("-c", "--config"):
                self.args.SetConfigFile(arg)

    # Get arguments
    def GetArgs(self) -> Arguments:
        return self.args


#
# Functions
#

# Print header
def print_header() -> None:
    print("")
    print("***********************************")
    print("****                           ****")
    print("***                             ***")
    print("**                               **")
    print("*    Telegram Crypto Price Bot    *")
    print("*   Author: Emanuele Bellocchia   *")
    print("*         Version: %s          *" % __version__)
    print("**                               **")
    print("***                             ***")
    print("****                           ****")
    print("***********************************")
    print("")


#
# Main
#
if __name__ == "__main__":
    # Print header
    print_header()

    # Get arguments
    args_parser = ArgumentsParser()
    args_parser.Parse(sys.argv)

    # Create and run bot
    price_bot = PriceBot(args_parser.GetArgs().GetConfigFile())
    price_bot.Run()
