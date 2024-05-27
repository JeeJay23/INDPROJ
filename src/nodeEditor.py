import dearpygui.dearpygui as dpg
import numpy as np
import pyaudio
import pyopencl as cl
import os
import threading

os.environ['PYOPENCL_CTX'] = ''
p = pyaudio.PyAudio()

dpg.create_context()

def link_callback(sender, app_data):
    print(f"sender {sender}, app_data {app_data}")
    outAttrTag, inAttrTag = app_data

    print(dpg.get_item_children(outAttrTag))

    dpg.add_node_link(app_data[0], app_data[1], parent=sender)

# callback runs when user attempts to disconnect attributes
def delink_callback(sender, app_data):
    # app_data -> link_id
    print(f"sender {sender}, app_data {app_data}")
    dpg.delete_item(app_data)

def open_stream(sender, app_data, user_data):
    global stream, audio_data
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=dpg.get_value("fs"),
                    input=True,
                    frames_per_buffer=dpg.get_value("bufferSize"))
    audio_data = np.zeros(dpg.get_value("bufferSize"), dtype=np.int16)
    start_audio_thread()

def read_audio_data():
    global audio_data
    while True:
        data = stream.read(dpg.get_value("bufferSize"), exception_on_overflow=False)
        audio_data = np.frombuffer(data, dtype=np.int16)
        dpg.set_value("audio_series", [list(range(dpg.get_value("bufferSize"))), audio_data.tolist()])

# Function to start the audio reading thread
def start_audio_thread():
    audio_thread = threading.Thread(target=read_audio_data, daemon=True)
    audio_thread.start()

def on_update_buffer_size(sender, app_data):
    dpg.set_axis_limits("xAxis", 0, dpg.get_value("bufferSize"))

with dpg.window(label="Node editor", tag="Primary Window", menubar=True):
    with dpg.node_editor(callback=link_callback, delink_callback=delink_callback):
        with dpg.node(label="Audio input", tag="AudioInput"):
            with dpg.node_attribute(label="Audio buffer", attribute_type=dpg.mvNode_Attr_Output):
                dpg.add_slider_int(
                    tag="bufferSize",
                    label="buffer size",
                    width=150,
                    default_value=1024,
                    min_value=100,
                    max_value=2000,
                    callback=on_update_buffer_size)
                dpg.add_input_float(tag="volume", label="volume", width=150, default_value=1.0)
                dpg.add_input_int(tag="fs", label="sample rate", width=150, default_value=44100)

                with dpg.plot(label="Waveform Plot", height=500):
                    dpg.add_plot_axis(dpg.mvXAxis, label="Samples", tag="xAxis")
                    dpg.set_axis_limits(dpg.last_item(), 0, dpg.get_value("bufferSize"))
                    with dpg.plot_axis(dpg.mvYAxis, label="Amplitude"):
                        dpg.set_axis_limits(dpg.last_item(), -30000, 30000)
                        dpg.add_line_series([], [], label="Audio Data", parent=dpg.last_item(), id="audio_series")

                dpg.add_button(label="Open stream", callback=open_stream)

        with dpg.node(label="Node 2"):
            with dpg.node_attribute(label="Node A3"):
                dpg.add_input_float(label="F3", width=200)

            with dpg.node_attribute(label="Node A4", attribute_type=dpg.mvNode_Attr_Output):
                dpg.add_input_float(label="F4", width=200)

stream = None
audio_data = None

dpg.create_viewport(title='Custom DSPedal', width=1200, height=900)
dpg.setup_dearpygui()
dpg.show_item_registry()
dpg.show_viewport()
dpg.set_primary_window("Primary Window", True)
dpg.start_dearpygui()
dpg.destroy_context()

stream.stop_stream()
stream.close()
p.terminate()
