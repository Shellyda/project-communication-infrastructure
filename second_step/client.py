import socket as skt
import struct
from random import *
import env_props as env # Environment properties

bind_address = env.CLIENT_HOST

MAX_BUFF_SIZE = env.MAX_BUFF_SIZE  # 1024 Bytes

class UDPClient:
    def __init__(self, socket_family=skt.AF_INET, socket_type=skt.SOCK_DGRAM, socket_binding=bind_address):
        self.client_socket = skt.socket(socket_family, socket_type)
        self.client_socket.bind(socket_binding) # Binding the socket to the address
        self.state = ""

    def sendAck(self, ack, seq, target_address):
        # global endFlag
        data = struct.pack('i', ack)
        # receiverSocket.sendto(data, addr)
        if randint(0, 9):  # 10% loss rate
            self.client_socket.sendto(data, target_address) # Sends the data to the destination
        else: 
            print('\x1b[1;31;40m' + f'Ack {seq} lost' + '\x1b[0m')
            # endFlag = 0

    def receive(self):

        self.endFlag = 0

        message, target_address = self.client_socket.recvfrom(MAX_BUFF_SIZE)
        file_name = message.decode().replace('\0', '')

        file_name = "received_" + file_name # Rename the file
        file = open(file_name, 'wb') # Open the file in binary mode

        self.action = "sendAck0"

        while(True): # Main loop of the receiver's finite state machine
    
            if self.state == "waitSeq_0": # State of waiting for packet 0
                print("Waiting for SeqNum=0")
                try:
                    pckg, target_address = self.client_socket.recvfrom(MAX_BUFF_SIZE) # Receives the packet if any arrives
                except: 
                    print('an exception occurred (waitSeq_0)')
                    pass # While there is no packet to receive, just wait
                else:
                    print('\x1b[1;32;40m' + 'Packet received' + '\x1b[0m')
                    tam = len(pckg) - 4
                    pckg = struct.unpack_from(f'i {tam}s', pckg)
                    seq = pckg[0]
                    payload = pckg[1:]

                    if seq == 0:
                        if(payload[0] == b'END'): # If received final message from sender, end the loop
                            self.endFlag = 1
                        for i in payload:
                            file.write(i)

                        self.action = "sendAck0"  # Upon receiving the packet, if the sequence number is zero, send the corresponding ack
                    else: 
                        self.action = "sendAck1" # If the packet is not the correct one, send sequence 1 ack instead
                        if(payload[0] == b'END'): # If received final message from sender, end the loop
                            self.endFlag = 1

            elif self.state == "waitSeq_1": # State of waiting for packet 1
                print("Waiting for SeqNum=1")
                try:
                    pckg, target_address = self.client_socket.recvfrom(MAX_BUFF_SIZE) # Receives the packet if any arrives
                except: 
                    print('an exception occurred (waitSeq_1)')
                    pass  # Wait until a packet arrives
                else:
                    print('\x1b[1;32;40m' + 'Packet received' + '\x1b[0m')
                    tam = len(pckg) - 4
                    pckg = struct.unpack_from(f'i {tam}s', pckg)
                    seq = pckg[0]
                    payload = pckg[1:]

                    if seq == 1:
                        self.action = "sendAck1" # If the sequence of the packet is as expected, send sequence 1 ack, and should change the state
                        if(payload[0] == b'END'): # If received final message from sender, end the loop
                            self.endFlag = 1
                        for i in payload:
                            file.write(i)
                    else: 
                        self.action = "sendAck0" # If the sequence of the packet is not as expected, send sequence 0 ack, and should remain in the same state
                        if(payload[0] == b'END'): # If received final message from sender, end the loop
                            self.endFlag = 1

            if self.action == "sendAck0":
                print('\x1b[1;34;40m' + 'Ack 0 sent' + '\x1b[0m')
                self.sendAck(0, 0, target_address) # Send sequence 0 ack
                if self.endFlag:
                    file.close() 
                    break
                self.state = "waitSeq_1" # Change state to waitSeq_1
                
            elif self.action == "sendAck1":
                print('\x1b[1;34;40m' + 'Ack 1 sent' + '\x1b[0m')
                self.sendAck(1, 1, target_address) # Send sequence 1 ack
                if self.endFlag: 
                    file.close()
                    break
                self.state = "waitSeq_0" # Change state to waitSeq_0

def main():
    client = UDPClient()

    print(f"\n---------------------------------\n")
    print(f"🚀 Client is running on {bind_address[0]} with PORT {bind_address[1]}!")
    print(f"\n---------------------------------\n")

    client.receive()

    print(f"\n---------------------------------\n")
    print(f"🛑 Stopping client socket!")

    client.client_socket.close()
    
    print(f"\n---------------------------------\n")

    print('\x1b[7;35;47m' + 'End of program' + '\x1b[0m')


main()
