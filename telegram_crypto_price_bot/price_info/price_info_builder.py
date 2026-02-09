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

from telegram_crypto_price_bot.bot.bot_config_types import BotConfigTypes
from telegram_crypto_price_bot.config.config_object import ConfigObject
from telegram_crypto_price_bot.misc.formatters import (
    CoinPairFormatter,
    MarketCapFormatter,
    PriceChangePercFormatter,
    PriceFormatter,
    VolumeFormatter,
)
from telegram_crypto_price_bot.price_info.price_info import PriceInfo, PriceInfoTypes
from telegram_crypto_price_bot.translation.translation_loader import TranslationLoader


class PriceInfoBuilderConst:
    """Constants for price information builder configuration."""

    ALIGN_LEN: int = 16
    MARKDOWN_CODE_DELIM: str = "```"


class PriceInfoBuilder:
    """Builder class for formatting cryptocurrency price information messages."""

    config: ConfigObject
    translator: TranslationLoader

    def __init__(self,
                 config: ConfigObject,
                 translator: TranslationLoader) -> None:
        """
        Initialize the price info builder.

        Args:
            config: Configuration object.
            translator: Translation loader.
        """
        self.config = config
        self.translator = translator

    def Build(self,
              price_info: PriceInfo) -> str:
        """
        Build a formatted price information message.

        Args:
            price_info: Price information to format.

        Returns:
            Formatted price information message string.
        """
        coin_vs = price_info.GetData(PriceInfoTypes.COIN_VS)
        coin_vs_sym = price_info.GetData(PriceInfoTypes.COIN_VS_SYMBOL)

        coin_pair = CoinPairFormatter.Format(price_info.GetData(PriceInfoTypes.COIN_SYMBOL), coin_vs)
        price = PriceFormatter.Format(price_info.GetData(PriceInfoTypes.CURR_PRICE), coin_vs_sym)

        high_24h = PriceFormatter.Format(price_info.GetData(PriceInfoTypes.HIGH_24H), coin_vs_sym)
        low_24h = PriceFormatter.Format(price_info.GetData(PriceInfoTypes.LOW_24H), coin_vs_sym)
        volume = VolumeFormatter.Format(price_info.GetData(PriceInfoTypes.TOTAL_VOLUME), coin_vs_sym)
        market_cap = MarketCapFormatter.Format(price_info.GetData(PriceInfoTypes.MARKET_CAP), coin_vs_sym)
        market_cap_rank = price_info.GetData(PriceInfoTypes.MARKET_CAP_RANK)

        change_perc_24h = PriceChangePercFormatter.Format(price_info.GetData(PriceInfoTypes.PRICE_CHANGE_PERC_24H))
        change_perc_7d = PriceChangePercFormatter.Format(price_info.GetData(PriceInfoTypes.PRICE_CHANGE_PERC_7D))
        change_perc_14d = PriceChangePercFormatter.Format(price_info.GetData(PriceInfoTypes.PRICE_CHANGE_PERC_14D))
        change_perc_30d = PriceChangePercFormatter.Format(price_info.GetData(PriceInfoTypes.PRICE_CHANGE_PERC_30D))

        msg = self.translator.GetSentence("PRICE_INFO_TITLE_MSG",
                                          coin_name=price_info.GetData(PriceInfoTypes.COIN_NAME))

        msg += PriceInfoBuilderConst.MARKDOWN_CODE_DELIM
        msg += "\n"

        msg += self.__PrintAligned(f"💵 {coin_pair}", price)
        msg += self.__PrintAligned("📈 High 24h", high_24h)
        msg += self.__PrintAligned("📈 Low 24h", low_24h)
        msg += self.__PrintAligned("📊 Volume 24h", volume)

        if self.config.GetValue(BotConfigTypes.PRICE_DISPLAY_MARKET_CAP):
            msg += self.__PrintAligned("💎 Market Cap", market_cap)
        if self.config.GetValue(BotConfigTypes.PRICE_DISPLAY_MARKET_CAP_RANK):
            msg += self.__PrintAligned("🏆 Rank", f"{market_cap_rank:d}")

        msg += "\n⚖ Diff.\n"
        msg += self.__PrintAligned("     24h", change_perc_24h, 1)
        msg += self.__PrintAligned("     7d", change_perc_7d, 1)
        msg += self.__PrintAligned("     14d", change_perc_14d, 1)
        msg += self.__PrintAligned("     30d", change_perc_30d, 1, False)

        msg += "\n"
        msg += PriceInfoBuilderConst.MARKDOWN_CODE_DELIM

        return msg

    @staticmethod
    def __PrintAligned(header: str,
                       value: str,
                       correction: int = 0,
                       add_new_line: bool = True) -> str:
        """
        Format a string with aligned header and value.

        Args:
            header: Header text.
            value: Value text.
            correction: Alignment correction offset.
            add_new_line: Whether to add a newline character.

        Returns:
            Formatted aligned string.
        """
        alignment = " " * (PriceInfoBuilderConst.ALIGN_LEN + correction - len(header))
        new_line = "\n" if add_new_line else ""

        return f"{header}{alignment}{value}{new_line}"
