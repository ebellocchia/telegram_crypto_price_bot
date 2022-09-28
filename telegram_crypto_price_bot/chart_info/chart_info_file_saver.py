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
import os
import tempfile
from datetime import datetime
from threading import Lock
from typing import Optional

import matplotlib
from matplotlib import pyplot as plt

from telegram_crypto_price_bot.bot.bot_config import BotConfigTypes
from telegram_crypto_price_bot.chart_info.chart_info import ChartInfo
from telegram_crypto_price_bot.config.config_object import ConfigObject
from telegram_crypto_price_bot.logger.logger import Logger
from telegram_crypto_price_bot.misc.formatters import CoinIdFormatter, PriceFormatter
from telegram_crypto_price_bot.translation.translation_loader import TranslationLoader
from telegram_crypto_price_bot.utils.utils import Synchronized


#
# Variables
#

# Lock for plotting charts, since matplotlib works only in single thread
plot_lock: Lock = Lock()


#
# Classes
#

# Constants for chart info file saver class
class ChartInfoFileSaverConst:
    # Chart image extension
    CHART_IMG_EXT: str = ".png"


# Chart info file saver class
class ChartInfoFileSaver:

    config: ConfigObject
    translator: TranslationLoader

    # Constructor
    def __init__(self,
                 config: ConfigObject,
                 translator: TranslationLoader) -> None:
        self.config = config
        self.translator = translator

    # Save chart to file
    @Synchronized(plot_lock)
    def SaveToFile(self,
                   chart_info: ChartInfo,
                   file_name: str) -> None:
        # Create subplot
        fig, ax = plt.subplots()

        # Configure plot
        self.__SetAxesFormatter(ax)
        self.__SetBackgroundColor(fig, ax)
        self.__SetAxesColor(ax)
        self.__SetFrameColor(ax)
        self.__SetGrid(ax)
        self.__SetTitle(chart_info)
        # Plot
        self.__Plot(chart_info, fig, ax)
        # Save to file and close figure
        self.__SaveAndClose(fig, file_name)

    # Set axes formatter
    def __SetAxesFormatter(self,
                           ax: plt.axes) -> None:
        date_format = self.config.GetValue(BotConfigTypes.CHART_DATE_FORMAT)
        grid_max_size = self.config.GetValue(BotConfigTypes.CHART_GRID_MAX_SIZE)

        ax.xaxis.set_major_locator(plt.MaxNLocator(grid_max_size))
        ax.xaxis.set_major_formatter(
            matplotlib.ticker.FuncFormatter(
                lambda x, p: datetime.fromtimestamp(int(x)).strftime(date_format)
            )
        )
        ax.yaxis.set_major_formatter(
            matplotlib.ticker.FuncFormatter(lambda x, p: PriceFormatter.Format(x))
        )

    # Set background color
    def __SetBackgroundColor(self,
                             fig: plt.figure,
                             ax: plt.axes) -> None:
        bckg_color = self.config.GetValue(BotConfigTypes.CHART_BACKGROUND_COLOR)

        fig.patch.set_facecolor(bckg_color)
        ax.set_facecolor(bckg_color)

    # Set axes color
    def __SetAxesColor(self,
                       ax: plt.axes) -> None:
        axes_color = self.config.GetValue(BotConfigTypes.CHART_AXES_COLOR)

        ax.tick_params(color=axes_color,
                       labelcolor=axes_color)

    # Set frame color
    def __SetFrameColor(self,
                        ax: plt.axes) -> None:
        frame_color = self.config.GetValue(BotConfigTypes.CHART_FRAME_COLOR)

        for spine in ax.spines.values():
            spine.set_edgecolor(frame_color)

    # Set grid
    def __SetGrid(self,
                  ax: plt.axes) -> None:
        display_grid = self.config.GetValue(BotConfigTypes.CHART_DISPLAY_GRID)
        grid_color = self.config.GetValue(BotConfigTypes.CHART_GRID_COLOR)
        grid_line_style = self.config.GetValue(BotConfigTypes.CHART_GRID_LINE_STYLE)
        grid_line_width = self.config.GetValue(BotConfigTypes.CHART_GRID_LINE_WIDTH)

        ax.grid(display_grid,
                color=grid_color,
                linestyle=grid_line_style,
                linewidth=grid_line_width)

    # Set title
    def __SetTitle(self,
                   chart_info: ChartInfo) -> None:
        title_color = self.config.GetValue(BotConfigTypes.CHART_TITLE_COLOR)

        plt.title(
            self.translator.GetSentence("CHART_INFO_TITLE_MSG",
                                        coin_id=CoinIdFormatter.Format(chart_info.CoinId()),
                                        coin_vs=chart_info.CoinVs().upper(),
                                        last_days=chart_info.LastDays()),
            color=title_color
        )

    # Plot
    def __Plot(self,
               chart_info: ChartInfo,
               fig: plt.figure,
               ax: plt.axes) -> None:
        line_color = self.config.GetValue(BotConfigTypes.CHART_LINE_COLOR)
        line_style = self.config.GetValue(BotConfigTypes.CHART_LINE_STYLE)
        line_width = self.config.GetValue(BotConfigTypes.CHART_LINE_WIDTH)

        # Plot
        ax.plot(chart_info.X(),
                chart_info.Y(),
                color=line_color,
                linestyle=line_style,
                linewidth=line_width)
        # Rotate and align dates
        fig.autofmt_xdate()

    # Save to file and close
    @staticmethod
    def __SaveAndClose(fig: plt.figure,
                       file_name: str) -> None:
        plt.savefig(file_name, bbox_inches="tight")
        plt.close(fig)


# Chart info temporary file saver class
class ChartInfoTmpFileSaver:

    logger: Logger
    tmp_file_name: Optional[str]
    chart_info_file_saver: ChartInfoFileSaver

    # Constructor
    def __init__(self,
                 config: ConfigObject,
                 logger: Logger,
                 translator: TranslationLoader) -> None:
        self.logger = logger
        self.tmp_file_name = None
        self.chart_info_file_saver = ChartInfoFileSaver(config, translator)

    # Destructor
    def __del__(self):
        self.DeleteTmpFile()

    # Save chart to temporary file
    def SaveToTmpFile(self,
                      chart_info: ChartInfo) -> None:
        # Delete old file
        self.DeleteTmpFile()
        # Save new file
        self.tmp_file_name = self.__NewTmpFileName()
        self.chart_info_file_saver.SaveToFile(chart_info,
                                              self.tmp_file_name)
        # Log
        self.logger.GetLogger().info(
            f"Saved chart information for coin {chart_info.CoinId()}/{chart_info.CoinVs()}, "
            f"last days {chart_info.LastDays()}, number of points ({len(chart_info.X())}, {len(chart_info.Y())}), "
            f"file name: \"{self.tmp_file_name}\""
        )

    # Get temporary file name
    def TmpFileName(self) -> Optional[str]:
        return self.tmp_file_name

    # Delete temporary file
    def DeleteTmpFile(self) -> None:
        if self.tmp_file_name is not None:
            try:
                os.remove(self.tmp_file_name)
                self.logger.GetLogger().info(f"Deleted chart file \"{self.tmp_file_name}\"")
            except FileNotFoundError:
                pass
            finally:
                self.tmp_file_name = None

    # Get new temporary file name
    @staticmethod
    def __NewTmpFileName() -> str:
        return f"{next(tempfile._get_candidate_names())}{ChartInfoFileSaverConst.CHART_IMG_EXT}"    # type: ignore # noqa
