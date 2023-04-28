from RATFunction import RATFunction


class RATFunctionRegistry(object):
    def __init__(self):
        self.functions = []

    def add_function(self, function: RATFunction):
        self.functions.append(function)

