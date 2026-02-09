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
import json
import logging
from typing import Any, Dict

import httpx
from httpx import AsyncClient
from tenacity import (
    AsyncRetrying,
    RetryError,
    before_sleep_log,
    retry_if_exception,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from telegram_crypto_price_bot.bot.bot_config_types import BotConfigTypes
from telegram_crypto_price_bot.chart_info.chart_info import ChartInfo
from telegram_crypto_price_bot.config.config_object import ConfigObject
from telegram_crypto_price_bot.logger.logger import Logger
from telegram_crypto_price_bot.price_info.price_info import PriceInfo


class CoinGeckoPriceApiError(Exception):
    """Exception raised when CoinGecko API operations fail."""


class CoinGeckoPriceApiConst:
    """Constants for CoinGecko price API class."""
    API_DEMO_URL_BASE: str = "https://api.coingecko.com/api/v3"
    API_PRO_URL_BASE: str = "https://pro-api.coingecko.com/api/v3"

    HEADER_API_KEY_DEMO: str = "x-cg-demo-api-key"
    HEADER_API_KEY_PRO: str = "x-cg-pro-api-key"

    RETRY_DELAY: int = 2


class CoinGeckoPriceApi:
    """API wrapper for retrieving cryptocurrency price and chart data from CoinGecko."""

    api_base_url: str
    headers: Dict[str, str]
    logger: Logger
    retry_strategy: AsyncRetrying
    timeout: float

    def __init__(self,
                 config: ConfigObject,
                 logger: Logger) -> None:
        """
        Initialize the CoinGecko price API.

        Args:
            config: Configuration object containing API key.
            logger: Logger instance.
        """
        self.logger = logger
        self.timeout = config.GetValue(BotConfigTypes.COINGECKO_API_TIMEOUT_SEC)
        # Pro key
        api_key_pro = config.GetValue(BotConfigTypes.COINGECKO_API_KEY_PRO)
        if api_key_pro:
            self.headers = {
                CoinGeckoPriceApiConst.HEADER_API_KEY_PRO: api_key_pro
            }
            self.api_base_url = CoinGeckoPriceApiConst.API_PRO_URL_BASE
        else:
            # Demo key
            api_key_demo = config.GetValue(BotConfigTypes.COINGECKO_API_KEY_DEMO)
            if api_key_demo:
                self.headers = {
                    CoinGeckoPriceApiConst.HEADER_API_KEY_DEMO: api_key_demo
                }
            else:
                self.headers = {}
            self.api_base_url = CoinGeckoPriceApiConst.API_DEMO_URL_BASE

        self.retry_strategy = AsyncRetrying(
            stop=stop_after_attempt(config.GetValue(BotConfigTypes.COINGECKO_API_MAX_RETRIES)),
            wait=wait_exponential(multiplier=CoinGeckoPriceApiConst.RETRY_DELAY,
                                  min=CoinGeckoPriceApiConst.RETRY_DELAY),
            retry=(
                retry_if_exception_type(
                    (httpx.NetworkError, httpx.ProtocolError, httpx.TimeoutException)
                ) |
                retry_if_exception(
                    # Too many requests
                    lambda e: isinstance(e, httpx.HTTPStatusError) and e.response.status_code == 429
                )
            ),
            before_sleep=before_sleep_log(logger.GetLogger(), logging.WARNING),
            reraise=False
        )

    async def GetPriceInfo(self,
                           coin_id: str,
                           coin_vs: str) -> PriceInfo:
        """
        Get current price information for a cryptocurrency.

        Args:
            coin_id: Cryptocurrency coin identifier.
            coin_vs: Currency to compare against.

        Returns:
            Price information object.

        Raises:
            CoinGeckoPriceApiError: If API request fails.
        """
        coin_info = await self.__SendRequestWithRetry(f"coins/{coin_id}", {})
        return PriceInfo(coin_info, coin_vs)

    async def GetChartInfo(self,
                           coin_id: str,
                           coin_vs: str,
                           last_days: int) -> ChartInfo:
        """
        Get historical chart data for a cryptocurrency.

        Args:
            coin_id: Cryptocurrency coin identifier.
            coin_vs: Currency to compare against.
            last_days: Number of days of historical data to retrieve.

        Returns:
            Chart information object.

        Raises:
            CoinGeckoPriceApiError: If API request fails.
        """
        chart_info = await self.__SendRequestWithRetry(
            f"coins/{coin_id}/market_chart",
            {
                "vs_currency": coin_vs,
                "days": last_days,
            }
        )
        return ChartInfo(chart_info, coin_id, coin_vs, last_days)

    async def __SendRequestWithRetry(
        self,
        url: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send HTTP request with retry logic.

        Args:
            url: API endpoint path.
            params: Query parameters for the request.

        Returns:
            JSON response as dictionary.

        Raises:
            CoinGeckoPriceApiError: If all retry attempts fail.
        """
        try:
            return await self.retry_strategy(self.__SendRequest, url, params)
        except RetryError as e:
            self.logger.GetLogger().error(f"All attempts failed for CoinGecko request for URL {url}")
            raise CoinGeckoPriceApiError() from e

    async def __SendRequest(
        self,
        url: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send HTTP request to CoinGecko API.

        Args:
            url: API endpoint path.
            params: Query parameters for the request.

        Returns:
            JSON response as dictionary.

        Raises:
            httpx.HTTPStatusError: If HTTP request fails.
            httpx.NetworkError: If network error occurs.
            httpx.ProtocolError: If protocol error occurs.
            httpx.TimeoutException: If request times out.
        """
        async with AsyncClient(
            base_url=self.api_base_url,
            headers=self.headers,
            timeout=self.timeout
        ) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return json.loads(response.content.decode("utf-8"))
