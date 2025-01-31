import numpy as np
import dearpygui.dearpygui as dpg
import sounddevice as sd

from nodes.myglobals import *
from nodes.basenode import DspNode

class SineOscillatorNode(DspNode):
    def __init__(self, name, node_editor):
        self.fs = SAMPLING_FREQ
        self.freq = 440
        self.amplitude = 0.1
        self.phase = 0.0
        self.block_size = BLOCK_SIZE
        self.output_buffer = np.zeros(self.block_size)

        super().__init__(name, node_editor)
        self.run()

    @DspNode._draw
    def draw(self):
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

            with dpg.tree_node(label="Visualiser", default_open=True):
                self.graph = dpg.add_simple_plot(width=300, height=250)
                dpg.set_value(self.graph, self.output_buffer.tolist())
                
        self.output = dpg.add_node_attribute(
            label="Output",
            parent=self.node_id,
            attribute_type=dpg.mvNode_Attr_Output,
            user_data=self
        )

    def on_amplitude_changed(self, sender, app_data):
        self.amplitude = dpg.get_value(self.input_amplitude)
        self.run()

    def on_freq_changed(self, sender, app_data):
        self.freq = dpg.get_value(self.input_freq)
        self.run()

    def on_linked_output(self, node):
        super().on_linked_output(node)

    def refresh_graph(self):
        dpg.set_value(self.graph, self.output_buffer.tolist())

    def run(self):
        phase_increment = 2 * np.pi * self.freq / self.fs
        self.output_buffer = self.amplitude * np.sin(self.phase + phase_increment * np.arange(self.block_size))
        self.phase += phase_increment * self.block_size
        self.phase = self.phase % (2 * np.pi)
        self.refresh_graph()