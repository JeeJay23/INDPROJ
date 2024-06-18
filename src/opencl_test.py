"""Audio processing module"""

import pyopencl as cl
import numpy as np
import wave
import pyaudio
import os

os.environ['PYOPENCL_CTX'] = ''

ctx = cl.create_some_context()
queue = cl.CommandQueue(ctx)
p = pyaudio.PyAudio()

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

        return audio_data, n_channels, n_samples, fs, sample_size


def test_filter_1():
    # load exported coefficients
    coefs = np.loadtxt('src/filters/export.csv', delimiter=',', dtype=np.float32)

    input_data, nChannels, nFrames, sampleRate, sampWidth = read_wavefile('chime.wav', np.float32)
    print(f'loaded settings: channels: {nChannels}, Frames: {nFrames}, Frame Rate: {sampleRate}, Sample Width: {sampWidth}')

    input_buffer = cl.Buffer(ctx, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=input_data)
    coef_buffer = cl.Buffer(ctx, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=coefs)

    output_buffer = cl.Buffer(ctx, cl.mem_flags.WRITE_ONLY, input_data.nbytes)

    # program.apply_gain(queue, input_data.shape, None, input_buffer, output_buffer, np.float32(.1))
    program.apply_convolution(queue,
                            input_data.shape,
                            None, 
                            input_buffer, 
                            coef_buffer,
                            output_buffer, 
                            np.int32(coefs.shape[0]),
                            np.int32(input_data.shape[0]))

    output_data = np.empty_like(input_data)

    cl.enqueue_copy(queue, output_data, output_buffer).wait()

    print(f"output_data: {output_data}")

    with wave.open('output_bandpass_text.wav', 'wb') as wf:
        wf.setnchannels(nChannels)
        wf.setsampwidth(sampWidth)
        wf.setframerate(sampleRate)
        wf.writeframes(output_data.astype(dtype=np.int16).tobytes())

def test_dft():
    x_0 = np.array([1, 2, 3, 4], dtype=np.float32)
    output = np.empty_like(x_0)

    in_buffer = cl.Buffer(ctx, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=x_0)
    out_buffer = cl.Buffer(ctx, cl.mem_flags.WRITE_ONLY, x_0.nbytes)

    program.dft(queue, x_0.shape, None, in_buffer, out_buffer, np.int32(x_0.shape[0]), np.int32(1))

    cl.enqueue_copy(queue, output, out_buffer).wait()
    print(f"output: {output}")

def test_dft2():
    x_0 = np.array([1, 0, 2, 0, 3, 0, 4, 0], dtype=np.float32)
    output = np.empty_like(x_0)

    in_buffer = cl.Buffer(ctx, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=x_0)
    out_buffer = cl.Buffer(ctx, cl.mem_flags.WRITE_ONLY, x_0.nbytes)

    program.dft2(queue, x_0.shape, None, in_buffer, out_buffer, np.int32(x_0.shape[0] / 2), np.int32(1))

    cl.enqueue_copy(queue, output, out_buffer).wait()
    print(f"output: {output}")

test_dft()

