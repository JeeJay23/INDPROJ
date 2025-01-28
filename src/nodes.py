import dearpygui.dearpygui as dpg
import numpy as np
import sounddevice as sd
import threading

BLOCK_SIZE = 1024
SAMPLING_RATE = 44100

class DspNode():
    def __init__(self, name):
        self.name = name
        self.is_active = False
        self.input_nodes = []
        self.output_nodes = []
        self.draw()
        self.run()

    def draw(self):
        print(f'{self}: base draw method, override me!')

    def run(self):
        print(f'{self}: base run method, override me!')

    def on_linked_input(self, node):
        print(f'{self.name}: linked input from {node.name}')
        node.run()
        self.input_nodes.append(node)

    def on_linked_output(self, node):
        print(f'{self.name}: linked output to {node.name}')
        self.is_active = True
        self.output_nodes.append(node)

    def on_delinked_input(self, node):
        print(f'{self.name}: delinked input from {node.name}')
        self.input_nodes.remove(node)
        self.is_active = False
        pass

    def on_delinked_output(self, node):
        print(f'{self.name}: delinked output to {node.name}')
        self.output_nodes.remove(node)
        if len(self.output_nodes) == 0:
            self.is_active = False
        pass

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

class AudioPlaybackNode(DspNode):
    def __init__(self, name):
        self.blocksize = BLOCK_SIZE
        self.running = True
        self.channels = 2
        self.fs = SAMPLING_RATE
        self.audio_buffer = np.zeros(self.blocksize)

        super().__init__(name)
    
    def draw(self):
        with dpg.node(label=self.name) as self.node_id:
            with dpg.node_attribute(user_data=self):
                self.input_volume = dpg.add_slider_float(
                    label="Volume",
                    width=200,
                    default_value=.5,
                    min_value=0,
                    max_value=1,
                    callback=self.on_volume_changed
                )

    def stop(self):
        self.running = False

    def on_linked_input(self, node):
        self.running = True
        self.audio_out_thread = threading.Thread(target=self.audio_out)
        self.audio_out_thread.start()

        super().on_linked_input(node)

    def on_delinked_input(self, node):
        self.running = False
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