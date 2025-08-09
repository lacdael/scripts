#!/usr/bin/env python3
import sys
import os
import time

# --- Configuration ---
SAMPLE_FILES = [
    'kick.wav', 'snare.wav', 'hihat.wav',
    'kick.wav', 'snare.wav', 'hihat.wav',
    'kick.wav', 'snare.wav'
]
VELOCITY_HIGH = 1.0
VELOCITY_LOW = 0.6

# --- Initialization ---
try:
    import pygame
except ImportError:
    print("Error: The 'pygame' library is required. Please install it by running:", file=sys.stderr)
    print("pip install pygame", file=sys.stderr)
    sys.exit(1)

pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

samples = []
missing_files = False
for i, filename in enumerate(SAMPLE_FILES):
    if not os.path.exists(filename):
        print(f"Warning: Sound file for row {i} not found: {filename}", file=sys.stderr)
        missing_files = True
        samples.append(None)
    else:
        samples.append(pygame.mixer.Sound(filename))

if missing_files:
    print("\nWarning: Some sound files are missing.", file=sys.stderr)
    time.sleep(3)

# --- Main Loop ---
def main():
    """
    Reads drum_wfc output from stdin and plays the corresponding sounds.
    """
    print("Audio player started. Waiting for input from drum_wfc...", file=sys.stderr)
    print("Example: ./build/drum_wfc -c | ./pythonPlay.py", file=sys.stderr)
    print("Press Ctrl+C to exit.", file=sys.stderr)

    try:
        while True:
            line = sys.stdin.readline()
            if not line:
                break  # End of stream (Ctrl+D or program finishes)

            try:
                parts = line.strip().split(':')
                if len(parts) < 2:
                    continue

                pattern_str = parts[1].strip()
                if len(pattern_str) != 8:
                    continue
                print( pattern_str );
                for i, char in enumerate(pattern_str):
                    if samples[i] is None:
                        continue

                    if char == 'x':
                        samples[i].set_volume(VELOCITY_LOW)
                        samples[i].play()
                    elif char == 'X':
                        samples[i].set_volume(VELOCITY_HIGH)
                        samples[i].play()

            except Exception as e:
                print(f"Error processing line: {line.strip()} -> {e}", file=sys.stderr)

    except KeyboardInterrupt:
        print("\nExiting player.", file=sys.stderr)
    finally:
        pygame.mixer.quit()

if __name__ == "__main__":
    main()
