import dearpygui.dearpygui as dpg

class DspNode():
    def __init__(self, name):
        with dpg.node(label=name) as self.nodeId:
            with dpg.node_attribute():
                dpg.add_input_float(label="Gain", default_value=1, width=200, callback=self.on_gain_changed)
            self.output = dpg.add_node_attribute(label="Output", parent=self.nodeId, attribute_type=dpg.mvNode_Attr_Output)

    def on_gain_changed(self, sender, app_data):
        print(dpg.get_value())
