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

from pycoingecko import CoinGeckoAPI

from telegram_crypto_price_bot.bot.bot_config_types import BotConfigTypes
from telegram_crypto_price_bot.chart_info.chart_info import ChartInfo
from telegram_crypto_price_bot.config.config_object import ConfigObject
from telegram_crypto_price_bot.price_info.price_info import PriceInfo


class CoinGeckoPriceApiError(Exception):
    """Exception raised when CoinGecko API operations fail."""

    pass


class CoinGeckoPriceApi:
    """API wrapper for retrieving cryptocurrency price and chart data from CoinGecko."""

    api: CoinGeckoAPI

    def __init__(self, config: ConfigObject) -> None:
        """Initialize the CoinGecko price API.

        Args:
            config: Configuration object containing API key
        """
        self.api = CoinGeckoAPI(api_key=config.GetValue(BotConfigTypes.COINGECKO_API_KEY))

    def GetPriceInfo(self,
                     coin_id: str,
                     coin_vs: str) -> PriceInfo:
        """Get current price information for a cryptocurrency.

        Args:
            coin_id: Cryptocurrency coin identifier
            coin_vs: Currency to compare against

        Returns:
            Price information object

        Raises:
            CoinGeckoPriceApiError: If API request fails
        """
        try:
            coin_info = self.api.get_coin_by_id(id=coin_id)
        except ValueError as ex:
            raise CoinGeckoPriceApiError() from ex

        return PriceInfo(coin_info, coin_vs)

    def GetChartInfo(self,
                     coin_id: str,
                     coin_vs: str,
                     last_days: int) -> ChartInfo:
        """Get historical chart data for a cryptocurrency.

        Args:
            coin_id: Cryptocurrency coin identifier
            coin_vs: Currency to compare against
            last_days: Number of days of historical data to retrieve

        Returns:
            Chart information object

        Raises:
            CoinGeckoPriceApiError: If API request fails
        """
        try:
            chart_info = self.api.get_coin_market_chart_by_id(id=coin_id, vs_currency=coin_vs, days=last_days)
        except ValueError as ex:
            raise CoinGeckoPriceApiError() from ex

        return ChartInfo(chart_info, coin_id, coin_vs, last_days)
