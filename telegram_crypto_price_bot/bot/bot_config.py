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

import logging
from typing import Dict, Tuple

from telegram_crypto_price_bot.bot.bot_config_types import BotConfigTypes
from telegram_crypto_price_bot.config.config_typing import ConfigSectionsType
from telegram_crypto_price_bot.utils.utils import Utils


class _ConfigTypeConverter:
    """Internal class for converting configuration types."""

    STR_TO_LOG_LEVEL: Dict[str, int] = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }

    @staticmethod
    def StrToLogLevel(log_level: str) -> int:
        """
        Convert string representation to logging level.

        Args:
            log_level: String representation of log level.

        Returns:
            Logging level integer, defaults to INFO if not found.
        """
        return _ConfigTypeConverter.STR_TO_LOG_LEVEL[log_level] if log_level in _ConfigTypeConverter.STR_TO_LOG_LEVEL else logging.INFO

    @staticmethod
    def LogLevelToStr(log_level: int) -> str:
        """
        Convert logging level to string representation.

        Args:
            log_level: Logging level integer.

        Returns:
            String representation of the log level.
        """
        idx = list(_ConfigTypeConverter.STR_TO_LOG_LEVEL.values()).index(log_level)
        return list(_ConfigTypeConverter.STR_TO_LOG_LEVEL.keys())[idx]


class PriceBotConfigConst:
    """Constants for price bot configuration."""

    LINE_STYLES: Tuple[str, ...] = ("-", "--", "-.", ":", " ", "")


BotConfig: ConfigSectionsType = {
    # Pyrogram
    "pyrogram": [
        {
            "type": BotConfigTypes.API_ID,
            "name": "api_id",
        },
        {
            "type": BotConfigTypes.API_HASH,
            "name": "api_hash",
        },
        {
            "type": BotConfigTypes.BOT_TOKEN,
            "name": "bot_token",
        },
        {
            "type": BotConfigTypes.SESSION_NAME,
            "name": "session_name",
        },
    ],
    # App
    "app": [
        {
            "type": BotConfigTypes.APP_TEST_MODE,
            "name": "app_test_mode",
            "conv_fct": Utils.StrToBool,
        },
        {
            "type": BotConfigTypes.APP_LANG_FILE,
            "name": "app_lang_file",
            "def_val": None,
        },
    ],
    # Task
    "task": [
        {
            "type": BotConfigTypes.TASKS_MAX_NUM,
            "name": "tasks_max_num",
            "conv_fct": Utils.StrToInt,
            "def_val": 20,
            "valid_if": lambda cfg, val: val > 0,
        },
    ],
    # Coingecko
    "coingecko": [
        {
            "type": BotConfigTypes.COINGECKO_API_KEY_DEMO,
            "name": "coingecko_api_key_demo",
            "def_val": "",
        },
        {
            "type": BotConfigTypes.COINGECKO_API_KEY_PRO,
            "name": "coingecko_api_key_pro",
            "def_val": "",
        },
        {
            "type": BotConfigTypes.COINGECKO_API_MAX_RETRIES,
            "name": "coingecko_api_max_retries",
            "conv_fct": Utils.StrToInt,
            "def_val": 7,
        },
        {
            "type": BotConfigTypes.COINGECKO_API_TIMEOUT_SEC,
            "name": "coingecko_api_timeout_sec",
            "conv_fct": Utils.StrToFloat,
            "def_val": 10.0,
        },
        # For retro-compatibility
        {
            "type": BotConfigTypes.COINGECKO_API_KEY_PRO,
            "name": "coingecko_api_key",
            "def_val": "",
        },
    ],
    # Chart
    "chart": [
        {
            "type": BotConfigTypes.CHART_DISPLAY,
            "name": "chart_display",
            "conv_fct": Utils.StrToBool,
            "def_val": True,
        },
        {
            "type": BotConfigTypes.CHART_DATE_FORMAT,
            "name": "chart_date_format",
            "def_val": "%d/%m/%Y %H:00",
            "load_if": lambda cfg: cfg.GetValue(BotConfigTypes.CHART_DISPLAY),
        },
        {
            "type": BotConfigTypes.CHART_BACKGROUND_COLOR,
            "name": "chart_background_color",
            "def_val": "white",
            "load_if": lambda cfg: cfg.GetValue(BotConfigTypes.CHART_DISPLAY),
        },
        {
            "type": BotConfigTypes.CHART_TITLE_COLOR,
            "name": "chart_title_color",
            "def_val": "black",
            "load_if": lambda cfg: cfg.GetValue(BotConfigTypes.CHART_DISPLAY),
        },
        {
            "type": BotConfigTypes.CHART_FRAME_COLOR,
            "name": "chart_frame_color",
            "def_val": "black",
            "load_if": lambda cfg: cfg.GetValue(BotConfigTypes.CHART_DISPLAY),
        },
        {
            "type": BotConfigTypes.CHART_AXES_COLOR,
            "name": "chart_axes_color",
            "def_val": "black",
            "load_if": lambda cfg: cfg.GetValue(BotConfigTypes.CHART_DISPLAY),
        },
        {
            "type": BotConfigTypes.CHART_LINE_COLOR,
            "name": "chart_line_color",
            "def_val": "#3475AB",
            "load_if": lambda cfg: cfg.GetValue(BotConfigTypes.CHART_DISPLAY),
        },
        {
            "type": BotConfigTypes.CHART_LINE_STYLE,
            "name": "chart_line_style",
            "def_val": "-",
            "load_if": lambda cfg: cfg.GetValue(BotConfigTypes.CHART_DISPLAY),
            "valid_if": lambda cfg, val: val in PriceBotConfigConst.LINE_STYLES,
        },
        {
            "type": BotConfigTypes.CHART_LINE_WIDTH,
            "name": "chart_line_width",
            "conv_fct": Utils.StrToInt,
            "def_val": 1,
            "load_if": lambda cfg: cfg.GetValue(BotConfigTypes.CHART_DISPLAY),
            "valid_if": lambda cfg, val: val > 0,
        },
        {
            "type": BotConfigTypes.CHART_DISPLAY_GRID,
            "name": "chart_display_grid",
            "conv_fct": Utils.StrToBool,
            "def_val": True,
            "load_if": lambda cfg: cfg.GetValue(BotConfigTypes.CHART_DISPLAY),
        },
        {
            "type": BotConfigTypes.CHART_GRID_MAX_SIZE,
            "name": "chart_grid_max_size",
            "conv_fct": Utils.StrToInt,
            "def_val": 4,
            "load_if": lambda cfg: (cfg.GetValue(BotConfigTypes.CHART_DISPLAY) and cfg.GetValue(BotConfigTypes.CHART_DISPLAY_GRID)),
            "valid_if": lambda cfg, val: val > 0,
        },
        {
            "type": BotConfigTypes.CHART_GRID_COLOR,
            "name": "chart_grid_color",
            "def_val": "#DFDFDF",
            "load_if": lambda cfg: (cfg.GetValue(BotConfigTypes.CHART_DISPLAY) and cfg.GetValue(BotConfigTypes.CHART_DISPLAY_GRID)),
        },
        {
            "type": BotConfigTypes.CHART_GRID_LINE_STYLE,
            "name": "chart_grid_line_style",
            "def_val": "--",
            "load_if": lambda cfg: (cfg.GetValue(BotConfigTypes.CHART_DISPLAY) and cfg.GetValue(BotConfigTypes.CHART_DISPLAY_GRID)),
            "valid_if": lambda cfg, val: val in PriceBotConfigConst.LINE_STYLES,
        },
        {
            "type": BotConfigTypes.CHART_GRID_LINE_WIDTH,
            "name": "chart_grid_line_width",
            "conv_fct": Utils.StrToInt,
            "def_val": 1,
            "load_if": lambda cfg: (cfg.GetValue(BotConfigTypes.CHART_DISPLAY) and cfg.GetValue(BotConfigTypes.CHART_DISPLAY_GRID)),
            "valid_if": lambda cfg, val: val > 0,
        },
    ],
    # Price
    "price": [
        {
            "type": BotConfigTypes.PRICE_DISPLAY_MARKET_CAP,
            "name": "price_display_market_cap",
            "conv_fct": Utils.StrToBool,
            "def_val": True,
        },
        {
            "type": BotConfigTypes.PRICE_DISPLAY_MARKET_CAP_RANK,
            "name": "price_display_market_cap_rank",
            "conv_fct": Utils.StrToBool,
            "def_val": False,
        },
    ],
    # Logging
    "logging": [
        {
            "type": BotConfigTypes.LOG_LEVEL,
            "name": "log_level",
            "conv_fct": _ConfigTypeConverter.StrToLogLevel,
            "print_fct": _ConfigTypeConverter.LogLevelToStr,
            "def_val": logging.INFO,
        },
        {
            "type": BotConfigTypes.LOG_CONSOLE_ENABLED,
            "name": "log_console_enabled",
            "conv_fct": Utils.StrToBool,
            "def_val": True,
        },
        {
            "type": BotConfigTypes.LOG_FILE_ENABLED,
            "name": "log_file_enabled",
            "conv_fct": Utils.StrToBool,
            "def_val": False,
        },
        {
            "type": BotConfigTypes.LOG_FILE_NAME,
            "name": "log_file_name",
            "load_if": lambda cfg: cfg.GetValue(BotConfigTypes.LOG_FILE_ENABLED),
        },
        {
            "type": BotConfigTypes.LOG_FILE_USE_ROTATING,
            "name": "log_file_use_rotating",
            "conv_fct": Utils.StrToBool,
            "load_if": lambda cfg: cfg.GetValue(BotConfigTypes.LOG_FILE_ENABLED),
        },
        {
            "type": BotConfigTypes.LOG_FILE_APPEND,
            "name": "log_file_append",
            "conv_fct": Utils.StrToBool,
            "load_if": lambda cfg: (
                cfg.GetValue(BotConfigTypes.LOG_FILE_ENABLED) and not cfg.GetValue(BotConfigTypes.LOG_FILE_USE_ROTATING)
            ),
        },
        {
            "type": BotConfigTypes.LOG_FILE_MAX_BYTES,
            "name": "log_file_max_bytes",
            "conv_fct": Utils.StrToInt,
            "load_if": lambda cfg: (cfg.GetValue(BotConfigTypes.LOG_FILE_ENABLED) and cfg.GetValue(BotConfigTypes.LOG_FILE_USE_ROTATING)),
        },
        {
            "type": BotConfigTypes.LOG_FILE_BACKUP_CNT,
            "name": "log_file_backup_cnt",
            "conv_fct": Utils.StrToInt,
            "load_if": lambda cfg: (cfg.GetValue(BotConfigTypes.LOG_FILE_ENABLED) and cfg.GetValue(BotConfigTypes.LOG_FILE_USE_ROTATING)),
        },
    ],
}
