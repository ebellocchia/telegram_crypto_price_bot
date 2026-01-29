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

from typing import Dict, List, Union


class ChartInfo:
    """Class for storing and accessing chart information for cryptocurrency prices."""

    coin_id: str
    coin_vs: str
    last_days: int
    x: List[int]
    y: List[float]

    def __init__(self,
                 chart_info: Dict[str, List[List[Union[int, float]]]],
                 coin_id: str,
                 coin_vs: str,
                 last_days: int) -> None:
        """Initialize chart information from price data.

        Args:
            chart_info: Dictionary containing price data with timestamps
            coin_id: Cryptocurrency coin identifier
            coin_vs: Currency to compare against (e.g., 'usd')
            last_days: Number of days of historical data
        """
        self.coin_id = coin_id
        self.coin_vs = coin_vs
        self.last_days = last_days
        self.x = []
        self.y = []

        for price in chart_info["prices"]:
            self.x.append(int(price[0] / 1000))
            self.y.append(price[1])

    def CoinId(self) -> str:
        """Get the cryptocurrency coin identifier.

        Returns:
            The coin identifier string
        """
        return self.coin_id

    def CoinVs(self) -> str:
        """Get the currency to compare against.

        Returns:
            The comparison currency string
        """
        return self.coin_vs

    def LastDays(self) -> int:
        """Get the number of days of historical data.

        Returns:
            Number of days
        """
        return self.last_days

    def X(self) -> List[int]:
        """Get the x coordinates (timestamps) for the chart.

        Returns:
            List of timestamps in seconds
        """
        return self.x

    def Y(self) -> List[float]:
        """Get the y coordinates (prices) for the chart.

        Returns:
            List of price values
        """
        return self.y
