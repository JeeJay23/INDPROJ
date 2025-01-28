"""Main entry point of the application"""

import dearpygui.dearpygui as dpg
import numpy as np
import audio_processing 
import nodes

dpg.create_context()
dpg.create_viewport(title='Custom DSPedal', width=1200, height=900)
ap = audio_processing.AudioProcessing()
GRAPH_MAX_AMP = 1.0
GRAPH_MIN_AMP = -1.0

def link_callback(sender, app_data):
    from_node = dpg.get_item_user_data(app_data[0])
    to_node = dpg.get_item_user_data(app_data[1])

    from_node.on_linked_output(to_node)
    to_node.on_linked_input(from_node)

    print(f'from node: {from_node} to node: {to_node}')

    dpg.add_node_link(app_data[0], app_data[1], parent=sender, user_data=(from_node, to_node))

def delink_callback(sender, app_data):
    # app_data -> link_id

    linked_nodes = dpg.get_item_user_data(app_data)
    linked_nodes[0].on_delinked_output(linked_nodes[1])
    linked_nodes[1].on_delinked_input(linked_nodes[0])

    print(f'from node: {linked_nodes[0]} to node: {linked_nodes[1]}')
    dpg.delete_item(app_data)

def on_update_buffer_size(sender, app_data):
    dpg.set_axis_limits("xAxis", 0, dpg.get_value("bufferSize"))
    dpg.set_axis_limits("xAxis_2", 0, dpg.get_value("bufferSize"))
    dpg.set_axis_limits("xAxis_3", 0, dpg.get_value("bufferSize"))

def open_stream(sender, app_data):
    global ap
    if (ap.running):
        ap.close_stream()

    ap = audio_processing.AudioProcessing()
    ap.audio_chunk_size = dpg.get_value("bufferSize")

    # all precomputed filters are created with an fs of 44100. Changing this value will cause the filters to break
    ap.sampling_rate = dpg.get_value("fs")
    ap.on_audio_received = update_plot
    ap.on_processed_audio = on_audio_processed
    ap.playback = True

    ap.load_filter('low_pass', 'src/filters/low_pass_10k.csv')
    ap.load_filter('low_pass_2', 'src/filters/low_pass_400.csv')
    ap.open_stream()

def close_stream(sender, app_data):
    ap.close_stream()

def on_audio_processed(chunk, processed_chunk, dtf_abs):
    dpg.set_value("audio_series_2", [list(range(dpg.get_value("bufferSize"))), processed_chunk.tolist()])
    dpg.set_value("freq_series", [list(range(int(dpg.get_value("bufferSize")))), dtf_abs.tolist()])

def on_gain_changed(sender, app_data):
    ap.gain = dpg.get_value(sender)

def update_plot(audio_data):
    dpg.set_value("audio_series", [list(range(dpg.get_value("bufferSize"))), audio_data.tolist()])

def on_update_yAxis(sender, app_data):
    dpg.set_axis_limits("yAxis", 0, dpg.get_value("freq_yscale"))


with dpg.window(label="Node editor", menubar=True) as node_editor:
    with dpg.node_editor(callback=link_callback, delink_callback=delink_callback):
        # with dpg.node(label="Audio input", tag="AudioInput"):
        #     with dpg.node_attribute(label="Audio buffer", attribute_type=dpg.mvNode_Attr_Output):
        #         dpg.add_slider_int(
        #             tag="bufferSize",
        #             label="buffer size",
        #             width=150,
        #             default_value=1024,
        #             min_value=100,
        #             max_value=2000,
        #             callback=on_update_buffer_size)
        #         dpg.add_input_float(tag="volume", label="volume", width=150, default_value=1.0)
        #         dpg.add_input_int(tag="fs", label="sample rate", width=150, default_value=44100)

        #         with dpg.plot(label="Waveform Plot", height=500):
        #             dpg.add_plot_axis(dpg.mvXAxis, label="Samples", tag="xAxis")
        #             dpg.set_axis_limits(dpg.last_item(), 0, dpg.get_value("bufferSize"))
        #             with dpg.plot_axis(dpg.mvYAxis, label="Amplitude"):
        #                 dpg.set_axis_limits(dpg.last_item(), GRAPH_MIN_AMP, GRAPH_MAX_AMP)
        #                 dpg.add_line_series([], [], label="Audio Data", parent=dpg.last_item(), tag="audio_series")

        #         dpg.add_button(label="Open stream", callback=open_stream)
        #         dpg.add_button(label="Close stream", callback=close_stream)

        # with dpg.node(label="Gain", tag="gain"):
        #     with dpg.node_attribute(label="Settings"):
        #         dpg.add_input_float(label="Gain", default_value=1, width=200, callback=on_gain_changed)
        #     with dpg.node_attribute(label="Output", attribute_type=dpg.mvNode_Attr_Output):
        #         pass
        
        # with dpg.node(label="Visualiser", tag="visualiser"):
        #     with dpg.node_attribute(label="Audio input", attribute_type=dpg.mvNode_Attr_Input):
        #         pass
        #     with dpg.node_attribute(label="visualiser", attribute_type=dpg.mvNode_Attr_Output):
        #         with dpg.plot(label="Waveform Plot", height=500):
        #             dpg.add_plot_axis(dpg.mvXAxis, label="Samples", tag="xAxis_2")
        #             dpg.set_axis_limits(dpg.last_item(), 0, dpg.get_value("bufferSize"))
        #             with dpg.plot_axis(dpg.mvYAxis, label="Amplitude"):
        #                 dpg.set_axis_limits(dpg.last_item(), GRAPH_MIN_AMP, GRAPH_MAX_AMP)
        #                 dpg.add_line_series([], [], label="Audio Data", parent=dpg.last_item(), tag="audio_series_2")
        
        # with dpg.node(label="Frequency spectrum", tag="freq_vis"):
        #     with dpg.node_attribute(label="Audio input", attribute_type=dpg.mvNode_Attr_Input):
        #         pass
        #     with dpg.node_attribute(label="visualiser", attribute_type=dpg.mvNode_Attr_Output):
        #         dpg.add_slider_int(
        #             tag="freq_yscale",
        #             label="frequency_y_scale",
        #             width=150,
        #             default_value=100,
        #             min_value=100,
        #             max_value=2000,
        #             callback=on_update_yAxis)
        #         with dpg.plot(label="Frequency Spectrum", height=500):
        #             dpg.add_plot_axis(dpg.mvXAxis, label="Frequency", tag="xAxis_3")
        #             # because we are submitting our input in chunks to the dft, we get a result of the same size
        #             dpg.set_axis_limits(dpg.last_item(), 0, dpg.get_value("bufferSize"))
        #             with dpg.plot_axis(dpg.mvYAxis, tag="yAxis", label="Magnitude"):
        #                 dpg.set_axis_limits(dpg.last_item(), 0, 1000)
        #                 dpg.add_line_series([], [], label="Frequency Data", parent=dpg.last_item(), tag="freq_series")

        # with dpg.node(label="Output", tag="out"):
        #     with dpg.node_attribute(label="Settings"):
        #         dpg.add_input_float(label="Volume", default_value=1, width=200)

        sine_output_node = nodes.SineOscillatorNode("Sinus Generator")
        audio_playback_node = nodes.AudioPlaybackNode("Audio Out")

dpg.setup_dearpygui()
dpg.show_item_registry()
dpg.show_viewport()
dpg.set_primary_window(node_editor, True)
dpg.start_dearpygui()
sine_output_node.stop()
dpg.destroy_context()
ap.close_stream()
