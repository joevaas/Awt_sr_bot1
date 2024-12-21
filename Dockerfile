# Use the latest Python 3.11 image
FROM python:3.11

# Create and set permissions for the bot directory
RUN mkdir /bot && chmod 777 /bot
WORKDIR /bot

# Set environment variable to avoid interactive prompts during installs
ENV DEBIAN_FRONTEND=noninteractive

# Update package list and install dependencies
RUN apt -qq update && \
    apt -qq install -y --no-install-recommends \
    git wget pv jq python3-dev ffmpeg mediainfo neofetch fontconfig && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy bot files and install Python dependencies
COPY . .
RUN pip3 install --no-cache-dir -r requirements.txt

# Run the bot using the run.sh script
CMD ["python", "bot.py"]
