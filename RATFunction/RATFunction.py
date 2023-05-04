from abc import ABC, abstractmethod


class Side:
    ADMIN_SIDE = 0
    REMOTE_SIDE = 1


class RATFunction(ABC):

    def __init__(self, side, packet_queue):
        self.side = side
        self.packet_queue = packet_queue

    def handle_packet_data(self, data):
        if self.side == Side.ADMIN_SIDE:
            self.handle_packet_admin_side(data)
        elif self.side == Side.REMOTE_SIDE:
            self.handle_packet_remote_side(data)

    @abstractmethod
    def handle_packet_admin_side(self, data):
        pass

    @abstractmethod
    def handle_packet_remote_side(self, data):
        pass

    @abstractmethod
    def identifier(self) -> int:
        pass
