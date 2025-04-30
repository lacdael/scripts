import numpy as np
from kivy.lang import Builder
from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.uix.filemanager import MDFileManager
from kivymd.toast import toast
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Rectangle
from kivy.clock import Clock
from kivy.graphics import Color
import wave
import struct
import threading
from threading import Lock


import os

from cozy_ambience import (
    audio_start_playback,
    set_low_pass_filter_cutoff,
    set_low_pass_filter_resonance,
    set_audio_mix_ratio,
    set_distortion,
    set_reverb_wet_mix,
    set_reverb_decay_time,
    set_gain_post,
    set_mod_speed,
    set_filter_resonance,
    set_filter_min,
    set_filter_max,
  )

Window.size = (450, 750)

KV = '''
BoxLayout:
    orientation: "vertical"
    padding: dp(10)
    spacing: dp(20)

    Widget:
        id: equalizer
        size_hint_y: None
        size_hint_x: 1
        height: 200
        canvas.before:
            Color:
                rgba: 0.2, 0.2, 0.2, 1
            Rectangle:
                pos: self.pos
                size: self.size

    BoxLayout:
        orientation: "horizontal"
        spacing: dp(20)  # Adjust spacing between the buttons
        size_hint_y: None

        MDRaisedButton:
            id: input1_btn
            text: "Select input.wav"
            on_release: app.file_picker("input1")
            size_hint_x: 0.5

        MDRaisedButton:
            id: input2_btn
            text: "Select input2.wav"
            on_release: app.file_picker("input2")
            size_hint_x: 0.5

    MDBoxLayout:
        orientation: "vertical"
        spacing: dp(4)
        size_hint_y: None
        MDLabel:
            text: "Mix Ratio"
            halign: "center"
            size_hint_y: None
            height: dp(8)
        MDSlider:
            id: mix_ratio
            min: 0
            max: 1
            value: 0.75
            step: 0.01
            on_value: app.set_audio_mix_ratio(self.value)
    


    GridLayout:
        cols: 3
        MDBoxLayout:
            orientation: "vertical"
            
            MDBoxLayout:
                orientation: "vertical"
                spacing: dp(4)
                size_hint_y: None

                MDLabel:
                    text: "Distortion Gain"
                    halign: "center"
                    size_hint_y: None
                    height: dp(8)
                MDSlider:
                    id: distortion_gain
                    min: 0
                    max: 20
                    value: 2
                    step: 0.1
                    on_value: app.set_distortion(self.value)

        MDBoxLayout:
            orientation: "vertical"
            
            MDBoxLayout:
                orientation: "vertical"
                spacing: dp(4)
                size_hint_y: None

                MDLabel:
                    text: "Cutoff FQ"
                    halign: "center"
                    size_hint_y: None
                    height: dp(8)
                MDSlider:
                    id: cutoff_freq
                    min: 100
                    max: 1000
                    value: 800
                    step: 0.1
                    on_value: app.set_low_pass_filter_cutoff(self.value)


        MDBoxLayout:
            orientation: "vertical"

            MDBoxLayout:
                orientation: "vertical"
                spacing: dp(4)
                size_hint_y: None
                
                MDLabel:
                    text: "Resonance"
                    halign: "center"
                    size_hint_y: None
                    height: dp(8)
                MDSlider:
                    id: filter_resonance
                    min: 1
                    max: 10
                    value: 1
                    step: 0.1
                    on_value: app.set_low_pass_filter_resonance(self.value)




    GridLayout:
        cols: 3

        MDBoxLayout:
            orientation: "vertical"
            
            MDBoxLayout:
                orientation: "vertical"
                spacing: dp(4)  # Tight spacing between label and slider
                size_hint_y: None
                #height: dp(20)

                MDLabel:
                    text: "Reverb Wet Mix"
                    halign: "center"
                    size_hint_y: None
                    height: dp(8)
                MDSlider:
                    id: reverb_wet_mix
                    min: 0
                    max: 1
                    value: 0.5
                    step: 0.01
                    on_value: app.set_reverb_wet_mix(self.value)

        MDBoxLayout:
            orientation: "vertical"
            
            MDBoxLayout:
                orientation: "vertical"
                spacing: dp(4)  # Tight spacing between label and slider
                size_hint_y: None
                #height: dp(20)

                MDLabel:
                    text: "Reverb Decay"
                    halign: "center"
                    size_hint_y: None
                    height: dp(8)
                MDSlider:
                    id: decay_time
                    min: 0
                    max: 5
                    value: 0.8
                    step: 0.1
                    on_value: app.set_reverb_decay_time(self.value)

        MDBoxLayout:
            orientation: "vertical"
            
            MDBoxLayout:
                orientation: "vertical"
                spacing: dp(4)
                size_hint_y: None

                MDLabel:
                    text: "Gain"
                    halign: "center"
                    size_hint_y: None
                    height: dp(8)
                MDSlider:
                    id: gain_post
                    min: 0
                    max: 10
                    value: 1
                    step: 0.1
                    on_value: app.set_gain_post(self.value)









    BoxLayout:
        orientation: "horizontal"
        #spacing: dp(10)

        MDRaisedButton:
            id: input3_btn
            text: "Select input3.wav"
            on_release: app.file_picker("input3")

        MDBoxLayout:
            orientation: "vertical"

            MDBoxLayout:
                orientation: "vertical"
                #spacing: dp(4)  # Tight spacing between label and slider
                size_hint_y: None
                #height: dp(20)

                MDLabel:
                    text: "Modulation Rate"
                    halign: "center"
                    size_hint_y: None
                    height: dp(8)
                MDSlider:
                    id: mod_speed
                    min: 0.125
                    max: 4
                    value: 1
                    step: 0.1
                    on_value: app.set_mod_speed(self.value)

    GridLayout:
        cols: 3
        #spacing: dp(10)
        MDBoxLayout:
            orientation: "vertical"
            
            MDBoxLayout:
                orientation: "vertical"
                spacing: dp(4)  # Tight spacing between label and slider
                size_hint_y: None
                #height: dp(20)

                MDLabel:
                    text: "Resonance"
                    halign: "center"
                    size_hint_y: None
                    height: dp(8)
                MDSlider:
                    id: resonance
                    min: 1
                    max: 10
                    value: 1
                    step: 0.1
                    on_value: app.set_filter_resonance(self.value)

        MDBoxLayout:
            orientation: "vertical"
            
            MDBoxLayout:
                orientation: "vertical"
                spacing: dp(4)  # Tight spacing between label and slider
                size_hint_y: None
                #height: dp(20)

                MDLabel:
                    text: "Filter FQ min"
                    halign: "center"
                    size_hint_y: None
                    height: dp(8)
                MDSlider:
                    id: filter_fmin
                    min: 400
                    max: 2000
                    value: 500
                    step: 10
                    on_value: app.set_filter_min(self.value)

        MDBoxLayout:
            orientation: "vertical"

            MDBoxLayout:
                orientation: "vertical"
                spacing: dp(4)  # Tight spacing between label and slider
                size_hint_y: None
                #height: dp(20)

                MDLabel:
                    text: "Filter FQ max"
                    halign: "center"
                    size_hint_y: None
                    height: dp(8)
                MDSlider:
                    id: filter_fmax
                    min: 1000
                    max: 4000
                    value: 2000
                    step: 50
                    on_value: app.set_filter_max(self.value)


    MDRaisedButton:
        text: "Start"
        on_release: app.start_audio()
'''





    






class MainApp(MDApp):
    def build(self):
        self.sample_lock = Lock()
        self.latest_samples = np.zeros(2048)
        Clock.schedule_interval(self.safe_update_equalizer, 1 / 3 )  # ~15 fps
        self.manager = MDFileManager(
            select_path=self.select_path,
            preview=False,
            search='all',
            ext=['.wav']
        )
        self.file_key = ""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.file_paths = {
                "input1": os.path.join(script_dir, "input.wav"),
                "input2": os.path.join(script_dir, "input2.wav"),
                "input3": os.path.join(script_dir, "input3.wav")
                }

        return Builder.load_string(KV)

    def set_audio_mix_ratio(self, v):
        set_audio_mix_ratio(v);

    def set_distortion(self,v):
        set_distortion(v);

    def set_low_pass_filter_cutoff(self,v):
        set_low_pass_filter_cutoff(v);

    def set_low_pass_filter_resonance(self,v):
        set_low_pass_filter_resonance(v);

    def set_reverb_wet_mix(self,v):
        set_reverb_wet_mix(v);

    def set_reverb_decay_time(self,v):
        set_reverb_decay_time(v);

    def set_gain_post(self,v):
        set_gain_post(v);

    def set_mod_speed(self,v):
        set_mod_speed(v)

    def set_filter_resonance(self,v):
        set_filter_resonance(v)

    def set_filter_min(self,v):
        set_filter_min(v);

    def set_filter_max(self,v):
        set_filter_max(v);

    def file_picker(self, key):
        self.file_key = key
        home = os.path.expanduser("~")

        def wav_filter(folder, filename):
            path = os.path.join(folder, filename)
            return os.path.isdir(path) or filename.lower().endswith('.wav')

        self.manager.show(home)


    def select_path(self, path):
        if not path.lower().endswith(".wav"):
            toast("Please select a .wav file")
            return
        self.file_paths[self.file_key] = path
        self.root.ids[f"{self.file_key}_btn"].text = os.path.basename(path)
        self.manager.close()


    def safe_update_equalizer(self, dt):
        if self.root is None:
            return

        with self.sample_lock:
            samples = self.latest_samples.copy()

        self.samples = samples
        self.update_equalizer()


    def update_equalizer(self, dt=0):
        self.root.ids.equalizer.canvas.clear()
        num_bars = 32
        height = 100
        

        spectrum = np.abs(np.fft.rfft(self.samples))
        num_bars = min(32, len(spectrum))
        spectrum = spectrum[:num_bars]
        spectrum = spectrum / (np.max(spectrum) + 1e-6)  # Normalize
        bars = (spectrum * height).astype(int)

        with self.root.ids.equalizer.canvas:
            bar_width = self.root.ids.equalizer.width / num_bars
            offset_x = self.root.ids.equalizer.x  

            for i, bar_height in enumerate(bars):
                Color(1, 1 - bar_height / height, bar_height / height, 1)
                Rectangle(
                    pos=(offset_x + i * bar_width, self.root.ids.equalizer.y),
                    size=(bar_width, bar_height)
                )



    def _set_samples(self, s):
            with self.sample_lock:
                self.latest_samples = s.copy()



    def start_audio(self):
        values = {
            "mix_ratio": self.root.ids.mix_ratio.value,
            "distortion_gain": self.root.ids.distortion_gain.value,
            "cutoff_freq": self.root.ids.cutoff_freq.value,
            "filter_resonance": self.root.ids.filter_resonance.value,
            "reverb_wet_mix": self.root.ids.reverb_wet_mix.value,
            "decay_time": self.root.ids.decay_time.value,
            "gain_post": self.root.ids.gain_post.value,
            "mod_speed": self.root.ids.mod_speed.value,
            "resonance": self.root.ids.resonance.value,
            "fmin": self.root.ids.filter_fmin.value,
            "fmax": self.root.ids.filter_fmax.value,
        }
        print("Slider values:", values)
        print("Selected files:", self.file_paths)
        toast("Processing started (check terminal output)")

        threading.Thread(
            target=audio_start_playback,
            args=(self._set_samples, values, self.file_paths ),
            daemon=True
        ).start()

if __name__ == '__main__':
    MainApp().run()
