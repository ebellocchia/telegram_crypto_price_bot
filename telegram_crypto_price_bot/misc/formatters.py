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

from typing import Optional


class CoinIdFormatter:
    """Formatter for cryptocurrency ID strings."""

    @staticmethod
    def Format(coin_id: str) -> str:
        """Format a coin ID by title-casing and replacing hyphens with spaces.

        Args:
            coin_id: The coin identifier to format

        Returns:
            Formatted coin ID string
        """
        return coin_id.title().replace("-", " ")


class CoinPairFormatter:
    """Formatter for cryptocurrency trading pairs."""

    @staticmethod
    def Format(coin_sym: str,
               coin_vs: str) -> str:
        """Format a coin pair string.

        Args:
            coin_sym: The coin symbol
            coin_vs: The currency symbol to compare against

        Returns:
            Formatted coin pair string
        """
        return f"{coin_sym}/{coin_vs}"


class MarketCapFormatter:
    """Formatter for market capitalization values."""

    @staticmethod
    def Format(market_cap: int,
               coin_vs: Optional[str] = None) -> str:
        """Format market cap with appropriate magnitude suffix (B/M).

        Args:
            market_cap: Market capitalization value
            coin_vs: Optional currency symbol for formatting

        Returns:
            Formatted market cap string
        """
        coin_vs = coin_vs or ""
        space = " " if coin_vs not in ("$", "€") else ""

        if market_cap > 1e9:
            formatted_str = f"{market_cap / 1e9:.2f}B {coin_vs}"
        elif market_cap > 1e6:
            formatted_str = f"{market_cap / 1e6:.2f}M {coin_vs}"
        else:
            formatted_str = f"{market_cap:,}{space}{coin_vs}"
        return formatted_str


class PriceFormatter:
    """Formatter for cryptocurrency prices with adaptive precision."""

    @staticmethod
    def Format(price: float,
               coin_vs: Optional[str] = None) -> str:
        """Format price with precision based on value magnitude.

        Args:
            price: Price value to format
            coin_vs: Optional currency symbol for formatting

        Returns:
            Formatted price string
        """
        coin_vs = coin_vs or ""
        space = " " if coin_vs not in ("$", "€") else ""

        if price >= 1000:
            formatted_str = f"{price:.0f}{space}{coin_vs}"
        elif price >= 100:
            formatted_str = f"{price:.1f}{space}{coin_vs}"
        elif price >= 1:
            formatted_str = f"{price:.2f}{space}{coin_vs}"
        elif price >= 0.0001:
            formatted_str = f"{price:.4f}{space}{coin_vs}"
        else:
            formatted_str = f"{price:f}{space}{coin_vs}"
        return formatted_str


class PriceChangePercFormatter:
    """Formatter for price change percentages with visual indicators."""

    @staticmethod
    def Format(price_change: float) -> str:
        """Format price change percentage with red/green indicator.

        Args:
            price_change: Price change percentage value

        Returns:
            Formatted price change string with emoji indicator
        """
        return f"{'🔴' if price_change < 0 else '🟢'} {price_change:+.2f}%"


class VolumeFormatter:
    """Formatter for trading volume values."""

    @staticmethod
    def Format(volume: int,
               coin_vs: Optional[str] = None) -> str:
        """Format volume with appropriate magnitude suffix (B/M).

        Args:
            volume: Trading volume value
            coin_vs: Optional currency symbol for formatting

        Returns:
            Formatted volume string
        """
        coin_vs = coin_vs or ""
        space = " " if coin_vs not in ("$", "€") else ""

        if volume > 1e9:
            formatted_str = f"{volume / 1e9:.2f}B {coin_vs}"
        elif volume > 1e6:
            formatted_str = f"{volume / 1e6:.2f}M {coin_vs}"
        else:
            formatted_str = f"{volume:,}{space}{coin_vs}"
        return formatted_str
