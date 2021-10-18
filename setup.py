import setuptools
import re

VERSION_FILE = "telegram_crypto_price_bot/_version.py"

with open("README.md", "r") as f:
    long_description = f.read()

def load_version():
    version_line = open(VERSION_FILE).read().rstrip()
    vre = re.compile(r'__version__: str = "([^"]+)"')
    matches = vre.findall(version_line)

    if matches and len(matches) > 0:
        return matches[0]
    else:
        raise RuntimeError("Cannot find version string in %s" % VERSION_FILE)

version = load_version()

setuptools.setup(
    name="telegram_crypto_price_bot",
    version=version,
    author="Emanuele Bellocchia",
    author_email="ebellocchia@gmail.com",
    maintainer="Emanuele Bellocchia",
    maintainer_email="ebellocchia@gmail.com",
    description="Telegram bot for displaying cryptocurrencies price",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ebellocchia/telegram_crypto_price_bot",
    download_url="https://github.com/ebellocchia/telegram_crypto_price_bot/archive/v%s.tar.gz" % version,
    license="MIT",
    install_requires = ["pycoingecko", "matplotlib", "pyrogram", "tgcrypto", "apscheduler"],
    packages=setuptools.find_packages(exclude=[]),
    package_data={"telegram_crypto_price_bot": ["lang/lang_en.xml"]},
    keywords="telegram, bot, telegram bot, crypto, crypto prices, cryptocurrency, cryptocurrency prices",
    platforms = ["any"],
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
    ],
    python_requires=">=3.7",
)
