class DspNode():
    def __init__(self, name):
        self.name = name
        self.is_active = False
        self.input_nodes = []
        self.output_nodes = []
        self.draw()
        self.run()

    def draw(self):
        print(f'{self}: base draw method, override me!')

    def run(self):
        print(f'{self}: base run method, override me!')

    def on_linked_input(self, node):
        print(f'{self.name}: linked input from {node.name}')
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