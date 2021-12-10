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
from enum import Enum, auto, unique
from typing import Any, Dict
from telegram_crypto_price_bot.utils.utils import Utils


#
# Enumerations
#

# Price data types
@unique
class PriceInfoTypes(Enum):
    COIN_NAME = auto()
    COIN_SYMBOL = auto()
    COIN_VS = auto()
    COIN_VS_SYMBOL = auto()
    CURR_PRICE = auto()
    MARKET_CAP = auto()
    MARKET_CAP_RANK = auto()
    HIGH_24H = auto()
    LOW_24H = auto()
    TOTAL_VOLUME = auto()
    PRICE_CHANGE_PERC_24H = auto()
    PRICE_CHANGE_PERC_7D = auto()
    PRICE_CHANGE_PERC_14D = auto()
    PRICE_CHANGE_PERC_30D = auto()


#
# Classes
#

# Price info class
class PriceInfo:

    info: Dict[PriceInfoTypes, Any]

    # Constructor
    def __init__(self,
                 coin_data: Dict[str, Any],
                 coin_vs: str) -> None:
        self.info = {
            PriceInfoTypes.COIN_NAME: coin_data["name"],
            PriceInfoTypes.COIN_SYMBOL: coin_data["symbol"].upper(),
            PriceInfoTypes.COIN_VS: coin_vs.upper(),
            PriceInfoTypes.COIN_VS_SYMBOL: "$" if coin_vs == "usd" else ("€" if coin_vs == "eur" else coin_vs.upper()),
            PriceInfoTypes.CURR_PRICE: Utils.StrToFloat(coin_data["market_data"]["current_price"][coin_vs]),
            PriceInfoTypes.MARKET_CAP: Utils.StrToInt(coin_data["market_data"]["market_cap"][coin_vs]),
            PriceInfoTypes.MARKET_CAP_RANK: Utils.StrToInt(coin_data["market_data"]["market_cap_rank"]),
            PriceInfoTypes.HIGH_24H: Utils.StrToFloat(coin_data["market_data"]["high_24h"][coin_vs]),
            PriceInfoTypes.LOW_24H: Utils.StrToFloat(coin_data["market_data"]["low_24h"][coin_vs]),
            PriceInfoTypes.TOTAL_VOLUME: Utils.StrToInt(coin_data["market_data"]["total_volume"][coin_vs]),
            # Price change percentage
            PriceInfoTypes.PRICE_CHANGE_PERC_24H: Utils.StrToFloat(
                coin_data["market_data"]["price_change_percentage_24h"]
            ),
            PriceInfoTypes.PRICE_CHANGE_PERC_7D: Utils.StrToFloat(
                coin_data["market_data"]["price_change_percentage_7d"]
            ),
            PriceInfoTypes.PRICE_CHANGE_PERC_14D: Utils.StrToFloat(
                coin_data["market_data"]["price_change_percentage_14d"]
            ),
            PriceInfoTypes.PRICE_CHANGE_PERC_30D: Utils.StrToFloat(
                coin_data["market_data"]["price_change_percentage_30d"]
            ),
        }

    # Get info
    def GetData(self,
                data_type: PriceInfoTypes) -> Any:
        if not isinstance(data_type, PriceInfoTypes):
            raise TypeError("Invalid info type")

        return self.info[data_type]
