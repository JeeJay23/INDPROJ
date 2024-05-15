"""Main enty point for the application."""

import pyopencl as cl
import dearpygui as dpg
import numpy as np
import wave
import pyaudio

ctx = cl.create_some_context()
queue = cl.CommandQueue(ctx)

with open('src/kernel.cl', 'r') as f:
    kernel_code = f.read()

program = cl.Program(ctx, kernel_code).build()

def read_wavefile(filename):
    with wave.open(filename, 'rb') as wf:
        nChannels = wf.getnchannels()
        nFrames = wf.getnframes()
        frameRate = wf.getframerate()
        sampWidth = wf.getsampwidth()

        raw = wf.readframes(nFrames)
        audio_data = np.frombuffer(raw, dtype=np.float32)

        return audio_data, nChannels, nFrames, frameRate, sampWidth


audio_data, nChannels, nFrames, frameRate, sampWidth = read_wavefile('output.wav')

print(f'Channels: {nChannels}, Frames: {nFrames}, Frame Rate: {frameRate}, Sample Width: {sampWidth}')
print(audio_data.shape)

test_data = np.array(range(0, 10), dtype=np.float32)

input_buffer = cl.Buffer(ctx, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=test_data)
output_buffer = cl.Buffer(ctx, cl.mem_flags.WRITE_ONLY, audio_data.nbytes)

program.apply_gain(queue, test_data.shape, None, input_buffer, output_buffer)
output_data = np.empty_like(test_data)
cl.enqueue_copy(queue, output_data, output_buffer).wait()

print(output_data)
