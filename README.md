# Silence Detector

Silence Detector is a Python-based tool that monitors audio streams for silence events. It uses FFmpeg to process streams and send notifications using the Pushover API when silence is detected. The system automatically restarts FFmpeg processes every hour to ensure stability and performance.

## Features

- Monitors multiple audio streams for silence events.
- Sends notifications via Pushover when silence starts and ends.
- Automatically restarts FFmpeg processes every hour to maintain performance.
- Easily configurable using a `.env` file.
- Dockerized for easy deployment.

---

## Table of Contents

- [Installation](#installation)
- [Docker](#docker)
- [Configuration](#configuration)
- [Usage](#usage)
- [License](#license)

---

## Installation

### Prerequisites

- **Python 3.12 or higher**: Ensure you have Python installed on your machine.
- **FFmpeg**: You need to have FFmpeg installed and accessible in your system's `PATH`.
- **Pushover Account**: You need Pushover credentials to receive notifications.

### Step 1: Clone the repository

```bash
git clone https://github.com/bruijnes/silencedetector.git
cd silencedetector
```

### Step 2: Install dependencies

Install the required Python packages using `pip`:

```bash
pip install -r requirements.txt
```

Make sure FFmpeg is installed:

```bash
# On Ubuntu/Debian
sudo apt-get update
sudo apt-get install ffmpeg

# On MacOS (using Homebrew)
brew install ffmpeg
```

### Step 3: Create a `.env` file

You need to create a `.env` file with your stream information and Pushover credentials. Example:

```
URL1=https://stream.to.be/monitored
ID1=Example1
USER_KEY1=your_user_key_for_HD
APP_TOKEN1=your_app_token_for_HD
LOUDNESS1=-30
SILENCE_TIMEOUT1=5

URL2=https://stream.to.be/monitored
ID2=Example2
USER_KEY2=your_user_key_for_mobile
APP_TOKEN2=your_app_token_for_mobile
LOUDNESS2=-30
SILENCE_TIMEOUT2=5
```

### Step 4: Run the script

Once you’ve set up everything, run the Python script:

```bash
python silencedetector.py
```

---

## Docker

### Step 1: Build the Docker image

You can build the Docker image using the following command:

```bash
docker build -t silencedetector .
```

### Step 2: Run the Docker container

To run the container with the `.env` file:

```bash
docker run --env-file .env silencedetector
```

Alternatively, mount the `.env` file from your local directory:

```bash
docker run -v $(pwd)/.env:/usr/src/app/.env silencedetector
```

---

## Configuration

### .env File

All streams and related parameters are configured using the `.env` file.

- **URL**: The URL of the stream.
- **ID**: A unique identifier for the stream.
- **USER_KEY**: Your Pushover user key.
- **APP_TOKEN**: Your Pushover app token.
- **LOUDNESS**: Loudness level for FFmpeg silence detection.
- **SILENCE_TIMEOUT**: How long silence should be detected before being reported.

Example:

```bash
URL1=https://stream.to.be/monitored
ID1=Example1
USER_KEY1=your_user_key
APP_TOKEN1=your_app_token
LOUDNESS1=-30
SILENCE_TIMEOUT1=5
```

Any additional streams can be monitored using URL2, URL3, ULx and so on.

### Logs

All logs are stored in the `./log` directory. You can access them directly for any troubleshooting.

---

## Usage

After you’ve built and run the Docker container or installed the dependencies manually, the script will:

1. Start monitoring the streams for silence events.
2. Send a notification via Pushover when silence is detected and when it ends.
3. Automatically restart the FFmpeg processes every hour to ensure reliability.

To stop the container or process:

```bash
docker stop <container_id>
```

To view the logs inside the Docker container:

```bash
docker logs <container_id>
```

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

```
MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
```

---

## Contributions

Contributions, issues, and feature requests are welcome! Feel free to check out the [issues page](https://github.com/bruijnes/silencedetector/issues) if you want to contribute.

---

## Author

Developed by **bruijnes**.

