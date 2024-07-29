import socket as skt
import struct
from random import *
import env_props as env # Environment properties

bind_address = env.CLIENT_HOST

MAX_BUFF_SIZE = env.MAX_BUFF_SIZE  # 1024 Bytes
TIMEOUT = 1.0 # 1000ms

class Rdt3:
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
                        print('\x1b[1;34;40m' + f'ACK {sequence_number} received' + '\x1b[0m')
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

    def send_acknowledgement(self, ack, sequence_number, target_address):
        print('\x1b[1;34;40m' + f'ACK {sequence_number} sent' + '\x1b[0m')
        data = struct.pack('i', ack)
        if randint(0, 9):  # Simulating 10% loss rate
            self.client_socket.sendto(data, target_address) # Sends the data to the destination
        else: 
            print('\x1b[1;31;40m' + f'ACK = {sequence_number} lost' + '\x1b[0m')
        if sequence_number == 0:
            self.state = "wait_seq_1" # Change state to wait_seq_1
        elif sequence_number == 1:
            self.state = "wait_seq_0" # Change state to wait_seq_1

    def waiting_for_packet(self, file, expected_seq_number):
        print(f"Waiting for a packet whose sequence_number = {expected_seq_number}")
        try:
            packet, target_address = self.client_socket.recvfrom(MAX_BUFF_SIZE) # Receives the packet if any arrives
        except: 
            print(f'an exception occurred (wait_seq_{expected_seq_number})')
            pass # While there is no packet to receive, just wait
        else:
            print('\x1b[1;32;40m' + 'Packet received' + '\x1b[0m')
            length = len(packet) - 4
            packet = struct.unpack_from(f'i {length}s', packet)
            sequence_number = packet[0]
            payload = packet[1:]

            if sequence_number == expected_seq_number:
                if(payload[0] == b'END'): # If received final message from sender, end the loop
                    self.file_completed = True
                for i in payload:
                    file.write(i)

                self.action = f"send_ack_{expected_seq_number}"  # Upon receiving the packet, if the sequence number is zero or one, send the corresponding ack
            else: 
                if expected_seq_number == 0:
                    self.action = "send_ack_1" # If the packet is not the correct one, send the corresponding ack instead
                elif expected_seq_number == 1:
                    self.action  = "send_ack_0" # If the packet is not the correct one, send the corresponding ack instead
                if(payload[0] == b'END'): # If received final message from sender, end the loop
                    self.file_completed = True    

    def receive(self):

        self.file_completed = False # Flag to indicate that file was completely sent

        print("Waiting for a packet whose sequence_number = 0")
        message, target_address = self.client_socket.recvfrom(MAX_BUFF_SIZE) # Receiving the file name
        file_name = message.decode().replace('\0', '')
        print('\x1b[1;32;40m' + 'Packet received' + '\x1b[0m')

        file_name = "received_" + file_name # Rename the file
        file = open(file_name, 'wb') # Open the file in binary mode

        self.action = "send_ack_0"

        while not self.file_completed: # Main loop of the receiver's finite state machine
    
            if self.state == "wait_seq_0": # State of waiting for packet 0
                self.waiting_for_packet(file, 0)

            elif self.state == "wait_seq_1": # State of waiting for packet 1
                self.waiting_for_packet(file, 1)

            if self.action == "send_ack_0":
                self.send_acknowledgement(0, 0, target_address) # Send sequence 0 ack    
            elif self.action == "send_ack_1":
                self.send_acknowledgement(1, 1, target_address) # Send sequence 1 ack

        file.close() # Transmission ended