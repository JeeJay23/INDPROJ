import numpy as np
import dearpygui.dearpygui as dpg
import sounddevice as sd

from nodes.myglobals import *
from nodes.basenode import DspNode

class SineOscillatorNode(DspNode):
    def __init__(self, name):
        self.fs = SAMPLING_RATE
        self.freq = 440
        self.amplitude = 0.1
        self.phase = 0.0
        self.block_size = BLOCK_SIZE
        self.output_buffer = np.zeros(self.block_size)

        self.run()
        super().__init__(name)

    def draw(self):
        with dpg.node(label=self.name) as self.node_id:
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
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
                attribute_type=dpg.mvNode_Attr_Output,
                user_data=self
            )

    def on_amplitude_changed(self, sender, app_data):
        self.amplitude = dpg.get_value(self.input_amplitude)

    def on_freq_changed(self, sender, app_data):
        self.freq = dpg.get_value(self.input_freq)

    def on_linked_output(self, node):
        super().on_linked_output(node)

    def run(self):
        phase_increment = 2 * np.pi * self.freq / self.fs
        self.output_buffer = self.amplitude * np.sin(self.phase + phase_increment * np.arange(self.block_size))
        self.phase += phase_increment * self.block_size
        self.phase = self.phase % (2 * np.pi)