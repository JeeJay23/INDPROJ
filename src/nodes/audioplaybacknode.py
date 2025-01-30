import threading
import numpy as np
import sounddevice as sd
import dearpygui.dearpygui as dpg

from nodes.myglobals import *
from nodes.basenode import DspNode

class AudioPlaybackNode(DspNode):
    def __init__(self, name, node_editor):
        self.blocksize = BLOCK_SIZE
        self.running = True
        self.channels = 2
        self.fs = SAMPLING_RATE
        self.audio_buffer = np.zeros(self.blocksize)

        super().__init__(name, node_editor)
    
    # base draw created the node, add controls from here
    @DspNode._draw
    def draw(self):
        # with dpg.node(label=self.name, user_data=self) as self.node_id:
        with dpg.node_attribute(user_data=self):
            self.input_volume = dpg.add_slider_float(
                label="Volume",
                width=200,
                default_value=.5,
                min_value=0,
                max_value=1,
                callback=self.on_volume_changed
            )

    def on_delete(self):
        self.stop()
        return super().on_delete()

    def stop(self):
        self.running = False

    def on_linked_input(self, node):
        self.running = True
        self.audio_out_thread = threading.Thread(target=self.audio_out)
        self.audio_out_thread.start()

        super().on_linked_input(node)

    def on_delinked_input(self, node):
        self.stop()
        super().on_delinked_input(node)

    def audio_out(self):
        with sd.OutputStream(
            callback=self.audio_callback,
            blocksize=self.blocksize,
            channels=self.channels,
            samplerate=self.fs
        ):
            while self.running:
                sd.sleep(1000)

    def audio_callback(self, outdata, frames, time, status):
        if (len(self.input_nodes) == 0):
            return

        self.audio_buffer = self.input_nodes[0].output_buffer

        outdata[:, 0] = self.audio_buffer
        self.input_nodes[0].run()
    
    def on_volume_changed(self, sender, app_data):
        pass