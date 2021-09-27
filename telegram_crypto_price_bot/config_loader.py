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
from typing import Any, Dict, List
from telegram_crypto_price_bot.config import ConfigError, Config


#
# Types
#
FieldCfgType = Dict[str, Any]
FieldsCfgType = List[FieldCfgType]
ConfigCfgType = Dict[str, FieldsCfgType]


#
# Classes
#

# Configuration loader class
class ConfigLoader:
    # Constructor
    def __init__(self,
                 config_cfg: ConfigCfgType) -> None:
        self.config_cfg = config_cfg
        self.config = Config()
        self.config_parser = None

    # Load configuration
    def Load(self,
             config_file: str) -> None:
        # Read file
        self.config_parser = configparser.ConfigParser()
        self.config_parser.read(config_file)

        # Print
        print("Loading configuration...\n")
        # Load sections
        self.__LoadSections()
        # New line
        print("")

    # Get configuration
    def GetConfig(self) -> Config:
        return self.config

    # Load sections
    def __LoadSections(self) -> None:
        # For each section
        for section, fields in self.config_cfg.items():
            # Print section
            print(f"Section [{section}]")
            # Load fields
            self.__LoadFields(section, fields)

    # Load fields
    def __LoadFields(self,
                     section: str,
                     fields: FieldsCfgType) -> None:
        # For each field
        for field in fields:
            # Load if needed
            if self.__FieldShallBeLoaded(field):
                # Set field value and print it
                self.__SetFieldValue(section, field)
                self.__PrintFieldValue(field)

    # Get if field shall be loaded
    def __FieldShallBeLoaded(self,
                             field: FieldCfgType) -> bool:
        return field["load_if"](self.config) if "load_if" in field else True

    # Set field value
    def __SetFieldValue(self,
                        section: str,
                        field: FieldCfgType) -> None:
        try:
            field_val = self.config_parser[section][field["name"]]
        # Field not present, set default value if specified
        except KeyError:
            if "def_val" not in field:
                raise ConfigError(f"Configuration field \"{field['name']}\" not found")
            field_val = field["def_val"]

        # Convert value if needed
        if "conv_fct" in field:
            field_val = field["conv_fct"](field_val)
        # Validate value if needed
        if "valid_if" in field and not field["valid_if"](self.config, field_val):
            raise ConfigError(f"Value '{field_val}' is not valid for field \"{field['name']}\"")

        # Set value
        self.config.SetValue(field["type"], field_val)

    # Print field value
    def __PrintFieldValue(self,
                          field: FieldCfgType) -> None:
        if "print_fct" in field:
            print(f"- {field['name']}: {field['print_fct'](self.config.GetValue(field['type']))}")
        else:
            print(f"- {field['name']}: {self.config.GetValue(field['type'])}")
