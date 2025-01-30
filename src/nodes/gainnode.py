import numpy as np
import dearpygui.dearpygui as dpg

from nodes.myglobals import BLOCK_SIZE
from nodes.basenode import DspNode
import audio_processing as ap

import pyopencl as ocl

class GainNode(DspNode):
    def __init__(self, name, node_editor, ap_instance):
        self.gain = 2.0
        self.block_size = BLOCK_SIZE
        self.output_buffer = np.zeros(self.block_size, dtype=np.float32)
        self.ap_intance = ap_instance

        # self.queue = ocl.CommandQueue(self.ap_intance.ctx)

        super().__init__(name, node_editor)
        self.run()

    @DspNode._draw
    def draw(self):
        with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Input, user_data=self):
            self.input_gain = dpg.add_slider_float(
                label="Gain",
                width=200,
                default_value=self.gain,
                min_value=0,
                max_value=10,
                callback=self.on_gain_changed
            )
        
        with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
            with dpg.tree_node(label="Visualiser", default_open=True):
                self.graph = dpg.add_simple_plot(width=300, height=250)
                dpg.set_value(self.graph, self.output_buffer.tolist())
            
        self.output = dpg.add_node_attribute(
            label="Output",
            parent=self.node_id,
            attribute_type=dpg.mvNode_Attr_Output,
            user_data=self
        )

    def stop(self):
        pass
        
    def refresh(self):
        dpg.set_value(self.graph, self.output_buffer.tolist())
    
    def on_gain_changed(self, sender, app_data):
        self.gain = app_data
        self.run()
    
    def run(self):
        if (len(self.input_nodes) == 0):
            print(f'{self.name}: no input nodes linked')
            return

        # copy input buffer, the kernel works with 32b floats
        working_buf = self.input_nodes[0].output_buffer.copy().astype(np.float32)

        # setup ocl buffer linking to the working buffer
        in_buf = ocl.Buffer(
            self.ap_intance.ctx,
            ocl.mem_flags.READ_ONLY | ocl.mem_flags.COPY_HOST_PTR,
            hostbuf=working_buf
        )

        # setup ocl buffer for output ot write to
        out_buf = ocl.Buffer(
            self.ap_intance.ctx,
            ocl.mem_flags.READ_WRITE,
            working_buf.nbytes
        )

        with ocl.CommandQueue(self.ap_intance.ctx) as queue:
            self.ap_intance.program.apply_gain(
                queue,
                working_buf.shape,
                None,
                in_buf,
                out_buf,
                np.float32(self.gain)
            )
            # write to output buffer once were done
            ocl.enqueue_copy(queue, self.output_buffer, out_buf).wait()

        self.refresh()
