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

from telegram_crypto_price_bot.config.config_loader_ex import ConfigFieldNotExistentError, ConfigFieldValueError
from telegram_crypto_price_bot.config.config_object import ConfigObject
from telegram_crypto_price_bot.config.config_typing import ConfigFieldType, ConfigSectionType


#
# Classes
#

# Configuration section loader class
class ConfigSectionLoader:

    config_parser: configparser.ConfigParser

    # Constructor
    def __init__(self,
                 config_parser: configparser.ConfigParser) -> None:
        self.config_parser = config_parser

    # Load section
    def LoadSection(self,
                    config_obj: ConfigObject,
                    section_name: str,
                    section: ConfigSectionType) -> None:
        # For each field
        for field in section:
            # Load if needed
            if self.__FieldShallBeLoaded(config_obj, field):
                # Set field value and print it
                self.__SetFieldValue(config_obj, section_name, field)
                self.__PrintFieldValue(config_obj, field)
            # Otherwise set the default value
            elif "def_val" in field:
                config_obj.SetValue(field["type"], field["def_val"])

    # Get if field shall be loaded
    @staticmethod
    def __FieldShallBeLoaded(config_obj: ConfigObject,
                             field: ConfigFieldType) -> bool:
        return field["load_if"](config_obj) if "load_if" in field else True

    # Set field value
    def __SetFieldValue(self,
                        config_obj: ConfigObject,
                        section: str,
                        field: ConfigFieldType) -> None:
        try:
            field_val = self.config_parser[section][field["name"]]
        # Field not present, set default value if specified
        except KeyError as ex:
            if "def_val" not in field:
                raise ConfigFieldNotExistentError(f"Configuration field \"{field['name']}\" not found") from ex
            field_val = field["def_val"]
        else:
            # Convert value if needed
            if "conv_fct" in field:
                field_val = field["conv_fct"](field_val)

        # Validate value if needed
        if "valid_if" in field and not field["valid_if"](config_obj, field_val):
            raise ConfigFieldValueError(f"Value '{field_val}' is not valid for field \"{field['name']}\"")

        # Set value
        config_obj.SetValue(field["type"], field_val)

    # Print field value
    @staticmethod
    def __PrintFieldValue(config_obj: ConfigObject,
                          field: ConfigFieldType) -> None:
        if "print_fct" in field:
            print(f"- {field['name']}: {field['print_fct'](config_obj.GetValue(field['type']))}")
        else:
            print(f"- {field['name']}: {config_obj.GetValue(field['type'])}")
