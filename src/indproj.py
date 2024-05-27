"""Main enty point for the application."""

import pyopencl as cl
import dearpygui as dpg
import numpy as np
import wave
import pyaudio
import os

os.environ['PYOPENCL_CTX'] = ''

ctx = cl.create_some_context()
queue = cl.CommandQueue(ctx)

with open('src/kernel.cl', 'r') as f:
    kernel_code = f.read()

program = cl.Program(ctx, kernel_code).build()

def read_wavefile(filename, dtype=np.int16):
    """Reads a wave file and returns the audio data as a numpy array."""
    with wave.open(filename, 'rb') as wf:
        n_channels = wf.getnchannels()
        n_samples = wf.getnframes()
        fs = wf.getframerate()
        sample_size = wf.getsampwidth()

        raw = wf.readframes(n_samples)
        audio_data = np.frombuffer(raw, dtype=np.int16).astype(dtype)

        n = 15
        print(f"audio_data: {audio_data[n]}\nhex: 0x{raw[n*2:(n*2)+2].hex()}\nfloat16: {np.frombuffer(raw[n*2:(n*2)+2], dtype=np.int16)}")

        return audio_data, n_channels, n_samples, fs, sample_size

input_data, nChannels, nFrames, sampleRate, sampWidth = read_wavefile('chime.wav', np.float32)
# input_data = np.nan_to_num(input_data)

# print(f'Channels: {nChannels}, Frames: {nFrames}, Frame Rate: {sampleRate}, Sample Width: {sampWidth}')

input_buffer = cl.Buffer(ctx, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=input_data)
output_buffer = cl.Buffer(ctx, cl.mem_flags.WRITE_ONLY, input_data.nbytes)

program.apply_gain(queue, input_data.shape, None, input_buffer, output_buffer, np.float32(.1))
output_data = np.empty_like(input_data)

print(f"nans: {np.count_nonzero(np.isnan(input_data))}")

cl.enqueue_copy(queue, output_data, output_buffer).wait()

with wave.open('output_gain.wav', 'wb') as wf:
    wf.setnchannels(nChannels)
    wf.setsampwidth(sampWidth)
    wf.setframerate(sampleRate)
    wf.writeframes(output_data.astype(dtype=np.int16).tobytes())
