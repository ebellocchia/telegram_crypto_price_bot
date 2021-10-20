import os
import setuptools
import re


# Load long description
def load_long_description(desc_file):
    return open(desc_file).read()


# Load version
def load_version(*path_parts):
    version_file = os.path.join(*path_parts)
    version_line = open(os.path.join(*path_parts)).read().rstrip()
    vre = re.compile(r'__version__: str = "([^"]+)"')
    matches = vre.findall(version_line)

    if matches and len(matches) > 0:
        return matches[0]

    raise RuntimeError(f"Cannot find version string in {version_file}")


# Load requirements
def load_requirements(req_file):
    with open(req_file, "r") as fin:
        return [line for line in map(str.strip, fin.read().splitlines())
                if len(line) > 0 and not line.startswith("#")]


# Load version
version = load_version("telegram_crypto_price_bot", "_version.py")

setuptools.setup(
    name="telegram_crypto_price_bot",
    version=version,
    author="Emanuele Bellocchia",
    author_email="ebellocchia@gmail.com",
    maintainer="Emanuele Bellocchia",
    maintainer_email="ebellocchia@gmail.com",
    description="Telegram bot for displaying cryptocurrencies price",
    long_description=load_long_description("README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/ebellocchia/telegram_crypto_price_bot",
    download_url="https://github.com/ebellocchia/telegram_crypto_price_bot/archive/v%s.tar.gz" % version,
    license="MIT",
    install_requires=load_requirements("requirements.txt"),
    packages=setuptools.find_packages(exclude=[]),
    package_data={"telegram_crypto_price_bot": ["lang/lang_en.xml"]},
    keywords="telegram, bot, telegram bot, crypto, crypto prices, cryptocurrency, cryptocurrency prices",
    platforms=["any"],
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
