import dearpygui.dearpygui as dpg
import sounddevice as sd
import numpy as np
import threading

class DspNode():
    def __init__(self, name):
        self.name = name
        self.is_active = False
        self.draw()

    def draw(self):
        with dpg.node(label=self.name) as self.node_id:
            with dpg.node_attribute():
                self.input_gain = dpg.add_input_float(label="Gain", default_value=1, width=200, callback=self.on_gain_changed)
            self.output = dpg.add_node_attribute(label="Output", parent=self.node_id, attribute_type=dpg.mvNode_Attr_Output)

    def on_tick(self):
        pass

    def on_gain_changed(self, sender, app_data):
        print(dpg.get_value(self.input_gain))

    def on_link(self):
        pass

    def on_delink(self):
        pass

class SinusOutputNode(DspNode):
    def __init__(self, name):
        self.fs = 44100
        self.freq = 440
        self.blocksize = 1024
        self.amplitude = 0.1
        self.phase = 0.0
        self.running = True
        self.channels = 2
        self.audio_out_thread = threading.Thread(target=self.audio_out)
        self.audio_out_thread.start()
        super().__init__(name)

    def stop(self):
        self.running = False

    def audio_out(self):
        with sd.OutputStream(callback=self.audio_callback, blocksize=self.blocksize, channels=self.channels, samplerate=self.fs):
            while self.running:
                sd.sleep(1000)
    
    def audio_callback(self, outdata, frames, time, status):
        phase_increment = 2 * np.pi * self.freq / self.fs
        sine_wave = self.amplitude * np.sin(self.phase + phase_increment * np.arange(frames))
        self.phase += phase_increment * frames
        self.phase = self.phase % (2 * np.pi)
        outdata[:, 0] = sine_wave

    def draw(self):
        with dpg.node(label=self.name) as self.node_id:
            with dpg.node_attribute():
                self.lbl_fs = dpg.add_input_int(
                    label="Sample rate",
                    default_value=self.fs,
                    width=200,
                    enabled=False
                )

                self.input_amplitude = dpg.add_slider_float(
                    label="Amplitude",
                    width=200,
                    default_value=self.amplitude,
                    min_value=0,
                    max_value=10,
                    callback=self.on_amplitude_changed
                )

                self.input_freq = dpg.add_slider_float(
                    label="Frequency",
                    width=200,
                    default_value=self.freq,
                    min_value=20,
                    max_value=20000,
                    callback=self.on_freq_changed
                )

            self.output = dpg.add_node_attribute(
                label="Output",
                parent=self.node_id,
                attribute_type=dpg.mvNode_Attr_Output
            )

    def on_amplitude_changed(self, sender, app_data):
        self.amplitude = dpg.get_value(self.input_amplitude)

    def on_freq_changed(self, sender, app_data):
        self.freq = dpg.get_value(self.input_freq)