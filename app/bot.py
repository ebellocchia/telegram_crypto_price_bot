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
import argparse

from telegram_crypto_price_bot import PriceBot, __version__


#
# Variables
#

# Default configuration file
DEF_CONFIG_FILE = "conf/config.ini"


#
# Classes
#

# Argument parser
class ArgumentsParser:

    parser: argparse.ArgumentParser

    # Constructor
    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument(
            "-c", "--config",
            type=str,
            default=DEF_CONFIG_FILE,
            help="configuration file"
        )

    # Parse arguments
    def Parse(self) -> argparse.Namespace:
        return self.parser.parse_args()


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
    args = args_parser.Parse()

    # Create and run bot
    bot = PriceBot(args.config)
    bot.Run()
