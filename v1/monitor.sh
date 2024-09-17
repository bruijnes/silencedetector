#!/bin/sh

#################
### VARIABLES ###
#################

user_key="$USER_KEY"
app_token="$APP_TOKEN"
loudness="$LOUDNESS"
silence_timeout="$SILENCE_TIMEOUT"

  #################
  ### FUNCTIONS ###
  #################

  # Function to monitor output file for silence_start event
  monitor_silence_start() {
    sleep 2
    local identifier=$1
    local output_file="${identifier}_output.log"

    # Monitor the output file for silence_start event
    tail -n 0 -F "${output_file}" | grep --line-buffered "silence_start" | while read -r line
    do
      echo "Silence started for $identifier at $(date '+%Y-%m-%d %H:%M:%S')"

      # Add your action for silence_start event here
      # For example, send a notification using Pushover with priority set to 2 and additional parameters
      send_pushover "$identifier" "Silence started for $identifier at $(date '+%Y-%m-%d %H:%M:%S')" 2 3600 60
    done
  }

  # Function to monitor output file for silence_end event
  monitor_silence_end() {
    sleep 2
    local identifier=$1
    local output_file="${identifier}_output.log"

    # Monitor the output file for silence_end event
    tail -n 0 -F "${output_file}" | grep --line-buffered "silence_end" | while read -r line
    do
      echo "Silence ended for $identifier at $(date '+%Y-%m-%d %H:%M:%S')"

      # Add your action for silence_end event here
      # For example, cancel the Pushover notification with the corresponding identifier
      cancel_pushover_by_tag "$identifier"
    done
  }

  # Function to send a Pushover notification with optional parameters
  send_pushover() {
    local identifier=$1
    local message=$2
    local priority=${3:-0}  # Default priority is set to 0 (Normal)
    local expire=${4:-0}    # Default expire is set to 0 (No expiration)
    local retry=${5:-0}     # Default retry is set to 0 (No retry)

    # Send the notification with optional parameters
    curl -s \
      --form-string "token=${app_token}" \
      --form-string "user=${user_key}" \
      --form-string "message=${message}" \
      --form-string "priority=${priority}" \
      --form-string "expire=${expire}" \
      --form-string "retry=${retry}" \
      --form-string "tags=${identifier}" \
      https://api.pushover.net/1/messages.json
  }

  # Function to cancel a Pushover notification by tag (identifier)
  cancel_pushover_by_tag() {
    local identifier=$1

    # Cancel the notification by tag (identifier)
    curl -s \
      --form-string "token=${app_token}" \
      --form-string "user=${user_key}" \
      https://api.pushover.net/1/receipts/cancel_by_tag/${identifier}.json
  }

  ##################
  ### THE SCRIPT ###
  ##################

# Convert the string to an array-like structure
IFS="|"
for stream in $STREAMS; do
  IFS="," read -r url identifier <<EOF
$stream
EOF

    # Set other variables
    output_file="${identifier}_output.log"
    pid_file="${identifier}.pid"

    # Execute the ffmpeg command in the background and capture the PID
    ffmpeg -i "$url" -hide_banner -af silencedetect=n="${loudness}"dB:d="${silence_timeout}" -f null - > "${output_file}" 2>&1 &
    pid=$!

    # Save the PID to a file
    echo "$pid" > "${pid_file}"

    echo "$identifier stream is running in the background. PID: $pid"

    # Start monitoring for silence_start and silence_end events
    monitor_silence_start "$identifier" &
    monitor_silence_end "$identifier" &
  done

  # Wait for background processes to finish
  wait