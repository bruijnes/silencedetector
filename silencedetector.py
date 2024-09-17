import subprocess
import threading
import time
import requests
import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Ensure the log directory exists
log_directory = "./log"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# Setup logging to file and console
log_file = os.path.join(log_directory, 'silencedetector.log')
logging.basicConfig(
    level=logging.DEBUG,  # Change to logging.INFO to reduce verbosity
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Logs to the console
        logging.FileHandler(log_file)  # Logs to a file in ./log
    ]
)

# Global dictionary to keep track of FFmpeg processes and their threads
ffmpeg_processes = {}

# Function to get streams, user keys, app tokens, loudness, and silence timeout from environment variables
def get_streams():
    streams = []
    index = 1
    while True:
        url = os.getenv(f"URL{index}")
        identifier = os.getenv(f"ID{index}")
        user_key = os.getenv(f"USER_KEY{index}")
        app_token = os.getenv(f"APP_TOKEN{index}")
        loudness = os.getenv(f"LOUDNESS{index}", "-30")  # Default loudness is -30 if not provided
        silence_timeout = os.getenv(f"SILENCE_TIMEOUT{index}", "5")  # Default silence timeout is 5 seconds

        if url and identifier and user_key and app_token:
            streams.append((url, identifier, user_key, app_token, loudness, silence_timeout))
            logging.info(f"Stream {identifier} added with URL {url}, Loudness {loudness}, Silence Timeout {silence_timeout}")
            index += 1
        else:
            if index == 1:
                logging.error("No streams found in the .env file!")
            break
    return streams

# Function to send a Pushover notification with optional parameters
def send_pushover(identifier, message, url, user_key, app_token, priority=0, expire=0, retry=0):
    payload = {
        'token': app_token,
        'user': user_key,
        'message': message,
        'url': url,
        'priority': priority,
        'expire': expire,
        'retry': retry,
        'tags': identifier
    }
    try:
        response = requests.post('https://api.pushover.net/1/messages.json', data=payload)
        if response.status_code == 200:
            logging.info(f"Notification sent: {message} for {identifier}")
        else:
            logging.error(f"Failed to send notification for {identifier}. Status code: {response.status_code}")
    except requests.RequestException as e:
        logging.error(f"Error sending Pushover notification for {identifier}: {e}")

# Function to cancel a Pushover notification by tag (identifier)
def cancel_pushover_by_tag(identifier, user_key, app_token):
    try:
        response = requests.post(f'https://api.pushover.net/1/receipts/cancel_by_tag/{identifier}.json', data={
            'token': app_token,
            'user': user_key
        })
        if response.status_code == 200:
            logging.info(f"Notification canceled for {identifier}")
        else:
            logging.error(f"Failed to cancel notification for {identifier}. Status code: {response.status_code}")
    except requests.RequestException as e:
        logging.error(f"Error canceling Pushover notification for {identifier}: {e}")

# Function to capture and monitor ffmpeg output for silence events
def monitor_ffmpeg_process(proc, url, identifier, user_key, app_token):
    logging.info(f"Monitoring FFmpeg output for {identifier}")
    for line in iter(proc.stderr.readline, b''):
        decoded_line = line.decode('utf-8').strip()
        logging.debug(f"{identifier} FFmpeg output: {decoded_line}")
        
        if "silence_start" in decoded_line:
            logging.info(f"Silence started for {identifier}")
            send_pushover(identifier, f"Silence started for {identifier} at {time.strftime('%Y-%m-%d %H:%M:%S')}", url, user_key, app_token, priority=2, expire=3600, retry=60)
        elif "silence_end" in decoded_line:
            logging.info(f"Silence ended for {identifier}")
            cancel_pushover_by_tag(identifier, user_key, app_token)
            send_pushover(identifier, f"Audio started for {identifier} at {time.strftime('%Y-%m-%d %H:%M:%S')}", url, user_key, app_token, priority=1)

# Function to start the ffmpeg process and capture its output
def start_ffmpeg_process(url, identifier, user_key, app_token, loudness, silence_timeout):
    # Execute the ffmpeg command
    ffmpeg_command = [
        'ffmpeg', '-i', url, '-hide_banner', 
        '-af', f'silencedetect=n={loudness}dB:d={silence_timeout}',
        '-f', 'null', '-'
    ]

    logging.info(f"Starting FFmpeg for {identifier} with PID: {os.getpid()}")
    proc = subprocess.Popen(ffmpeg_command, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    
    # Start monitoring the ffmpeg output in a thread
    monitor_thread = threading.Thread(target=monitor_ffmpeg_process, args=(proc, identifier, url, user_key, app_token), daemon=True)
    monitor_thread.start()

    ffmpeg_processes[identifier] = (proc, monitor_thread)
    return proc

# Function to stop the ffmpeg process
def stop_ffmpeg_process(identifier):
    proc, monitor_thread = ffmpeg_processes.get(identifier, (None, None))
    if proc:
        proc.terminate()
        proc.wait()  # Ensure the process has fully stopped
        logging.info(f"FFmpeg process for {identifier} terminated.")

# Function to restart the ffmpeg process every hour
def restart_processes():
    while True:
        time.sleep(3600)  # Wait for 1 hour
        logging.info("Restarting all FFmpeg processes to ensure performance.")
        for identifier in ffmpeg_processes:
            # Stop the current process
            stop_ffmpeg_process(identifier)
            
            # Restart the process with the original parameters
            url, identifier, user_key, app_token, loudness, silence_timeout = get_stream_by_identifier(identifier)
            start_ffmpeg_process(url, identifier, user_key, app_token, loudness, silence_timeout)

# Helper function to retrieve stream info by identifier
def get_stream_by_identifier(identifier):
    for stream in get_streams():
        if stream[1] == identifier:
            return stream
    return None

# MAIN SCRIPT
def main():
    streams = get_streams()

    if not streams:
        logging.error("No valid streams were found. Exiting.")
        return

    for url, identifier, user_key, app_token, loudness, silence_timeout in streams:
        start_ffmpeg_process(url, identifier, user_key, app_token, loudness, silence_timeout)

    # Start the restart thread
    restart_thread = threading.Thread(target=restart_processes, daemon=True)
    restart_thread.start()

    # Keep the main thread running as long as the subprocesses are alive
    while threading.active_count() > 1:
        time.sleep(1)

if __name__ == "__main__":
    logging.info("Starting Silence Detector with automatic hourly restarts...")
    main()
    logging.info("Silence Detector stopped.")
