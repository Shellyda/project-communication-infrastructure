import socket as skt
import struct
from random import *
import env_props as env # Environment properties

MAX_BUFF_SIZE = env.MAX_BUFF_SIZE  # 1024 Bytes

class RDT_Receiver:
    def __init__(self, socket_family=skt.AF_INET, socket_type=skt.SOCK_DGRAM):
        self.socket = skt.socket(socket_family, socket_type)
        self.state = ""

    def send_acknowledgement(self, ack, sequence_number, target_address):
        # print('\x1b[1;34;40m' + f'ACK {sequence_number} sent' + '\x1b[0m')
        data = struct.pack('i', ack)
        if randint(0, 9):  # Simulating 10% loss rate
            self.socket.sendto(data, target_address) # Sends the data to the destination
        # else: 
        #     print('\x1b[1;31;40m' + f'ACK = {sequence_number} lost' + '\x1b[0m')
        if sequence_number == 0:
            self.state = "wait_seq_1" # Change state to wait_seq_1
        elif sequence_number == 1:
            self.state = "wait_seq_0" # Change state to wait_seq_1

    def waiting_for_packet(self, expected_seq_number):
        # print(f"Waiting for a packet whose sequence_number = {expected_seq_number}")
        try:
            packet, _ = self.socket.recvfrom(MAX_BUFF_SIZE) # Receives the packet if any arrives
        except: 
            # print(f'an exception occurred (wait_seq_{expected_seq_number})')
            pass # While there is no packet to receive, just wait
        else:
            # print('\x1b[1;32;40m' + 'Packet received' + '\x1b[0m')
            length = len(packet) - 4
            packet = struct.unpack_from(f'i {length}s', packet)
            sequence_number = packet[0]
            
            if sequence_number == expected_seq_number:
                self.action = f"send_ack_{expected_seq_number}"  # Upon receiving the packet, if the sequence number is zero or one, send the corresponding ack
            else: 
                if expected_seq_number == 0:
                    self.action = "send_ack_1" # If the packet is not the correct one, send the corresponding ack instead
                elif expected_seq_number == 1:
                    self.action  = "send_ack_0" # If the packet is not the correct one, send the corresponding ack instead
    
    def send(self, message, target_address):
        print('message to send to server', message)
        self.socket.sendto(message.encode(), target_address)

    def receive(self):
        # print("Waiting for a packet whose sequence_number = 0")
        data, target_address = self.socket.recvfrom(MAX_BUFF_SIZE) # Receiving the file name
        
        # print('\x1b[1;32;40m' + 'Packet received' + '\x1b[0m')

        self.action = "send_ack_0"

        while not data: # Main loop of the receiver's finite state machine
            if self.state == "wait_seq_0": # State of waiting for packet 0
                self.waiting_for_packet(0)

            elif self.state == "wait_seq_1": # State of waiting for packet 1
                self.waiting_for_packet(1)

            if self.action == "send_ack_0":
                self.send_acknowledgement(0, 0, target_address) # Send sequence 0 ack    
            elif self.action == "send_ack_1":
                self.send_acknowledgement(1, 1, target_address) # Send sequence 1 ack
                
        return data.decode()

