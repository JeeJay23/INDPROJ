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

    link = dpg.add_node_link(app_data[0], app_data[1], parent=sender, user_data=(from_node, to_node))
    from_node.out_links.append(link)

def delink_callback(sender, app_data):
    # app_data -> link_id

    linked_nodes = dpg.get_item_user_data(app_data)
    linked_nodes[0].on_delinked_output(linked_nodes[1])
    linked_nodes[1].on_delinked_input(linked_nodes[0])

    print(f'from node: {linked_nodes[0]} to node: {linked_nodes[1]}')
    dpg.delete_item(app_data)


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

node_list = []
node_editor = None

class NodeTypes():
    AUDIO = 'audio'
    SINE = 'sine'
    GAIN = 'gain'
    DFT = 'dft'

def add_node(nodetype):
    if node_editor is None:
        return
    elif (nodetype == NodeTypes.AUDIO):
        node = nodes.AudioPlaybackNode("Audio Input", node_editor)
    elif (nodetype == NodeTypes.SINE):
        node = nodes.SineOscillatorNode("Sine wave generator", node_editor)
    elif (nodetype == NodeTypes.GAIN):
        node = nodes.GainNode("Gain", node_editor, ap)
    elif (nodetype == NodeTypes.DFT):
        node = nodes.DftNode("Frequency Analyzer", node_editor, ap)

    node_list.append(node)

with dpg.window(label="Node editor", menubar=True) as main_window:
    with dpg.menu_bar():
        with dpg.menu(label='Add'):
            dpg.add_menu_item(label='Sine Oscillator', callback=lambda: add_node(NodeTypes.SINE))
            dpg.add_menu_item(label='Gain', callback=lambda ap: add_node(NodeTypes.GAIN))
            dpg.add_menu_item(label='Audio Playback', callback=lambda: add_node(NodeTypes.AUDIO))
            dpg.add_menu_item(label='Frequency Analyzer', callback=lambda: add_node(NodeTypes.DFT))

    with dpg.node_editor(
        callback=link_callback, 
        delink_callback=delink_callback, 
        minimap=True, 
        minimap_location=dpg.mvNodeMiniMap_Location_BottomRight
    ) as node_editor:
        pass
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

def delete_node(sender, app_data):
    node_tags = dpg.get_selected_nodes(node_editor=node_editor)
    for tag in node_tags:
        node = dpg.get_item_user_data(tag)
        node.on_delete()


with dpg.handler_registry():
    del_down = dpg.add_key_press_handler(
        dpg.mvKey_Delete,
        callback=delete_node
    )

dpg.setup_dearpygui()
# dpg.show_item_registry()
dpg.show_viewport()
dpg.set_primary_window(main_window, True)
dpg.start_dearpygui()

# cleanup

for node in node_list:
    node.on_delete()
dpg.destroy_context()
ap.close_stream()
