import socket as skt
import struct
from random import *
import env_props as env # Environment properties

bind_address = env.SENDER_HOST
MAX_BUFF_SIZE = env.MAX_BUFF_SIZE - 4  # 1024 - seqNum = 1024 - sizeof(int)
target_address = env.RECEIVER_HOST
time = 1.0 # 1000ms

class UDPServer:
    def __init__(self, socket_family=skt.AF_INET, socket_type=skt.SOCK_DGRAM, socket_binding=bind_address):
        self.server_socket = skt.socket(socket_family, socket_type)
        self.server_socket.bind(socket_binding) # Binding the socket to the address
        self.server_socket.settimeout(time)
        self.state = ""

    def sendPkt(self, payload, seqNum): # Converts the data into a string representation and encodes it into bytes
        tam = len(payload)
        data = bytearray(4 + tam)
        data = struct.pack(f'i {tam}s', seqNum, payload)
        print('\x1b[1;32;40m' + 'Packet sent' + '\x1b[0m')
        if randint(0, 3):   # 25% loss rate
            self.server_socket.sendto(data, target_address) # Sends the data to the destination
        else:
            print('\x1b[1;31;40m' + 'Packet lost' + '\x1b[0m')

    def send(self, message):

        self.fimPck = 0

        data = message.encode()

        self.sendPkt(data, 0)

        file = open(message, 'rb') # Open the file in binary mode

        self.state = "waitAck_0"

        print("exit")

        while(True): # Main loop of the sender's finite state machine

            if self.state == "waitCall_0":
                # State of waiting to send sequence packet 0
                print("Waiting for a call with SeqNum = 0")
                self.action = "sendPktSeq_0" # Send sequence packet 0

            elif self.state == "waitAck_0":
                # State of waiting for Ack 0 after packet 0 has been sent
                print("Waiting for an ACK = 0")
                try:
                    ack_pck = self.server_socket.recv(MAX_BUFF_SIZE) # If an Ack packet arrives, receives the Ack
                except skt.timeout:
                    print('\x1b[7;31;47m' + 'Transmitter Timeout' + '\x1b[0m')
                    self.action = "ReSendPktSeq_0" # If a timeout occurs, resend sequence packet 0
                else:
                    ack_pck = struct.unpack_from('i', ack_pck) # Decodes the ACK packet
                    ack = ack_pck[0]             # Gets the ACK field of the packet
                    if ack == 0:
                        print('\x1b[1;34;40m' + 'Ack 0 received' + '\x1b[0m')
                        self.action = "stopTimer_0" # If the ACK is 0, reset the timer
                        if self.fimPck:
                            file.close()
                            break
                    else:
                        self.action = "ReSendPktSeq_0" # If the ack has the wrong sequence, resend packet 0

            elif self.state == "waitCall_1":
                # State of waiting to send sequence packet 1
                print("Waiting for a call with SeqNum = 1")
                self.action = "sendPktSeq_1" # Send sequence packet 1

            elif self.state == "waitAck_1":
                # State of waiting for Ack 1 after packet 1 has been sent
                print("Waiting for an ACK = 1")
                try:
                    ack_pck = self.server_socket.recv(MAX_BUFF_SIZE) # If an Ack packet arrives, receives the Ack
                except skt.timeout:
                    print('\x1b[7;31;47m' + 'Transmitter Timeout' + '\x1b[0m')
                    self.action = "ReSendPktSeq_1" # If a timeout occurs, resend sequence packet 1
                else:
                    ack_pck = struct.unpack_from('i', ack_pck) # Decodes the ACK packet
                    ack = ack_pck[0]             # Gets the ACK field of the packet
                    if ack == 1:
                        self.action = "stopTimer_1" # If the ACK is 1, reset the timer
                        print('\x1b[1;34;40m' + 'Ack 1 received' + '\x1b[0m')
                        if self.fimPck: # Transmission ended and receiver received everything
                            file.close()
                            break
                    else:
                        self.action = "ReSendPktSeq_1" # If the ack has the wrong sequence, resend packet 1

            if self.action == "sendPktSeq_0":
                data = file.read(MAX_BUFF_SIZE)  # Read 1024 bytes from the file
                if not data:
                    self.fimPck = 1
                    self.sendPkt(b'END', 0)
                else:
                    self.sendPkt(data, 0)

                self.state = "waitAck_0"

            elif self.action == "stopTimer_0":
                self.server_socket.settimeout(time) # Reset timer
                self.state = "waitCall_1"

            elif self.action == "sendPktSeq_1":
                data = file.read(MAX_BUFF_SIZE)  # Read 1024 bytes from the file
                if not data:
                    self.fimPck = 1
                    self.sendPkt(b'END', 1)
                else: # there are still packets to send
                    self.sendPkt(data, 1)
                self.state = "waitAck_1"

            elif self.action == "stopTimer_1":
                self.server_socket.settimeout(time) # Reset timer
                self.state = "waitCall_0"

            elif self.action == "ReSendPktSeq_0":
                print('\x1b[1;33;40m' + 'Resending Packet (SeqNum=0)' + '\x1b[0m')

                if not data:
                    self.fimPck = 1
                    self.sendPkt(b'END', 0)
                else: # there are still packets to send
                    self.sendPkt(data, 0)
                self.state = "waitAck_0"

            elif self.action == "ReSendPktSeq_1":
                print('\x1b[1;33;40m' + 'Resending Packet (SeqNum=1)' + '\x1b[0m')
                if not data:
                    self.fimPck = 1
                    self.sendPkt(b'END', 1)
                else: # there are still packets to send
                    self.sendPkt(data, 1)
                self.state = "waitAck_1"

def main():

    server = UDPServer()

    input_file = input("💬 Enter the file name to send to server, you can choose 'image.png' or 'text.txt': ")
    message = input_file

    server.send(message)

    server.server_socket.close()

    print('\x1b[7;35;47m' + 'End of program' + '\x1b[0m')

main()
