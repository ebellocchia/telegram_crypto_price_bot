FROM python:3.13-slim

# Prevent Python from writing .pyc files and enable real-time logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /code/app

# Install system dependencies required for compiling C-based Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Install package
COPY . .
RUN pip install --no-cache-dir .

# Start bot
WORKDIR app
CMD exec python bot_start.py -c ${CONFIG_FILE:-conf/config.ini}
