import sounddevice as sd  # <== ADD THIS
import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt, lfilter, fftconvolve
from collections import deque
import argparse

# --- Globals for audio playback ---
record_buffer = []
record_enabled = False
callback = None
looped_audio = None
looped_audio_len = 0
position = 0
BUFFER_SIZE = 2048


def ensure_2d(data):
    """Ensure that the audio data is a 2D array (n_samples, n_channels)."""
    return data if data.ndim > 1 else data[:, np.newaxis]


def draw_equalizer(samples, num_bars=32, height=20):
    spectrum = np.abs(np.fft.rfft(samples))[:num_bars]
    spectrum = spectrum / (np.max(spectrum) + 1e-6)
    bars = (spectrum * height).astype(int)

    print("\033[H\033[J", end="")

    for row in reversed(range(height)):
        line = ""
        for bar_height in bars:
            if bar_height > row:
                if bar_height < 3:
                    color = "\033[38;5;15m"  # White
                else:
                    relative_level = row / bar_height

                    if relative_level < 0.15:
                        color = "\033[38;5;202m"  # Orange
                    elif relative_level < 0.33:
                        color = "\033[38;5;226m"  # Yellow
                    else:
                        color = "\033[38;5;15m"   # White
                line += f"{color}█\033[0m"
            else:
                line += " "
        print(line)


def audio_callback(outdata, frames, time, status):
    global position, looped_audio, looped_audio_len, callback, record_enabled, record_buffer

    if status:
        print(status)

    # Check if audio is ready
    if looped_audio is None:
        outdata.fill(0)
        return

    # Prepare output buffer
    out = np.zeros((frames,), dtype=np.float32)

    # Loop audio with wraparound
    remaining = frames
    idx = 0
    while remaining > 0:
        available = looped_audio_len - position
        chunk = min(available, remaining)
        out[idx:idx + chunk] = looped_audio[position:position + chunk]
        position = (position + chunk) % looped_audio_len
        remaining -= chunk
        idx += chunk

    outdata[:] = out.reshape(-1, 1)

    # Optional callback or equalizer visualization
    if callback is not None:
        callback(out)
    else:
        draw_equalizer(out)

    # Record if enabled
    if record_enabled:
        record_buffer.append(out.copy())


def parse_time_string(time_str):
    """
    Parses a time string in either SS.ss or MM:SS.ss format to total seconds.
    Also handles float or int values directly.
    """
    if isinstance(time_str, (int, float)):
        return float(time_str)
    if isinstance(time_str, str):
        parts = time_str.split(":")
        if len(parts) == 1:
            return float(parts[0])
        elif len(parts) == 2:
            minutes = int(parts[0])
            seconds = float(parts[1])
            return minutes * 60 + seconds
    raise ValueError(f"Invalid time format: '{time_str}'. Expected a number or 'MM:SS.ss' string.")


def time_to_samples(time_spec, sample_rate):
    """Converts a time specification (seconds or 'MM:SS.ss') to a number of samples."""
    seconds = parse_time_string(time_spec)
    return int(seconds * sample_rate)


# Apply fade-in
def apply_fade_in(audio):
    length = audio.shape[0]
    fade_curve = np.linspace(0.0, 1.0, num=length, endpoint=True)
    return audio * fade_curve[:, None] if audio.ndim == 2 else audio * fade_curve


# Apply fade-out
def apply_fade_out(audio):
    length = audio.shape[0]
    fade_curve = np.linspace(1.0, 0.0, num=length, endpoint=True)
    return audio * fade_curve[:, None] if audio.ndim == 2 else audio * fade_curve


# --- Arg parsing ---
def parse_args():
    parser = argparse.ArgumentParser(description="Create and play a seamless audio loop from a file.")
    parser.add_argument("filename", help="Path to the input audio file (e.g., input.wav).")
    parser.add_argument("--loop_start", type=str, default="2.0", help="Start time of the loop. Format: 'SS.ss' or 'MM:SS.ss'. Default: 2.0 seconds.")
    parser.add_argument("--loop_length", type=str, default="8.0", help="Length of the loop. Format: 'SS.ss' or 'MM:SS.ss'. Default: 8.0 seconds.")
    parser.add_argument("--fade_length", type=str, default="0.1", help="Length of the cross-fade. Format: 'SS.ss' or 'MM:SS.ss'. Default: 0.1 seconds.")
    parser.add_argument("--record", type=str, help="Optional output file path to record the looped audio (e.g., output.wav).")
    return parser.parse_args()


# --- Main execution ---
def main():
    global looped_audio, looped_audio_len, record_enabled, record_buffer

    args = parse_args()

    try:
        audio_data, FS = sf.read(args.filename, dtype='float32')
    except FileNotFoundError:
        print(f"Error: File not found at '{args.filename}'")
        return
    except Exception as e:
        print(f"Error reading audio file: {e}")
        return

    # If stereo, convert to mono by averaging channels
    if audio_data.ndim > 1 and audio_data.shape[1] > 1:
        print("Input audio is stereo. Converting to mono.")
        audio_data = np.mean(audio_data, axis=1)

    # The audio data is now guaranteed to be mono (1D array).

    # Convert times to sample counts
    try:
        loop_start_samples = time_to_samples(args.loop_start, FS)
        loop_length_samples = time_to_samples(args.loop_length, FS)
        fade_length_samples = time_to_samples(args.fade_length, FS)
    except ValueError as e:
        print(f"Error parsing time arguments: {e}")
        return

    loop_end_samples = loop_start_samples + loop_length_samples

    if loop_start_samples < 0 or loop_end_samples > len(audio_data):
        print("Error: Loop section is outside the bounds of the audio file.")
        print(f"Audio length: {len(audio_data)/FS:.2f}s, Loop end: {loop_end_samples/FS:.2f}s")
        return
    if fade_length_samples <= 0:
        print("Warning: Fade length is zero, the loop may not be seamless.")
        loop_segment = audio_data[loop_start_samples:loop_end_samples]
        looped_audio = loop_segment
    elif fade_length_samples > loop_length_samples:
        print("Error: Fade length cannot be greater than loop length.")
        return
    else:
        # Extract the loop segment
        loop_segment = audio_data[loop_start_samples:loop_end_samples]

        # Create the crossfade
        head = loop_segment[:fade_length_samples]
        tail = loop_segment[-fade_length_samples:]

        faded_head = apply_fade_in(head)
        faded_tail = apply_fade_out(tail)

        # Mix with simple addition, as one fades in while the other fades out
        cross_faded_section = faded_head + faded_tail

        # Construct the seamless loop by replacing the start of the loop
        # with the cross-faded section.
        looped_audio = np.copy(loop_segment)
        looped_audio[:fade_length_samples] = cross_faded_section

    looped_audio_len = len(looped_audio)

    if args.record:
        record_enabled = True
        record_path = args.record

    print("Starting audio stream... Press Ctrl+C to stop.")
    try:
        with sd.OutputStream(callback=audio_callback, samplerate=FS, blocksize=BUFFER_SIZE, channels=1, dtype='float32'):
            print("Playing. Press Ctrl+C to exit.")
            while True:
                sd.sleep(1000)
    except KeyboardInterrupt:
        print("\nStopped by user.")
    except Exception as e:
        print(f"An audio error occurred: {e}")


    if record_enabled and record_buffer:
        print(f"Saving recorded audio to {record_path}...")
        try:
            output_array = np.concatenate(record_buffer)
            sf.write(record_path, output_array, FS)
            print("Save complete.")
        except Exception as e:
            print(f"Error saving file: {e}")


if __name__ == "__main__":
    main()

