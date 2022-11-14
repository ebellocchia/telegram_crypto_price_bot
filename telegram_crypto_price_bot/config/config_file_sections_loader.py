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
import configparser

from telegram_crypto_price_bot.config.config_object import ConfigObject
from telegram_crypto_price_bot.config.config_sections_loader import ConfigSectionsLoader
from telegram_crypto_price_bot.config.config_typing import ConfigSectionsType


#
# Classes
#

# Configuration file sections loader class
class ConfigFileSectionsLoader:
    # Load
    @staticmethod
    def Load(file_name: str,
             sections: ConfigSectionsType) -> ConfigObject:
        print(f"\nLoading configuration file {file_name}...\n")

        # Read file
        config_parser = configparser.ConfigParser()
        config_parser.read(file_name, encoding="utf-8")

        # Load sections
        return ConfigSectionsLoader(config_parser).LoadSections(sections)
