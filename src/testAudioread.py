import pyaudio
import numpy as np
import dearpygui.dearpygui as dpg
import threading

# Audio stream settings
FORMAT = pyaudio.paInt16  # 16-bit resolution
CHANNELS = 1  # Mono
RATE = 44100  # 44.1kHz sampling rate
CHUNK = 1024  # Number of frames per buffer

# Initialize PyAudio
p = pyaudio.PyAudio()

# Create a stream to read data
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

# Global variable to store audio data
audio_data = np.zeros(CHUNK, dtype=np.int16)

# Function to read audio data in a separate thread
def read_audio_data():
    global audio_data
    while True:
        data = stream.read(CHUNK, exception_on_overflow=False)
        audio_data = np.frombuffer(data, dtype=np.int16)
        dpg.set_value("audio_series", [list(range(CHUNK)), audio_data.tolist()])

# Function to start the audio reading thread
def start_audio_thread():
    audio_thread = threading.Thread(target=read_audio_data, daemon=True)
    audio_thread.start()

# Initialize DearPyGui
dpg.create_context()

with dpg.window(label="Microphone Input", width=600, height=400):
    dpg.add_text("Audio Waveform")
    with dpg.plot(label="Waveform Plot", height=-1):
        dpg.add_plot_axis(dpg.mvXAxis, label="Samples")
        with dpg.plot_axis(dpg.mvYAxis, label="Amplitude"):
            dpg.add_line_series([], [], label="Audio Data", parent=dpg.last_item(), id="audio_series")


dpg.create_viewport(title='Microphone Input', width=600, height=400)
dpg.setup_dearpygui()
dpg.show_viewport()

# Start the audio thread
start_audio_thread()

dpg.start_dearpygui()
dpg.destroy_context()

# Close the audio stream
stream.stop_stream()
stream.close()
p.terminate()
