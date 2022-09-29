# Telegram Crypto Price Bot

[![PyPI version](https://badge.fury.io/py/telegram-crypto-price-bot.svg)](https://badge.fury.io/py/telegram-crypto-price-bot)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/e494ae8a0df847ca85dc72305bdb3ffa)](https://www.codacy.com/gh/ebellocchia/telegram_crypto_price_bot/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=ebellocchia/telegram_crypto_price_bot&amp;utm_campaign=Badge_Grade)
[![CodeFactor](https://www.codefactor.io/repository/github/ebellocchia/telegram_crypto_price_bot/badge)](https://www.codefactor.io/repository/github/ebellocchia/telegram_crypto_price_bot)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://raw.githubusercontent.com/ebellocchia/bip_utils/master/LICENSE)

Telegram bot for displaying cryptocurrencies prices and charts based on *pyrogram* and *matplotlib* libraries.\
Data is retrieved using CoinGecko APIs.\
It is possible to show coin information either on demand (by manually calling a command) or periodically using background tasks.\
A single bot instance can be used with multiple coins and in multiple groups.\
The usage of the bot is restricted to admins, in order to avoid users to flood the chat with price requests.

## Setup

### Create Telegram app

In order to use the bot, in addition to the bot token you also need an APP ID and hash.\
To get them, create an app using the following website: [https://my.telegram.org/apps](https://my.telegram.org/apps).

### Installation

The package requires Python 3, it is not compatible with Python 2.\
To install it:
- Using *setuptools*:

        python setup.py install

- Using *pip*:

        pip install telegram_crypto_price_bot

To run the bot, edit the configuration file by specifying the API ID/hash and bot token. Then, move to the *app* folder and run the *bot.py* script:

    cd app
    python bot.py

When run with no parameter, *conf/config.ini* will be the default configuration file (in this way it can be used for different groups).\
To specify a different configuration file:

    python bot.py -c another_conf.ini
    python bot.py --config another_conf.ini

Of course, the *app* folder can be moved elsewhere if needed.

## Configuration

An example of configuration file is provided in the *app/conf* folder.\
The list of all possible fields that can be set is shown below.

|Name|Description|
|---|---|
|**[pyrogram]**|Configuration for pyrogram|
|`session_name`|Session name of your choice|
|`api_id`|API ID from [https://my.telegram.org/apps](https://my.telegram.org/apps)|
|`api_hash`|API hash from [https://my.telegram.org/apps](https://my.telegram.org/apps)|
|`bot_token`|Bot token from BotFather|
|**[app]**|Configuration for app|
|`app_is_test_mode`|True to activate test mode false otherwise|
|`app_lang_file`|Language file in XML format (default: English)|
|**[task]**|Configuration for tasks|
|`tasks_max_num`|Maximum number of running tasks (totally, in all groups). Default: `20`.|
|**[chart]**|Configuration for price chart|
|`chart_display`|True to display price chart, false otherwise (default: true). If false, all the next fields will be skipped.|
|`chart_date_format`|Date format for price chart (default: `%%d/%%m/%%Y %%H:00`)|
|`chart_background_color`|Background color for price chart (default: `white`)|
|`chart_title_color`|Title color for price chart (default: `black`)|
|`chart_frame_color`|Frame color for price chart (default: `black`)|
|`chart_axes_color`|Axes color for price chart (default: `black`)|
|`chart_line_color`|Line color for price chart (default: `#3475AB`)|
|`chart_line_style`|Line style for price chart (default: `-`). Same as matplotlib line styles: `-` `--` `-.` `:`|
|`chart_line_width`|Line width for price chart (default: `1`)|
|`chart_display_grid`|True to display price chart grid, false otherwise (default: `true`). If false, all the next fields will be skipped.|
|`chart_grid_max_size`|Maximum size for price chart grid (default: `4`)|
|`chart_grid_color`|Line color for price chart grid (default: `#DFDFDF`)|
|`chart_grid_line_style`|Line style for price chart grid (default: `--`). Same as matplotlib line styles: `-` `--` `-.` `:`|
|`chart_grid_line_width`|Line width for price chart grid (default: `1`)|
|**[price]**|Configuration for price info|
|`price_display_market_cap`|True to display market cap, false otherwise (default: `true`)|
|`price_display_market_cap_rank`|True to display market cap rank, false otherwise (default: `false`)|
|**[logging]**|Configuration for logging|
|`log_level`|Log level, same of python logging (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`). Default: `INFO`.|
|`log_console_enabled`|True to enable logging to console, false otherwise (default: `true`)|
|`log_file_enabled`|True to enable logging to file, false otherwise (default: `false`). If false, all the next fields will be skipped.|
|`log_file_name`|Log file name|
|`log_file_use_rotating`|True for using a rotating log file, false otherwise|
|`log_file_max_bytes`|Maximum size in bytes for a log file. When reached, a new log file is created up to `log_file_backup_cnt`. Valid only if `log_file_use_rotating` is true.|
|`log_file_backup_cnt`|Maximum number of log files. Valid only if `log_file_use_rotating` is true.|
|`log_file_append`|True to append to log file, false to start from a new file each time. Valid only if `log_file_use_rotating` is false.|

All the colors can be either a name or a RGB color in format `#RRGGBB` (same as matplotlib colors).\
Chart and price configurations will be applied to all coin information in all groups. It's not possible to configure a single coin.

## Supported Commands

List of supported commands:
- `/help`: show this message
- `/alive`: show if bot is active
- `/pricebot_set_test_mode true/false`: enable/disable test mode
- `/pricebot_is_test_mode`: show if test mode is enabled
- `/pricebot_version`: show bot version
- `/pricebot_get_single COIN_ID COIN_VS LAST_DAYS [SAME_MSG]`: show chart and price information of the specified pair (single call).\
Parameters:
    - `COIN_ID`: CoinGecko *ID*
    - `COIN_VS`: CoinGecko *vs_currency*
    - `LAST_DAYS`: Last number of days to show price chart
    - `SAME_MSG` (optional): true for sending chart and price information in the same message (price information will be a caption of the chart image), false to send them in separate messages. Default value: true.
- `/pricebot_task_start PERIOD_HOURS START_HOUR COIN_ID COIN_VS LAST_DAYS`: start a price task in the current chat. If the task `COIN_ID/COIN_VS` already exists in the current chat, an error message will be shown. To start it again, it shall be stopped with the `pricebot_task_stop` command.\
Parameters:
    - `PERIOD_HOURS`: Task period in hours, it shall be between 1 and 24
    - `START_HOUR`: Task start hour, it shall be between 0 and 23
    - `COIN_ID`: CoinGecko *ID*
    - `COIN_VS`: CoinGecko *vs_currency*
    - `LAST_DAYS`: Last number of days to show price chart
- `/pricebot_task_stop COIN_ID COIN_VS`: stop the specified price task in the current chat. If the task `COIN_ID/COIN_VS` does not exist in the current chat, an error message will be shown.\
Parameters:
    - `COIN_ID`: CoinGecko *ID*
    - `COIN_VS`: CoinGecko *vs_currency*
- `/pricebot_task_stop_all`: stop all price tasks in the current chat
- `/pricebot_task_pause COIN_ID COIN_VS`: pause the specified price task in the current chat. If the task `COIN_ID/COIN_VS` does not exist in the current chat, an error message will be shown.\
Parameters:
    - `COIN_ID`: CoinGecko *ID*
    - `COIN_VS`: CoinGecko *vs_currency*
- `/pricebot_task_resume COIN_ID COIN_VS`: resume the specified price task in the current chat. If the task `COIN_ID/COIN_VS` does not exist in the current chat, an error message will be shown.\
Parameters:
    - `COIN_ID`: CoinGecko *ID*
    - `COIN_VS`: CoinGecko *vs_currency*
- `/pricebot_task_send_in_same_msg COIN_ID COIN_VS true/false`: enable/disable the sending of chart and price information in the same message. If the task `COIN_ID/COIN_VS` does not exist in the current chat, an error message will be shown.\
Parameters:
    - `COIN_ID`: CoinGecko *ID*
    - `COIN_VS`: CoinGecko *vs_currency*
    - `flag`: true for sending chart and price information in the same message (price information will be a caption of the chart image), false to send them in separate messages
- `/pricebot_task_delete_last_msg COIN_ID COIN_VS true/false`: enable/disable the deletion of last messages for the specified price task in the current chat. If the task `COIN_ID/COIN_VS` does not exist in the current chat, an error message will be shown.\
Parameters:
    - `COIN_ID`: CoinGecko *ID*
    - `COIN_VS`: CoinGecko *vs_currency*
    - `flag`: true or false
- `/pricebot_task_info`: show the list of active price tasks in the current chat

By default:
- a price task will send chart and price information in the same message. This can be enabled/disabled with the `pricebot_task_send_in_same_msg` command.
- a price task will delete the last sent message when sending a new one. This can be enabled/disabled with the `pricebot_task_delete_last_msg` command.

The task period starts from the specified starting hour (be sure to set the correct time on the VPS), for example:
- A task period of 8 hours starting from 00:00 will send the message at: 00:00, 08:00 and 16:00
- A task period of 6 hours starting from 08:00 will send the message at: 08:00, 14:00, 20:00 and 02:00

In case of API errors (e.g. network issues or invalid coin ID) an error message will be shown.

**Examples**

Show the price of BTC/USD of the last 14 days in the current chat (single call):

    /pricebot_get_single bitcoin usd 14

Show the price of ETH/BTC of the last 30 days periodically every 8 hours starting from 10:00 in the current chat:

    /pricebot_task_start 8 10 ethereum btc 30

Pause/Resume/Stop the previous task:

    /pricebot_task_pause ethereum btc
    /pricebot_task_resume ethereum btc
    /pricebot_task_stop ethereum btc

Set task so that it sends chart and price information in the same message:

    /pricebot_task_send_in_same_msg ethereum btc true

Set task so that it doesn't delete the last sent message:

    /pricebot_task_delete_last_msg ethereum btc false

## Run the Bot

It'd be better if the bot is an administrator of the group. This is mandatory if it needs to delete the last sent messages.\
In order to display prices periodically, the bot shall run 24h/24h so it's suggested to run it on a VPS (there is no performance requirements, so a cheap VPS will suffice).

## Test Mode

During test mode, the bot will work as usual but the task period will be applied in minutes instead of hours. This allows to quickly check if it is working.

## Translation

The messages sent by the bot on Telegram can be translated into different languages (the default language is English) by providing a custom XML file.\
The XML file path is specified in the configuration file (`app_lang_file` field).\
An example XML file in italian is provided in the folder *app/lang*.

## Image Examples

Example with chart and price information on different messages:

<img src="https://github.com/ebellocchia/telegram_crypto_price_bot/blob/master/img/example_diff_msg.png" width="500px">

Example with chart and price information on the same message:

<img src="https://github.com/ebellocchia/telegram_crypto_price_bot/blob/master/img/example_same_msg.png" width="500px">

# License

This software is available under the MIT license.
