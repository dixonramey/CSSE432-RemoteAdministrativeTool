import struct

from RATFunction import RATFunction


class RATFunctionRegistry(object):
    def __init__(self):
        self.functions = {}

    def add_function(self, function: RATFunction):
        self.functions[function.identifier()] = function

    def route_packet(self, data):
        packet_id, _ = struct.unpack("I 2044s", data)
        if packet_id in self.functions:
            function = self.functions[packet_id]
            if function.enabled:
                function.handle_packet_data(data)

    def get_function(self, identifier):
        return self.functions[identifier]

