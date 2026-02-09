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

import configparser

from telegram_crypto_price_bot.config.config_loader_ex import ConfigFieldNotExistentError, ConfigFieldValueError
from telegram_crypto_price_bot.config.config_object import ConfigObject
from telegram_crypto_price_bot.config.config_typing import ConfigFieldType, ConfigSectionType


class ConfigSectionLoader:
    """Loader for a single configuration section."""

    config_parser: configparser.ConfigParser

    def __init__(self,
                 config_parser: configparser.ConfigParser) -> None:
        """
        Initialize the section loader.

        Args:
            config_parser: ConfigParser instance with loaded configuration.
        """
        self.config_parser = config_parser

    def LoadSection(self,
                    config_obj: ConfigObject,
                    section_name: str,
                    section: ConfigSectionType) -> None:
        """
        Load a configuration section and populate the configuration object.

        Args:
            config_obj: Configuration object to populate.
            section_name: Name of the section to load.
            section: Section configuration structure.
        """
        for field in section:
            if self.__FieldShallBeLoaded(config_obj, field):
                self.__SetFieldValue(config_obj, section_name, field)
                self.__PrintFieldValue(config_obj, field)
            elif "def_val" in field:
                config_obj.SetValue(field["type"], field["def_val"])

    @staticmethod
    def __FieldShallBeLoaded(config_obj: ConfigObject,
                             field: ConfigFieldType) -> bool:
        """
        Check if a field should be loaded based on conditions.

        Args:
            config_obj: Configuration object with current values.
            field: Field configuration.

        Returns:
            True if field should be loaded, False otherwise.
        """
        return field["load_if"](config_obj) if "load_if" in field else True

    def __SetFieldValue(self,
                        config_obj: ConfigObject,
                        section: str,
                        field: ConfigFieldType) -> None:
        """
        Set a field value in the configuration object.

        Args:
            config_obj: Configuration object to update.
            section: Section name containing the field.
            field: Field configuration.

        Raises:
            ConfigFieldNotExistentError: If required field is missing.
            ConfigFieldValueError: If field value is invalid.
        """
        try:
            field_val = self.config_parser[section][field["name"]]
        except KeyError as ex:
            if "def_val" not in field:
                raise ConfigFieldNotExistentError(f"Configuration field \"{field['name']}\" not found") from ex
            field_val = field["def_val"]
        else:
            if "conv_fct" in field:
                field_val = field["conv_fct"](field_val)

        if "valid_if" in field and not field["valid_if"](config_obj, field_val):
            raise ConfigFieldValueError(f"Value '{field_val}' is not valid for field \"{field['name']}\"")

        config_obj.SetValue(field["type"], field_val)

    @staticmethod
    def __PrintFieldValue(config_obj: ConfigObject,
                          field: ConfigFieldType) -> None:
        """
        Print a field value to the console.

        Args:
            config_obj: Configuration object containing the field value.
            field: Field configuration.
        """
        if "print_fct" in field:
            print(f"- {field['name']}: {field['print_fct'](config_obj.GetValue(field['type']))}")
        else:
            print(f"- {field['name']}: {config_obj.GetValue(field['type'])}")
