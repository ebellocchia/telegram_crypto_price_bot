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

import os
import secrets
import string
from datetime import datetime
from threading import Lock
from typing import Optional

import matplotlib
from matplotlib import pyplot as plt

from telegram_crypto_price_bot.bot.bot_config_types import BotConfigTypes
from telegram_crypto_price_bot.chart_info.chart_info import ChartInfo
from telegram_crypto_price_bot.config.config_object import ConfigObject
from telegram_crypto_price_bot.logger.logger import Logger
from telegram_crypto_price_bot.misc.formatters import CoinIdFormatter, PriceFormatter
from telegram_crypto_price_bot.translation.translation_loader import TranslationLoader
from telegram_crypto_price_bot.utils.utils import Synchronized


# Disable matplotlib GUI
matplotlib.use("Agg")
# Lock for thread safety when creating charts
plot_lock: Lock = Lock()


class ChartInfoFileSaverConst:
    """Constants for chart info file saver class."""

    CHART_IMG_EXT: str = ".png"
    TMP_FILE_NAME_LEN: int = 16


class ChartInfoFileSaver:
    """Class for saving chart information to files."""

    config: ConfigObject
    translator: TranslationLoader

    def __init__(self,
                 config: ConfigObject,
                 translator: TranslationLoader) -> None:
        """
        Initialize the chart info file saver.

        Args:
            config: Configuration object containing chart settings.
            translator: Translation loader for internationalization.
        """
        self.config = config
        self.translator = translator

    @Synchronized(plot_lock)
    def SaveToFile(self,
                   chart_info: ChartInfo,
                   file_name: str) -> None:
        """
        Save chart to a file.

        Args:
            chart_info: Chart information to plot and save
            file_name: Path to save the chart image
        """
        fig, ax = plt.subplots()

        self.__SetAxesFormatter(ax)
        self.__SetBackgroundColor(fig, ax)
        self.__SetAxesColor(ax)
        self.__SetFrameColor(ax)
        self.__SetGrid(ax)
        self.__SetTitle(chart_info, ax)
        self.__Plot(chart_info, fig, ax)
        self.__SaveAndClose(fig, file_name)

    def __SetAxesFormatter(self,
                           ax: plt.axes) -> None:
        """
        Set formatting for chart axes.

        Args:
            ax: Matplotlib axes object to configure.
        """
        date_format = self.config.GetValue(BotConfigTypes.CHART_DATE_FORMAT)
        grid_max_size = self.config.GetValue(BotConfigTypes.CHART_GRID_MAX_SIZE)

        ax.xaxis.set_major_locator(plt.MaxNLocator(grid_max_size))
        ax.xaxis.set_major_formatter(
            matplotlib.ticker.FuncFormatter(lambda x, p: datetime.fromtimestamp(int(x)).strftime(date_format))
        )
        ax.yaxis.set_major_formatter(
            matplotlib.ticker.FuncFormatter(lambda x, p: PriceFormatter.Format(x))
        )

    def __SetBackgroundColor(self,
                             fig: plt.figure,
                             ax: plt.axes) -> None:
        """
        Set background color for the chart.

        Args:
            fig: Matplotlib figure object.
            ax: Matplotlib axes object.
        """
        bckg_color = self.config.GetValue(BotConfigTypes.CHART_BACKGROUND_COLOR)

        fig.patch.set_facecolor(bckg_color)
        ax.set_facecolor(bckg_color)

    def __SetAxesColor(self,
                       ax: plt.axes) -> None:
        """
        Set color for chart axes.

        Args:
            ax: Matplotlib axes object to configure.
        """
        axes_color = self.config.GetValue(BotConfigTypes.CHART_AXES_COLOR)

        ax.tick_params(color=axes_color, labelcolor=axes_color)

    def __SetFrameColor(self,
                        ax: plt.axes) -> None:
        """
        Set color for chart frame.

        Args:
            ax: Matplotlib axes object to configure.
        """
        frame_color = self.config.GetValue(BotConfigTypes.CHART_FRAME_COLOR)

        for spine in ax.spines.values():
            spine.set_edgecolor(frame_color)

    def __SetGrid(self,
                  ax: plt.axes) -> None:
        """
        Set grid configuration for the chart.

        Args:
            ax: Matplotlib axes object to configure.
        """
        display_grid = self.config.GetValue(BotConfigTypes.CHART_DISPLAY_GRID)
        grid_color = self.config.GetValue(BotConfigTypes.CHART_GRID_COLOR)
        grid_line_style = self.config.GetValue(BotConfigTypes.CHART_GRID_LINE_STYLE)
        grid_line_width = self.config.GetValue(BotConfigTypes.CHART_GRID_LINE_WIDTH)

        ax.grid(display_grid, color=grid_color, linestyle=grid_line_style, linewidth=grid_line_width)

    def __SetTitle(self,
                   chart_info: ChartInfo,
                   ax: plt.axes) -> None:
        """
        Set title for the chart.

        Args:
            chart_info: Chart information containing coin details.
            ax: Matplotlib axes object to configure.
        """
        title_color = self.config.GetValue(BotConfigTypes.CHART_TITLE_COLOR)

        ax.set_title(
            self.translator.GetSentence(
                "CHART_INFO_TITLE_MSG",
                coin_id=CoinIdFormatter.Format(chart_info.CoinId()),
                coin_vs=chart_info.CoinVs().upper(),
                last_days=chart_info.LastDays(),
            ),
            color=title_color,
        )

    def __Plot(self,
               chart_info: ChartInfo,
               fig: plt.figure,
               ax: plt.axes) -> None:
        """
        Plot the chart data.

        Args:
            chart_info: Chart information to plot.
            fig: Matplotlib figure object.
            ax: Matplotlib axes object.
        """
        line_color = self.config.GetValue(BotConfigTypes.CHART_LINE_COLOR)
        line_style = self.config.GetValue(BotConfigTypes.CHART_LINE_STYLE)
        line_width = self.config.GetValue(BotConfigTypes.CHART_LINE_WIDTH)

        ax.plot(chart_info.X(), chart_info.Y(), color=line_color, linestyle=line_style, linewidth=line_width)
        fig.autofmt_xdate()

    @staticmethod
    def __SaveAndClose(fig: plt.figure,
                       file_name: str) -> None:
        """
        Save figure to file and close it.

        Args:
            fig: Matplotlib figure object to save.
            file_name: Path to save the figure.
        """
        fig.savefig(file_name, bbox_inches="tight")
        plt.close(fig)


class ChartInfoTmpFileSaver:
    """Class for saving chart information to temporary files."""

    logger: Logger
    tmp_file_name: Optional[str]
    chart_info_file_saver: ChartInfoFileSaver

    def __init__(self,
                 config: ConfigObject,
                 logger: Logger,
                 translator: TranslationLoader) -> None:
        """
        Initialize the temporary chart file saver.

        Args:
            config: Configuration object containing chart settings.
            logger: Logger instance for logging operations.
            translator: Translation loader for internationalization.
        """
        self.logger = logger
        self.tmp_file_name = None
        self.chart_info_file_saver = ChartInfoFileSaver(config, translator)

    def __del__(self):
        """Clean up temporary files on object destruction."""
        self.DeleteTmpFile()

    def SaveToTmpFile(self,
                      chart_info: ChartInfo) -> None:
        """
        Save chart to a temporary file.

        Args:
            chart_info: Chart information to save.
        """
        self.DeleteTmpFile()
        self.tmp_file_name = self.__NewTmpFileName()
        self.chart_info_file_saver.SaveToFile(chart_info, self.tmp_file_name)
        self.logger.GetLogger().info(
            f"Saved chart information for coin {chart_info.CoinId()}/{chart_info.CoinVs()}, "
            f"last days {chart_info.LastDays()}, number of points ({len(chart_info.X())}, {len(chart_info.Y())}), "
            f'file name: "{self.tmp_file_name}"'
        )

    def TmpFileName(self) -> Optional[str]:
        """
        Get the temporary file name.

        Returns:
            The temporary file name or None if no file exists.
        """
        return self.tmp_file_name

    def DeleteTmpFile(self) -> None:
        """Delete the temporary chart file if it exists."""
        if self.tmp_file_name is not None:
            try:
                os.remove(self.tmp_file_name)
                self.logger.GetLogger().info(f'Deleted chart file "{self.tmp_file_name}"')
            except FileNotFoundError:
                pass
            finally:
                self.tmp_file_name = None

    @staticmethod
    def __NewTmpFileName() -> str:
        """
        Generate a new temporary file name.

        Returns:
            A new temporary file name with chart image extension.
        """
        tmp_name = "".join(
            secrets.choice(string.ascii_letters + string.digits) for _ in range(ChartInfoFileSaverConst.TMP_FILE_NAME_LEN)
        )
        return f"{tmp_name}{ChartInfoFileSaverConst.CHART_IMG_EXT}"
