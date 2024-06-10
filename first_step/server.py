import socket as skt
import time
import env_props as env # Environment properties

bind_address = env.SERVER_HOST
target_address = env.CLIENT_HOST # Target
MAX_BUFF_SIZE = env.MAX_BUFF_SIZE  # 1024 Bytes

class UDPServer:
    def __init__(self, socket_family=skt.AF_INET, socket_type=skt.SOCK_DGRAM, socket_binding=bind_address):
        self.server_socket = skt.socket(socket_family, socket_type)
        self.server_socket.bind(socket_binding) # Binding the socket to the address
        self.server_socket.settimeout(0.1) # 100ms

    def receive(self):
        while True:
            try:
                message, origin_address = self.server_socket.recvfrom(MAX_BUFF_SIZE)
                bytes_from_message = b""
                file_name = message.decode() # Decode the file name

                print(f"📥 Receiving file '{file_name}' from HOST {origin_address[0]} with PORT {origin_address[1]}!")
                print(f"📦 File size: {len(message)} bytes")
                print(f"💾 Saving file as 'server_received_{file_name}'...")

                file_name = "server_received_" + file_name # Rename the file
                file = open(file_name, 'wb') # Open the file in binary mode

                datagram_count = 0
                still_have_data_to_get = True
                while still_have_data_to_get: # While the datagram is not empty
                    datagram, origin_address = self.server_socket.recvfrom(MAX_BUFF_SIZE)
                    bytes_from_message += datagram
                    datagram_count += 1
                    still_have_data_to_get = datagram != b""

                print(f"📊 Received {datagram_count} datagrams from HOST {origin_address[0]} with port {origin_address[1]}!")
                print(f"🆕 Writing {len(bytes_from_message)} bytes to '{file_name}'...")
                print("✅ File saved from Server!")

                file.write(bytes_from_message)
                file.close()

                return message

            except skt.timeout:
                continue

    def send(self, message: bytes, target_address: tuple[str, str]):
        file = open(message, 'rb') # Open the file in binary mode
        file_name = message.decode() # Decode the file name
        
        print(f"📤 Sending file '{file_name}' to HOST {target_address[0]} with PORT {target_address[1]}...")

        self.server_socket.sendto(message, target_address) # Send the file name to client

        still_have_data_to_send = True
        while still_have_data_to_send:
            datagram = file.read(MAX_BUFF_SIZE) # Read the file in chunks of 1024 bytes
            self.server_socket.sendto(datagram, target_address)
            still_have_data_to_send = len(datagram) > 0

        self.server_socket.sendto(b"", target_address) # Send an empty message to signal the end of the file

        print(f"✅ File '{file_name}' sent to HOST {target_address[0]} with PORT {target_address[1]}!")

        time.sleep(0.0001) # Sleep for 100ms
        file.close()

def main():
    # Creating a UDP socket (SOCK_DGRAM) using IPv4 (AF_INET).
    server = UDPServer()

    print(f"\n---------------------------------\n")
    print(f"🌐 Server is running on {bind_address[0]} with PORT {bind_address[1]}!")
    print(f"\n---------------------------------\n")
    
    # 1. Receive the file from the client 
    message = server.receive() 

    print(f"\n---------------------------------\n")

    # 2. Send the file to the client
    server.send(message, target_address) 

    print(f"\n---------------------------------\n")

    print(f"🛑 Stopping server socket!")
    server.server_socket.close()


main()
