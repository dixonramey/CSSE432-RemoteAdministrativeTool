import struct
import sys
import traceback

from Constants import PACKET_SIZE
from RATFunction import RATFunction


class RATFunctionRegistry(object):
    def __init__(self):
        self.functions = {}

    def add_function(self, function: RATFunction):
        self.functions[function.identifier()] = function

    def route_packet(self, data):
        packet_id, _ = struct.unpack(f"I {PACKET_SIZE - 4}s", data)
        if packet_id in self.functions:
            function = self.functions[packet_id]
            try:
                function.handle_packet_data(data)
            except:
                traceback.print_exc(file=sys.stderr)

    def get_function(self, identifier):
        return self.functions[identifier]
