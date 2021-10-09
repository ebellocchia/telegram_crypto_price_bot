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
from telegram_crypto_price_bot.config import ConfigTypes, Config
from telegram_crypto_price_bot.formatters import (
    CoinPairFormatter, MarketCapFormatter, PriceFormatter, PriceChangePercFormatter, VolumeFormatter
)
from telegram_crypto_price_bot.price_info import PriceInfoTypes, PriceInfo
from telegram_crypto_price_bot.translation_loader import TranslationLoader


#
# Classes
#

# Constants for price info builder class
class PriceInfoBuilderConst:
    # Alignment size
    ALIGN_LEN: int = 16
    # Delimiter for Markdown code
    MARKDOWN_CODE_DELIM: str = "```"


# Price info builder class
class PriceInfoBuilder:

    config: Config
    translator: TranslationLoader

    # Constructor
    def __init__(self,
                 config: Config,
                 translator: TranslationLoader) -> None:
        self.config = config
        self.translator = translator

    # Build price info
    def Build(self,
              price_info: PriceInfo) -> str:
        coin_vs = price_info.GetData(PriceInfoTypes.COIN_VS)
        coin_vs_sym = price_info.GetData(PriceInfoTypes.COIN_VS_SYMBOL)

        # Get and format data
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

        #
        # Build message string
        #

        # Title
        msg = self.translator.GetSentence("PRICE_INFO_TITLE_MSG",
                                          coin_name=price_info.GetData(PriceInfoTypes.COIN_NAME))

        # Begin code
        msg += PriceInfoBuilderConst.MARKDOWN_CODE_DELIM

        # Price info
        msg += self.__PrintAligned(f"💵 {coin_pair}", price)
        msg += self.__PrintAligned("📈 High 24h", high_24h)
        msg += self.__PrintAligned("📈 Low 24h", low_24h)
        msg += self.__PrintAligned("📊 Volume 24h", volume)

        # Market cap
        if self.config.GetValue(ConfigTypes.PRICE_DISPLAY_MARKET_CAP):
            msg += self.__PrintAligned("💎 Market Cap", market_cap)
        # Market cap rank
        if self.config.GetValue(ConfigTypes.PRICE_DISPLAY_MARKET_CAP_RANK):
            msg += self.__PrintAligned("🏆 Rank", f"{market_cap_rank:d}")

        # Price differences
        msg += "\n⚖ Diff.\n"
        msg += self.__PrintAligned("     24h", change_perc_24h, 1)
        msg += self.__PrintAligned("     7d", change_perc_7d, 1)
        msg += self.__PrintAligned("     14d", change_perc_14d, 1)
        msg += self.__PrintAligned("     30d", change_perc_30d, 1, False)

        # End code
        msg += PriceInfoBuilderConst.MARKDOWN_CODE_DELIM

        return msg

    # Print string aligned
    @staticmethod
    def __PrintAligned(header: str,
                       value: str,
                       correction: int = 0,
                       add_new_line: bool = True) -> str:
        alignment = " " * (PriceInfoBuilderConst.ALIGN_LEN + correction - len(header))
        new_line = "\n" if add_new_line else ""

        return f"{header}{alignment}{value}{new_line}"
