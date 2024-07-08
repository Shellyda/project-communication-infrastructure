import socket as skt
import struct
from random import *
import env_props as env # Environment properties

bind_address = env.SERVER_HOST
target_address = env.CLIENT_HOST # Target

MAX_BUFF_SIZE = env.MAX_BUFF_SIZE - 4  # 1024 - sequence_number = 1024 - sizeof(int)
TIMEOUT = 1.0 # 1000ms

class UDPServer:
    def __init__(self, socket_family=skt.AF_INET, socket_type=skt.SOCK_DGRAM, socket_binding=bind_address):
        self.server_socket = skt.socket(socket_family, socket_type)
        self.server_socket.bind(socket_binding) # Binding the socket to the address
        self.server_socket.settimeout(TIMEOUT)
        self.state = ""

    def send_packet(self, payload, sequence_number): # Converts the data into a string representation and encodes it into bytes
        packet_length = len(payload)
        data = bytearray(4 + packet_length)
        data = struct.pack(f'i {packet_length}s', sequence_number, payload)
        print('\x1b[1;32;40m' + 'Packet sent' + '\x1b[0m')
        if randint(0, 3):   # 25% loss rate
            self.server_socket.sendto(data, target_address) # Sends the data to the destination
        else:
            print('\x1b[1;31;40m' + 'Packet lost' + '\x1b[0m')

    def send(self, message):

        self.end_of_packet = False

        data = message.encode()
        self.send_packet(data, 0)

        file = open(message, 'rb') # Open the file in binary mode

        self.state = "wait_ack_0"

        while not self.end_of_packet: # Main loop of the sender's finite state machine

            if self.state == "wait_call_0":
                # State of waiting to send sequence packet 0
                print("Waiting for a call with sequence_number = 0")
                self.action = "send_packet_seq_0" # Send sequence packet 0

            elif self.state == "wait_ack_0":
                # State of waiting for Ack 0 after packet 0 has been sent
                print("Waiting for an ACK = 0")
                try:
                    acknowledgement_packet = self.server_socket.recv(MAX_BUFF_SIZE) # If an Ack packet arrives, receives the Ack
                except skt.timeout:
                    print('\x1b[7;31;47m' + 'Transmitter Timeout' + '\x1b[0m')
                    self.action = "resend_packet_seq_0" # If a timeout occurs, resend sequence packet 0
                else:
                    acknowledgement_packet = struct.unpack_from('i', acknowledgement_packet) # Decodes the ACK packet
                    ack = acknowledgement_packet[0]             # Gets the ACK field of the packet
                    if ack == 0:
                        print('\x1b[1;34;40m' + 'Ack 0 received' + '\x1b[0m')
                        self.action = "stop_timer_0" # If the ACK is 0, reset the timer
                    else:
                        self.action = "resend_packet_seq_0" # If the ack has the wrong sequence, resend packet 0

            elif self.state == "wait_call_1":
                # State of waiting to send sequence packet 1
                print("Waiting for a call with sequence_number = 1")
                self.action = "send_packet_seq_1" # Send sequence packet 1

            elif self.state == "wait_ack_1":
                # State of waiting for Ack 1 after packet 1 has been sent
                print("Waiting for an ACK = 1")
                try:
                    acknowledgement_packet = self.server_socket.recv(MAX_BUFF_SIZE) # If an Ack packet arrives, receives the Ack
                except skt.timeout:
                    print('\x1b[7;31;47m' + 'Transmitter Timeout' + '\x1b[0m')
                    self.action = "resend_packet_seq_1" # If a timeout occurs, resend sequence packet 1
                else:
                    acknowledgement_packet = struct.unpack_from('i', acknowledgement_packet) # Decodes the ACK packet
                    ack = acknowledgement_packet[0]             # Gets the ACK field of the packet
                    if ack == 1:
                        self.action = "stop_timer_1" # If the ACK is 1, reset the timer
                        print('\x1b[1;34;40m' + 'Ack 1 received' + '\x1b[0m')
                    else:
                        self.action = "resend_packet_seq_1" # If the ack has the wrong sequence, resend packet 1

            if self.action == "send_packet_seq_0":
                data = file.read(MAX_BUFF_SIZE)  # Read 1024 bytes from the file
                if not data:
                    self.end_of_packet = True
                    self.send_packet(b'END', 0)
                else:
                    self.send_packet(data, 0)

                self.state = "wait_ack_0"

            elif self.action == "stop_timer_0":
                self.server_socket.settimeout(TIMEOUT) # Reset timer
                self.state = "wait_call_1"

            elif self.action == "send_packet_seq_1":
                data = file.read(MAX_BUFF_SIZE)  # Read 1024 bytes from the file
                if not data:
                    self.end_of_packet = True
                    self.send_packet(b'END', 1)
                else: # there are still packets to send
                    self.send_packet(data, 1)
                self.state = "wait_ack_1"

            elif self.action == "stop_timer_1":
                self.server_socket.settimeout(TIMEOUT) # Reset timer
                self.state = "wait_call_0"

            elif self.action == "resend_packet_seq_0":
                print('\x1b[1;33;40m' + 'Resending Packet (sequence_number=0)' + '\x1b[0m')

                if not data:
                    self.end_of_packet = True
                    self.send_packet(b'END', 0)
                else: # there are still packets to send
                    self.send_packet(data, 0)
                self.state = "wait_ack_0"

            elif self.action == "resend_packet_seq_1":
                print('\x1b[1;33;40m' + 'Resending Packet (sequence_number=1)' + '\x1b[0m')
                if not data:
                    self.end_of_packet = True
                    self.send_packet(b'END', 1)
                else: # there are still packets to send
                    self.send_packet(data, 1)
                self.state = "wait_ack_1"
        
        file.close() # Transmission ended and receiver received everything

def main():
    server = UDPServer()

    print(f"\n---------------------------------\n")
    print(f"🌐 Server is running on {bind_address[0]} with PORT {bind_address[1]}!")
    print(f"\n---------------------------------\n")

    input_file = input("💬 Enter the file name to send to server, you can choose 'image.png' or 'text.txt': ")
    message = input_file

    server.send(message)

    print(f"\n---------------------------------\n")
    print(f"🛑 Stopping server socket!")

    server.server_socket.close()

    print(f"\n---------------------------------\n")

    print('\x1b[7;35;47m' + 'End of program' + '\x1b[0m')

main()
