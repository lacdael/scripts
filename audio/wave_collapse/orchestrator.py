#!/usr/bin/env python3
import sys
import os
import time
import subprocess

# --- Configuration ---
# Add the filenames of the patterns you want to layer here
PATTERN_FILES = [
    'pattern1.txt',
    'pattern2.txt',
    'example.txt' # Using the original example file as a third layer
]

# Sequencer settings
BPM = 120.0
NOTES_PER_BEAT = 4  # 16th notes
STEP_DELAY = 60.0 / BPM / NOTES_PER_BEAT

# Audio settings
SAMPLE_FILES = [
    'kick.wav', 'snare.wav', 'hihat.wav', 'kick.wav',
    'snare.wav', 'hihat.wav', 'kick.wav', 'snare.wav'
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
for i, filename in enumerate(SAMPLE_FILES):
    if not os.path.exists(filename):
        print(f"Warning: Sound file for row {i} not found: {filename}", file=sys.stderr)
        samples.append(None)
    else:
        samples.append(pygame.mixer.Sound(filename))

# --- Main Application ---
def main():
    print("Starting orchestrator...", file=sys.stderr)
    processes = []
    
    # 1. Start a subprocess for each pattern file
    for pattern_file in PATTERN_FILES:
        if not os.path.exists(pattern_file):
            print(f"Warning: Pattern file not found, skipping: {pattern_file}", file=sys.stderr)
            continue
        
        command = ['./build/drum_wfc', '-f', pattern_file, '-i']
        print(f"Starting process: {' '.join(command)}", file=sys.stderr)
        
        proc = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, # Capture stderr to see generator status
            text=True
        )
        processes.append(proc)

    if not processes:
        print("Error: No valid pattern files found. Exiting.", file=sys.stderr)
        return

    # Read initial "Generator running..." message from stderr of each process
    time.sleep(0.1) # Give processes a moment to start and print
    for proc in processes:
        line = proc.stderr.readline().strip()
        if line:
            print(f"[{proc.pid}]: {line}", file=sys.stderr)

    print("\n--- Sequencer Running ---", file=sys.stderr)
    print(f"BPM: {BPM}, Step Delay: {STEP_DELAY:.4f}s", file=sys.stderr)
    print("Press Ctrl+C to exit.", file=sys.stderr)

    try:
        # 2. Run the master clock loop
        while True:
            # Tell all processes to generate their next step
            for proc in processes:
                proc.stdin.write('\n')
                proc.stdin.flush()

            # Read the generated line from each process
            lines = [proc.stdout.readline() for proc in processes]

            # Combine the patterns
            final_pattern = ['-'] * 8
            for line in lines:
                parts = line.strip().split(':')
                if len(parts) < 2: continue
                pattern_str = parts[1].strip()
                
                for i, char in enumerate(pattern_str):
                    if char == 'X':
                        final_pattern[i] = 'X'
                    elif char == 'x' and final_pattern[i] != 'X':
                        final_pattern[i] = 'x'
            
            # Play the combined pattern
            print( final_pattern );
            for i, char in enumerate(final_pattern):
                if samples[i]:
                    if char == 'x':
                        samples[i].set_volume(VELOCITY_LOW)
                        samples[i].play()
                    elif char == 'X':
                        samples[i].set_volume(VELOCITY_HIGH)
                        samples[i].play()
            
            # Wait for the next step
            time.sleep(STEP_DELAY)

    except KeyboardInterrupt:
        print("\nStopping sequencer and child processes...", file=sys.stderr)
    finally:
        for proc in processes:
            proc.terminate() # Cleanly stop the subprocesses
        pygame.mixer.quit()
        print("Done.", file=sys.stderr)


if __name__ == "__main__":
    main()
