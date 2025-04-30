#!/bin/bash

# Ensure the correct number of arguments
if [ "$#" -ne 4 ]; then
    echo "Usage: $0 input_audio output_audio start duration"
    exit 1
fi

# Define inputs
input_audio="$1"
output_audio="$2"
start_time="$3"
duration="$4"

# Validate duration (must be at least 6 seconds for proper fades)
if (( $(echo "$duration < 6" | bc -l) )); then
    echo "Error: Duration must be at least 6 seconds."
    exit 1
fi

# Define fade parameters
fade_duration=4
fade_out_start=$(echo "$duration - $fade_duration" | bc -l)

# Temporary file
loop_faded="loop_faded.wav"

# Step 1: Extract the main segment and apply fades
ffmpeg -y -i "$input_audio" -ss "$start_time" -t "$duration" \
    -af "afade=t=in:ss=0:d=$fade_duration,afade=t=out:st=$fade_out_start:d=$fade_duration" \
    -acodec pcm_s16le "$loop_faded"

if [ $? -ne 0 ]; then
    echo "Error applying fade effects."
    exit 1
fi

# Move the final output
mv "$loop_faded" "$output_audio"

echo "Processed file saved as: $output_audio"
