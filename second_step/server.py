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

    def waiting_for_ack(self, sequence_number):
        # State of waiting for Ack, after packet has been sent
                print(f"Waiting for an ACK = {sequence_number}")
                try:
                    acknowledgement_packet = self.server_socket.recv(MAX_BUFF_SIZE) # If an Ack packet arrives, receives the Ack
                except skt.timeout:
                    print('\x1b[7;31;47m' + 'Transmitter Timeout' + '\x1b[0m')
                    self.action = f"resend_packet_seq_{sequence_number}" # If a timeout occurs, resend sequence packet 
                else:
                    acknowledgement_packet = struct.unpack_from('i', acknowledgement_packet) # Decodes the ACK packet
                    ack = acknowledgement_packet[0]             # Gets the ACK field of the packet
                    if ack == int(sequence_number):
                        print('\x1b[1;34;40m' + f'Ack {sequence_number} received' + '\x1b[0m')
                        self.action = f"stop_timer_{sequence_number}" # If the ACK is sequence_number, reset the timer
                    else:
                        self.action = f"resend_packet_seq_{sequence_number}" # If the ack has the wrong sequence, resend packet 

    def waiting_for_call(self, sequence_number):
        print(f"Waiting for a call with sequence_number = {sequence_number}")
        self.action = f"send_packet_seq_{sequence_number}" # Send sequence packet 

    def send_packet_sequence(self, sequence_number, data):
                if not data:
                    self.end_of_packet = True
                    self.send_packet(b'END', int(sequence_number))
                else: # there are still packets to send
                    self.send_packet(data, int(sequence_number))
                self.state = f"wait_ack_{sequence_number}"

    def stop_timer(self, new_call_sequence_number):
        self.server_socket.settimeout(TIMEOUT) # Reset timer
        self.state = f"wait_call_{new_call_sequence_number}"

    def resend_packet_sequence(self, sequence_number, data):
                print('\x1b[1;33;40m' + f'Resending Packet (sequence_number={sequence_number})' + '\x1b[0m')

                if not data:
                    self.end_of_packet = True
                    self.send_packet(b'END', int(sequence_number))
                else: # there are still packets to send
                    self.send_packet(data, int(sequence_number))
                self.state = f"wait_ack_{sequence_number}"

    
    def send(self, message):

        self.end_of_packet = False

        data = message.encode()
        self.send_packet(data, 0)

        file = open(message, 'rb') # Open the file in binary mode

        self.state = "wait_ack_0"

        while not self.end_of_packet: # Main loop of the sender's finite state machine
            # Waiting calls
            if self.state == "wait_call_0":
                # State of waiting to send sequence packet 0
                self.waiting_for_call('0')
            elif self.state == "wait_call_1":
                # State of waiting to send sequence packet 1
                self.waiting_for_call('1')
            elif self.state == "wait_ack_0":
                # State of waiting for Ack 0 after packet 0 has been sent
                self.waiting_for_ack('0')
            elif self.state == "wait_ack_1":
                # State of waiting for Ack 1 after packet 1 has been sent
                self.waiting_for_ack('1')

            # Packets sequences senders
            if self.action == "send_packet_seq_0":
               data = file.read(MAX_BUFF_SIZE)  # Read 1024 bytes from the file
               self.send_packet_sequence('0', data)
            elif self.action == "send_packet_seq_1":
               data = file.read(MAX_BUFF_SIZE)  # Read 1024 bytes from the file
               self.send_packet_sequence('1', data)

            # Stop timer
            elif self.action == "stop_timer_0":
                self.stop_timer('1')
            elif self.action == "stop_timer_1":
                self.stop_timer('0')
                
            # Resend packet
            elif self.action == "resend_packet_seq_0":
                self.resend_packet_sequence('0', data)
            elif self.action == "resend_packet_seq_1":
                self.resend_packet_sequence('1', data)

        
        file.close() # Transmission ended 

def main():
    server = UDPServer()

    print(f"\n---------------------------------\n")
    print(f"🌐 Server is running on {bind_address[0]} with PORT {bind_address[1]}!")
    print(f"\n---------------------------------\n")

    input_file = input("💬 Enter the file name to send to client, you can choose 'image.png' or 'text.txt': ")
    message = input_file

    server.send(message)

    print(f"\n---------------------------------\n")
    print(f"🛑 Stopping server socket!")

    server.server_socket.close()

    print(f"\n---------------------------------\n")

    print('\x1b[7;35;47m' + 'End of program' + '\x1b[0m')

main()
