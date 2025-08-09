import sounddevice as sd
import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt, lfilter, fftconvolve
from collections import deque
import argparse

record_buffer = []
record_enabled = False
callback = None;

def ensure_2d(data):
    return data if data.ndim > 1 else data[:, np.newaxis]

filename = "input.wav"
audio_data, FS = sf.read(filename, dtype='float32')
audio_data = ensure_2d(audio_data)

filename2 = "input2.wav"
audio_data2, FS2 = sf.read(filename2, dtype='float32')
audio_data2 = ensure_2d(audio_data2)

filename3 = "input3.wav"
audio_data3, FS3 = sf.read(filename3, dtype='float32')
audio_data3 = ensure_2d(audio_data3)

assert FS3 == FS, "Sample rate of input3.wav does not match"
assert FS == FS2, "Sample rates do not match"
min_len = min(len(audio_data), len(audio_data2), len(audio_data3))
audio_data = audio_data[:min_len]
audio_data2 = audio_data2[:min_len]
audio_data3 = audio_data3[:min_len]

BUFFER_SIZE = 2048
position = 0
position3 = 0;

##############################################
# Low Pass Filter with Resonance #############
##############################################

cutoff_freq = 800  
resonance = 0.7 
FS = 44100

def make_resonant_lowpass_sos(cutoff, Q, fs):
    omega = 2 * np.pi * cutoff / fs
    alpha = np.sin(omega) / (2 * Q)
    cos_omega = np.cos(omega)

    b0 = (1 - cos_omega) / 2
    b1 = 1 - cos_omega
    b2 = (1 - cos_omega) / 2
    a0 = 1 + alpha
    a1 = -2 * cos_omega
    a2 = 1 - alpha

    b = [b0 / a0, b1 / a0, b2 / a0]
    a = [1.0, a1 / a0, a2 / a0]

    return np.array([[b[0], b[1], b[2], a[0], a[1], a[2]]])

# Initialize filter
sos_low = make_resonant_lowpass_sos(cutoff_freq, resonance, FS)
low_pass_state = np.zeros((sos_low.shape[0], 2))

def apply_low_pass_filter(samples):
    global low_pass_state
    samples, low_pass_state = sosfilt(sos_low, samples, zi=low_pass_state)
    return samples

def set_low_pass_filter_cutoff(f):
    global cutoff_freq, sos_low, low_pass_state
    cutoff_freq = max(100, min(1000, f))
    sos_low = make_resonant_lowpass_sos(cutoff_freq, resonance, FS)
    low_pass_state = np.zeros((sos_low.shape[0], 2))

def set_low_pass_filter_resonance(q):
    global resonance, sos_low, low_pass_state
    resonance = max(0.1, min(10.0, q))
    sos_low = make_resonant_lowpass_sos(cutoff_freq, resonance, FS)
    low_pass_state = np.zeros((sos_low.shape[0], 2))

##############################################


##############################################
# Cross Fade #################################
##############################################

mix_ratio = 0.75  # 0 = only input2.wav, 1 = only processed input.wav

def set_audio_mix_ratio(value):
    global mix_ratio
    mix_ratio = max(0.0, min(1.0, value))  # Clamp between 0 and 1

##############################################



##############################################
# Distortion #################################
##############################################

distortion_gain = 2

def set_distortion( g ):
    global distortion_gain
    distortion_gain = max(0.0, min(20.0, g))  # Clamp between 0 and 1

def apply_distortion(samples):
    return np.clip(samples * distortion_gain, -1, 1)

distortion_gain_post = 1

def set_gain_post( g ):
    global distortion_gain_post
    distortion_gain_post = max(0.0, min(20.0, g))  # Clamp between 0 and 1

def apply_gain_post(samples):
    return np.clip(samples * distortion_gain_post, -1, 1)
##############################################



##############################################
# Reverb #####################################
##############################################

decay_time = 0.8  # in seconds
reverb_wet_mix = 0.5
reverb_buffer = deque([0.0]*2048, maxlen=2048)

impulse_length = int(FS * decay_time)
t = np.linspace(0, decay_time, impulse_length)
impulse_response = np.exp(-3 * t / decay_time)
impulse_response /= np.sum(impulse_response)

def set_reverb_decay_time( t ):
    global decay_time
    decay_time = max(0.0, min(5.0, t))  # Clamp between 0 and 2

def set_reverb_wet_mix(value):
    global reverb_wet_mix
    reverb_wet_mix = max(0.0, min(1.0, value))  # Clamp between 0 and 1

def apply_reverb(samples):
    global reverb_buffer, reverb_wet_mix, impulse_response

    wet = fftconvolve(samples, impulse_response, mode='full')[:len(samples)]
    tail = np.array(reverb_buffer)
    if len(tail) < len(samples):
        tail = np.pad(tail, (0, len(samples) - len(tail)))
    wet += tail

    new_tail = fftconvolve(samples, impulse_response, mode='full')[len(samples):]
    reverb_buffer = deque(new_tail, maxlen=BUFFER_SIZE)

    output = (1 - reverb_wet_mix) * samples + reverb_wet_mix * wet
    return np.clip(output, -1.0, 1.0)

##############################################

##############################################
# Dynamic Low pass filter ####################
##############################################

mod_speed = 1.0 

def set_mod_speed(s):
    global mod_speed
    mod_speed = max(0.125, min(4.0, s))

dynamic_cutoff = 500
filter_resonance = 0.7

def resonant_lowpass_sos(cutoff, resonance, fs):
    omega = 2 * np.pi * cutoff / fs
    alpha = np.sin(omega) / (2 * resonance)
    cos_omega = np.cos(omega)

    b0 = (1 - cos_omega) / 2
    b1 = 1 - cos_omega
    b2 = (1 - cos_omega) / 2
    a0 = 1 + alpha
    a1 = -2 * cos_omega
    a2 = 1 - alpha

    b = [b0 / a0, b1 / a0, b2 / a0]
    a = [1.0, a1 / a0, a2 / a0]

    sos = np.array([[b[0], b[1], b[2], a[0], a[1], a[2]]])
    return sos

sos_dynamic_low = resonant_lowpass_sos(dynamic_cutoff, filter_resonance, FS)
dynamic_low_pass_state = np.zeros((sos_dynamic_low.shape[0], 2))

def set_filter_resonance(q):
    global filter_resonance
    filter_resonance = max(0.1, min(10.0, float(q)))
    update_filter()

def update_filter():
    global sos_dynamic_low, dynamic_cutoff, dynamic_low_pass_state
    sos_dynamic_low = resonant_lowpass_sos(dynamic_cutoff, filter_resonance, FS)
    #dynamic_low_pass_state = np.zeros((sos_dynamic_low.shape[0], 2))  # reset state

def set_filter_min(freq):
    global frequency_min
    frequency_min = max(20, min(5000, int(freq)))

def set_filter_max(freq):
    global frequency_max
    frequency_max = max(1000, min(FS // 2 - 100, int(freq)))

mod_min = float('inf')
mod_max = 0.0
frequency_min = 100.0
frequency_max = 1000.0
smoothed_freq = None
smoothing_factor = 0.1
last_cutoff = None

def apply_dynamic_low_pass_filter(samples, mod_source):
    global mod_min, mod_max, smoothed_freq, frequency_min, frequency_max
    global dynamic_cutoff, sos_dynamic_low, dynamic_low_pass_state

    peak = np.max(np.abs(mod_source))
    if not np.isfinite(peak):
        peak = 0.0

    if mod_min == float('inf') or mod_max == 0.0:
        mod_min = peak
        mod_max = peak + 1e-6

    mod_min = min(mod_min, peak)
    mod_max = max(mod_max, peak)

    range_val = mod_max - mod_min
    percent = 0.0 if range_val < 1e-6 else (peak - mod_min) / range_val

    mapped_freq = frequency_min + percent * (frequency_max - frequency_min)
    mapped_freq = np.clip(mapped_freq, 20, FS / 2 - 100)

    if smoothed_freq is None:
        smoothed_freq = mapped_freq
    else:
        smoothed_freq = (smoothing_factor * mapped_freq +
                         (1 - smoothing_factor) * smoothed_freq)

    new_cutoff = max(frequency_min, min(frequency_max, smoothed_freq))
    if abs(new_cutoff - dynamic_cutoff) > 10:
        dynamic_cutoff = new_cutoff
        try:
            update_filter()
        except Exception as e:
            print(f"[FILTER ERROR] Could not update filter: {e}")

    filtered_samples, dynamic_low_pass_state = sosfilt(sos_dynamic_low, samples, zi=dynamic_low_pass_state)
    filtered_samples = np.nan_to_num(filtered_samples, nan=0.0, posinf=1.0, neginf=-1.0)

    return filtered_samples

##############################################

##############################################
# Draw Equalizer #############################
##############################################

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

##############################################


def audio_callback(outdata, frames, time, status):
    global position, position3, record_enabled, record_buffer,callback
    if status:
        print(status)
    if position + frames > len(audio_data):
        outdata[:] = np.zeros((frames, 1))
        return

    raw = audio_data[position:position + frames, 0] 
    unprocessed = audio_data2[position:position + frames, 0]
    position += frames
   
    mod_indices = (position3 + np.arange(frames) * mod_speed).astype(int)
    mod_indices = np.clip(mod_indices, 0, len(audio_data3) - 1)
    mod_source = audio_data3[mod_indices, 0]
    position3 += int(frames * mod_speed)

    processed = apply_distortion(raw)
    processed = apply_low_pass_filter(processed)
    processed = np.clip(processed, -1, 1)
    processed = apply_reverb(processed)
    processed = apply_gain_post(processed)
    processed = np.clip(processed, -1, 1)
    processed = apply_dynamic_low_pass_filter(processed, mod_source)
    
    mixed = (mix_ratio * processed) + ((1 - mix_ratio) * unprocessed)
    mixed = np.clip(mixed, -1, 1)

    if callback != None:
        callback( mixed );
    else:
        draw_equalizer(mixed)
    outdata[:] = mixed.reshape(-1, 1)

    # Record if enabled
    if record_enabled:
        record_buffer.append(mixed.copy())


def audio_start_playback( mCallback, settings, files ):
    global callback,filename,filename2,filename3,position, position3,audio_data,audio_data2,audio_data3,FS,FS2,FS3;
    position = 0;
    position3 = 0;

    if "input1" in files:
        filename = files["input1"];
        audio_data, FS = sf.read(filename, dtype='float32')
        audio_data = ensure_2d(audio_data)
    if "input2" in files:
        filename2 = files["input2"];
        audio_data2, FS2 = sf.read(filename2, dtype='float32')
        audio_data2 = ensure_2d(audio_data2)
    if "input3" in files:
        filename3 = files["input3"];
        audio_data3, FS3 = sf.read(filename3, dtype='float32')
        audio_data3 = ensure_2d(audio_data3)
    if "mix_ratio" in settings:
        set_audio_mix_ratio( settings["mix_ratio"] );
    if "distortion_gain" in settings:
        set_distortion( settings["distortion_gain"] );
    if "cutoff_freq" in settings:
        set_low_pass_filter_cutoff( settings["cutoff_freq"] );
    if "filter_resonance" in settings:
        set_low_pass_filter_resonance( settings["filter_resonance"] );
    if "reverb_wet_mix" in settings:
        set_reverb_wet_mix( settings["reverb_wet_mix"] );
    if "decay_time" in settings:
        set_reverb_decay_time( settings["decay_time"] );
    if "gain_post" in settings:
        set_gain_post( settings["gain_post"] );
    if "mod_speed" in settings:
        set_mod_speed( settings["mod_speed"] );
    if "resonance" in settings:
        set_filter_resonance( settings["resonance"] );
    if "fmin" in settings:
        set_filter_min( settings["fmin"] );
    if "fmax" in settings:
        set_filter_max( settings["fmax"] );

    callback = mCallback;
    with sd.OutputStream(callback=audio_callback, samplerate=FS, blocksize=BUFFER_SIZE, channels=1, dtype='float32'):
        print("Playing and processing audio in real-time... Press Ctrl+C to stop.")
        sd.sleep(int(len(audio_data) / FS * 1000))

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Real-time audio processor with modulation and filters.")
    parser.add_argument("filename", help="Path to input.wav")
    parser.add_argument("filename2", help="Path to input2.wav (dry mix)")
    parser.add_argument("filename3", help="Path to input3.wav (modulation source)")

    parser.add_argument("--cutoff_freq", type=float, default=800, help="Low-pass filter cutoff frequency (Hz)")
    parser.add_argument("--filter_resonance", type=float, default=1.2, help="Q factor for the low pass filter")
    parser.add_argument("--mix_ratio", type=float, default=0.75, help="Mix ratio: 0 = dry (input2), 1 = wet (processed)")
    parser.add_argument("--distortion_gain", type=float, default=2.0, help="Gain for distortion effect")
    parser.add_argument("--reverb_wet_mix", type=float, default=0.5, help="Wet mix ratio for reverb")
    parser.add_argument("--decay_time", type=float, default=0.8, help="Reverb decay time in seconds")
    parser.add_argument("--gain_post", type=float, default=1.0, help="Gain for distortion effect")
    parser.add_argument("--mod_speed", type=float, default=1.0, help="Speed multiplier for modulation signal")
    parser.add_argument("--resonance", type=float, default=2, help="Q factor for modulated bandpass filter")
    parser.add_argument("--fmin", type=float, default=200, help="Minimum center frequency for bandpass filter")
    parser.add_argument("--fmax", type=float, default=1000, help="Maximum center frequency for bandpass filter")
    parser.add_argument("--record", type=str, help="Path to save the processed output (e.g., output.wav)")

    args = parser.parse_args()

    filename = args.filename
    filename2 = args.filename2
    filename3 = args.filename3

    audio_data, FS = sf.read(filename, dtype='float32')
    audio_data = ensure_2d(audio_data)

    audio_data2, FS2 = sf.read(filename2, dtype='float32')
    audio_data2 = ensure_2d(audio_data2)

    audio_data3, FS3 = sf.read(filename3, dtype='float32')
    audio_data3 = ensure_2d(audio_data3)


    assert FS == FS2 == FS3, "All input files must have the same sample rate."
    min_len = min(len(audio_data), len(audio_data2), len(audio_data3))
    audio_data = audio_data[:min_len]
    audio_data2 = audio_data2[:min_len]
    audio_data3 = audio_data3[:min_len]

    BUFFER_SIZE = 2048
    position = 0
    position3 = 0

    set_low_pass_filter_cutoff( args.cutoff_freq )
    set_low_pass_filter_resonance(args.filter_resonance);
    set_audio_mix_ratio( args.mix_ratio )
    set_distortion( args.distortion_gain )
    set_reverb_wet_mix( args.reverb_wet_mix )
    set_reverb_decay_time( args.decay_time );
    set_gain_post( args.gain_post )

    impulse_length = int(FS * decay_time)
    t = np.linspace(0, decay_time, impulse_length)
    impulse_response = np.exp(-3 * t / decay_time)
    impulse_response /= np.sum(impulse_response)

    set_mod_speed( args.mod_speed )
    set_filter_resonance( args.resonance )
    set_filter_min( args.fmin );
    set_filter_max( args.fmax );
    
    if args.record:
        record_enabled = True
        record_path = args.record
    
    with sd.OutputStream(callback=audio_callback, samplerate=FS, blocksize=BUFFER_SIZE, channels=1, dtype='float32'):
        print("... Press Ctrl+C to stop.")
        sd.sleep(int(len(audio_data) / FS * 1000))
        if record_enabled and record_buffer:
            print(f"Saving to {record_path}...")
            output_array = np.concatenate(record_buffer)
            sf.write(record_path, output_array, FS)


"""
pythonx ./cozy_ambience.py input.wav input2.wav input3.wav \
  --cutoff_freq 1000 \
  --filter_resonance 1.2 \
  --mix_ratio 0.5 \
  --distortion_gain 3 \
  --reverb_wet_mix 0.4 \
  --decay_time 1.0 \
  --gain_post 1.0 \
  --mod_speed 0.5 \
  --resonance 0.5 \
  --fmin 300 \
  --fmax 1200 \
  --record output.wav
"""
