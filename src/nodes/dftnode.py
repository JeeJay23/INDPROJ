import numpy as np
import dearpygui.dearpygui as dpg

from nodes.myglobals import BLOCK_SIZE, SAMPLING_FREQ, NYQUIST_FREQ
from nodes.basenode import DspNode
import audio_processing as ap

import pyopencl as ocl

class DftNode(DspNode):
    def __init__(self, name, node_editor, ap_instance):
        # we only need the context and specific kernel for this operation
        self.ocl_context = ap_instance.ctx
        self.ocl_dft_kernel = ap_instance.program.dft
        self.input_buffer = np.zeros(BLOCK_SIZE, dtype=np.float32)
        self.output_buffer = np.zeros(BLOCK_SIZE, dtype=np.float32)
        self.dft_output_buffer = np.zeros(BLOCK_SIZE, dtype=np.float32)
        # static x axis
        # frequency range = 0 to sample_rate / 2
        # step size is sample_rate / block_size
        # since dft returns the entire frequency domain we need to divide the block size by 2
        samples = int(BLOCK_SIZE / 2 - 1)
        self.plot_x_axis_data = np.linspace(0, ap_instance.sample_rate / 2, samples).tolist()
        # self.plot_x_axis_data = self.in_buffer.tolist()
        super().__init__(name, node_editor)

    @DspNode._draw
    def draw(self):
        with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Input, user_data=self):
            dpg.add_text('Audio in')
        with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static, user_data=self):
            with dpg.plot(label="Frequency domain", height=500, width=500) as self.plot:
                self.plot_x_axis = dpg.add_plot_axis(
                    dpg.mvXAxis, 
                    label="Frequency (Hz)"
                )

                with dpg.plot_axis(dpg.mvYAxis, label="Magnitude") as self.plot_y_axis:
                    self.plot_series = dpg.add_line_series(self.plot_x_axis_data, self.dft_output_buffer, label="DFT")

                dpg.set_axis_limits_constraints(self.plot_x_axis, 0, NYQUIST_FREQ)
                dpg.set_axis_limits_constraints(self.plot_y_axis, -50, 1000)

        with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output, user_data=self):
            dpg.add_text('Audio out')
        with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output, user_data=self):
            dpg.add_text('DFT out')

    def refresh(self):
        dpg.set_value(
            self.plot_series, 
            [self.plot_x_axis_data, self.dft_output_buffer.tolist()]
        )

    def run(self):
        if len(self.input_nodes) == 0:
            print(f'{self.name}: no input nodes linked')
            return
        
        working_buffer = self.input_nodes[0].output_buffer.copy().astype(np.float32)

        ocl_input_buffer = ocl.Buffer(
            self.ocl_context,
            ocl.mem_flags.READ_ONLY | ocl.mem_flags.COPY_HOST_PTR,
            hostbuf=working_buffer
        )

        ocl_out_buffer = ocl.Buffer(
            self.ocl_context,
            ocl.mem_flags.WRITE_ONLY,
            working_buffer.nbytes
        )

        with ocl.CommandQueue(self.ocl_context) as queue:
            self.ocl_dft_kernel(
                queue,
                working_buffer.shape,
                None,
                ocl_input_buffer,
                ocl_out_buffer,
                np.int32(working_buffer.shape[0]),
                np.int32(1)
            )

            ocl.enqueue_copy(queue, self.dft_output_buffer, ocl_out_buffer)

        self.output_buffer = self.input_nodes[0].output_buffer
        self.refresh()
