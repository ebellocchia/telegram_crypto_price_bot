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
from typing import Optional


#
# Classes
#

# Coin ID formatter class
class CoinIdFormatter:
    # Format coin ID
    @staticmethod
    def Format(coin_id: str) -> str:
        return coin_id.title().replace("-", " ")


# Coin pair formatter class
class CoinPairFormatter:
    # Format coin pair
    @staticmethod
    def Format(coin_sym: str,
               coin_vs: str) -> str:
        return f"{coin_sym}/{coin_vs}"


# Market cap formatter class
class MarketCapFormatter:
    # Format market cap
    @staticmethod
    def Format(market_cap: int,
               coin_vs: Optional[str] = None) -> str:
        coin_vs = coin_vs or ""
        space = " " if coin_vs not in ("$", "€") else ""

        if market_cap > 1e9:
            return f"{market_cap / 1e9:.2f}B {coin_vs}"
        elif market_cap > 1e6:
            return f"{market_cap / 1e6:.2f}M {coin_vs}"
        return f"{market_cap:,}{space}{coin_vs}"


# Price formatter class
class PriceFormatter:
    # Format price
    @staticmethod
    def Format(price: float,
               coin_vs: Optional[str] = None) -> str:
        coin_vs = coin_vs or ""
        space = " " if coin_vs not in ("$", "€") else ""

        if price >= 1000:
            return f"{price:.0f}{space}{coin_vs}"
        elif price >= 100:
            return f"{price:.1f}{space}{coin_vs}"
        elif price >= 1:
            return f"{price:.2f}{space}{coin_vs}"
        elif price >= 0.0001:
            return f"{price:.4f}{space}{coin_vs}"
        return f"{price:f}{space}{coin_vs}"


# Price change percentage formatter class
class PriceChangePercFormatter:
    # Format price change percentage
    @staticmethod
    def Format(price_change: float) -> str:
        return f"{'🔴' if price_change < 0 else '🟢'} {price_change:+.2f}%"


# Volume formatter class
class VolumeFormatter:
    # Format volume
    @staticmethod
    def Format(volume: int,
               coin_vs: Optional[str] = None) -> str:
        coin_vs = coin_vs or ""
        space = " " if coin_vs not in ("$", "€") else ""

        if volume > 1e9:
            return f"{volume / 1e9:.2f}B {coin_vs}"
        elif volume > 1e6:
            return f"{volume / 1e6:.2f}M {coin_vs}"
        return f"{volume:,}{space}{coin_vs}"
