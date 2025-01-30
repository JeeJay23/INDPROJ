"""Audio processing module"""

import pyopencl as ocl
import numpy as np
import pyaudio
import os
import threading
import queue

from nodes.myglobals import BLOCK_SIZE

# set environment variable to automatically select a platform
os.environ['PYOPENCL_CTX'] = ''
os.environ['PYOPENCL_COMPILER_OUTPUT'] = '1'

class AudioProcessing():
    """Audio processing module."""
    def __init__(self, 
                 chunk=BLOCK_SIZE,
                 dtype=np.float32, 
                 channels=1, 
                 rate=44100):
        self.audio_handler = pyaudio.PyAudio()
        self.audio_input_stream = None
        self.audio_data = None
        self.audio_chunk_size = chunk
        self.data_type = dtype
        self.num_audio_channels = channels
        self.sample_rate = rate

        self.running = False

        self.filters = {}

        self.on_audio_received = None
        self.on_processed_audio = None
        self.audio_thread = None
        self.processing_thread = None
        self.stop_audio_thread = False
        self.stop_processing_thread = False

        self.playback = False

        self.gain = 1.0

        self.audio_queue = queue.Queue()

        self.ctx = ocl.create_some_context()

        with open('src/kernel.cl', 'r') as f:
            kernel_code = f.read()

        self.program = ocl.Program(self.ctx, kernel_code).build()
        self.cl_queue = ocl.CommandQueue(self.ctx)
    
    def load_filter(self, filter_name, filter_path):
        """Load a filter from a file."""
        self.filters[filter_name] = np.loadtxt(filter_path, delimiter=',', dtype=np.float32)

    def read_audio_data(self):
        """Audio reading processed on a separate thread."""
        print("AudioProcessing: reading audio data...")
        while (not self.stop_audio_thread):
            data = self.audio_input_stream.read(self.audio_chunk_size, exception_on_overflow=False)
            self.audio_data = np.frombuffer(data, dtype=self.data_type)
            if self.on_audio_received:
                self.on_audio_received(self.audio_data)
            self.audio_queue.put(self.audio_data)

    def process_audio(self):
        """Process audio data."""
        while (not self.stop_processing_thread):
            chunk = None
            if not self.audio_queue.empty():
                chunk = self.audio_queue.get()
                if chunk is None:
                    continue
            else:
                continue

            mf = ocl.mem_flags
            input_buffer = ocl.Buffer(self.ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=chunk)
            gain_output_buffer = ocl.Buffer(self.ctx, mf.READ_WRITE, chunk.nbytes)

            self.program.apply_gain(self.cl_queue,
                                    chunk.shape,
                                    None,
                                    input_buffer,
                                    gain_output_buffer,
                                    np.float32(self.gain))

            conv_output_buffer = ocl.Buffer(self.ctx, mf.WRITE_ONLY, chunk.nbytes)
            coef_input_buffer = ocl.Buffer(self.ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=self.filters['low_pass_2'])

            self.program.apply_convolution(self.cl_queue,
                                           chunk.shape,
                                           None,
                                           gain_output_buffer,
                                           coef_input_buffer,
                                           conv_output_buffer,
                                           np.int32(100),
                                           np.int32(chunk.shape[0]))

            dft_output = np.empty_like(chunk)
            dft_output_buffer = ocl.Buffer(self.ctx, mf.WRITE_ONLY, dft_output.nbytes)

            self.program.dft(self.cl_queue,
                             chunk.shape,
                             None,
                             conv_output_buffer,
                             dft_output_buffer,
                             np.int32(chunk.shape[0]),
                             np.int32(1))

            processed_chunk = np.empty_like(chunk)
            ocl.enqueue_copy(self.cl_queue, processed_chunk, conv_output_buffer).wait()
            ocl.enqueue_copy(self.cl_queue, dft_output, dft_output_buffer).wait()

            if self.playback:
                self.out_stream.write(processed_chunk.tobytes())

            if self.on_processed_audio:
                self.on_processed_audio(chunk, processed_chunk, dft_output)
                
    def open_stream(self):
        self.running = True
        """Open the audio stream."""
        self.audio_input_stream = self.audio_handler.open(
                                format=pyaudio.paFloat32,
                                channels=self.num_audio_channels,
                                rate=self.sample_rate,
                                input=True,
                                frames_per_buffer=self.audio_chunk_size)
        self.audio_data = np.zeros(self.audio_chunk_size, dtype=self.data_type)
        self.audio_thread = threading.Thread(target=self.read_audio_data, daemon=True)
        self.audio_thread.start()
        self.processing_thread = threading.Thread(target=self.process_audio, daemon=True)
        self.processing_thread.start()

        self.out_stream = self.audio_handler.open(
                                format=pyaudio.paFloat32,
                                channels=self.num_audio_channels,
                                rate=self.sample_rate,
                                output=True,
                                frames_per_buffer=self.audio_chunk_size)

    def close_stream(self):
        self.running = False
        """Close the audio stream."""
        self.stop_audio_thread = True
        self.stop_processing_thread = True
        if (self.audio_input_stream):
            self.audio_input_stream.stop_stream()
            self.audio_input_stream.close()
        self.audio_handler.terminate()