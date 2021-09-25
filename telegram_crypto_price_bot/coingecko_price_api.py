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
from pycoingecko import CoinGeckoAPI
from telegram_crypto_price_bot.chart_info import ChartInfo
from telegram_crypto_price_bot.price_info import PriceInfo


#
# Classes
#

# Error for coingecko price API class
class CoinGeckoPriceApiError(Exception):
    pass


# Coingecko price API class
class CoinGeckoPriceApi:
    # Constructor
    def __init__(self) -> None:
        self.api = CoinGeckoAPI()

    # Get price info
    def GetPriceInfo(self,
                     coin_id: str,
                     coin_vs: str) -> PriceInfo:
        try:
            coin_info = self.api.get_coin_by_id(id=coin_id)
        except ValueError as ex:
            raise CoinGeckoPriceApiError() from ex

        return PriceInfo(coin_info, coin_vs)

    # Get chart info
    def GetChartInfo(self,
                     coin_id: str,
                     coin_vs: str,
                     last_days: int) -> ChartInfo:
        try:
            chart_info = self.api.get_coin_market_chart_by_id(id=coin_id, vs_currency=coin_vs, days=last_days)
        except ValueError as ex:
            raise CoinGeckoPriceApiError() from ex

        return ChartInfo(chart_info, coin_id, coin_vs, last_days)
