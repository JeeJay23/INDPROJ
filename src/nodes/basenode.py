import dearpygui.dearpygui as dpg

class DspNode():
    def __init__(self, name, node_editor):
        self.name = name
        self.is_active = False
        self.node_id = None # assigned in draw
        self.input_nodes = []
        self.output_nodes = []
        self.out_links = []
        self.node_editor = node_editor
        self.draw()
        self.run()

    def _draw(func):
        def wrapper(*args):
            _self = args[0]
            with dpg.node(label=_self.name, user_data=_self, parent=_self.node_editor) as _self.node_id:
                func(_self)
        return wrapper

    def draw(self):
        print(f'{self}: base draw method, override me!')

    def run(self):
        print(f'{self}: base run method, override me!')
    
    def on_delete(self):
        for node in self.output_nodes:
            node.on_delinked_input(self)
        for link in self.out_links:
            dpg.delete_item(link)
        dpg.delete_item(self.node_id)

    def on_linked_input(self, node):
        print(f'{self.name}: linked input from {node.name}')
        self.is_active = True
        node.run()
        self.input_nodes.append(node)

    def on_linked_output(self, node):
        print(f'{self.name}: linked output to {node.name}')
        self.is_active = True
        self.output_nodes.append(node)

    def on_delinked_input(self, node):
        print(f'{self.name}: delinked input from {node.name}')
        self.input_nodes.remove(node)
        self.is_active = False

    def on_delinked_output(self, node):
        print(f'{self.name}: delinked output to {node.name}')
        self.output_nodes.remove(node)
        if len(self.output_nodes) == 0:
            self.is_active = False