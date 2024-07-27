import socket as skt
import struct
from threading import Thread
import env_props as env # Environment props

MAX_BUFF_SIZE = env.MAX_BUFF_SIZE

class Client:
    def __init__(self, host, port):
        # Create a UDP socket and associate it with the server address
        self.client_socket = skt.socket(skt.AF_INET, skt.SOCK_DGRAM)
        self.server_addr = (host, port)
        self.username = None

    def send_message(self, message):
        # Send a message to the server
        self.client_socket.sendto(message.encode(), self.server_addr)

    def receive_message(self):
        # Receive a message from the server
        while True:
            data, _ = self.client_socket.recvfrom(MAX_BUFF_SIZE)
            print(data.decode())

    def login(self, username):
        # Perform user login
        self.username = username
        self.send_message(f"login {username}")

    def logout(self):
        # Perform user logout
        if self.username:
            self.send_message(f"logout {self.username}")
            self.username = None

    def create_accommodation(self, name, location, description):
        # Create a new accommodation
        self.send_message(f"create {name} {location} {description}")

    def list_my_accommodations(self):
        # List client's accommodations
        if self.username:
            self.send_message(f"list:myacmd {self.username}")

    def list_accommodations(self):
        # List all available accommodations
        self.send_message("list:acmd")

    def list_my_reservations(self):
        # List client's reservations
        if self.username:
            self.send_message(f"list:myrsv {self.username}")

    def book_accommodation(self, owner, name, location, day, room):
        # Book an accommodation
        self.send_message(f"book {owner} {name} {location} {day} {room}")

    def cancel_reservation(self, owner, name, location, day):
        # Cancel a reservation
        self.send_message(f"cancel {owner} {name} {location} {day}")

    def run(self):
        # Start the client and wait for user commands
        print("Accommodation client started. Please login to continue.")
        Thread(target=self.receive_message).start()

        while True:
            command = input()
            action = command.split()[0]
            if action == "login":
                self.login(command.split()[1])
            elif action == "logout":
                self.logout()
            elif action == "create":
                self.create_accommodation(command.split()[1], command.split()[2], command.split()[3])
            elif action == "list:myacmd":
                self.list_my_accommodations()
            elif action == "list:acmd":
                self.list_accommodations()
            elif action == "list:myrsv":
                self.list_my_reservations()
            elif action == "book":
                self.book_accommodation(command.split()[1], command.split()[2], command.split()[3], command.split()[4], command.split()[5])
            elif action == "cancel":
                self.cancel_reservation(command.split()[1], command.split()[2], command.split()[3], command.split()[4])
            elif action == "--help":
                self.send_message("--help")
            else:
                print('This command is not valid, try again! \nIf needed you can type --help to get the commands list!')

if __name__ == "__main__":
    client = Client(env.SERVER_HOST, env.SERVER_PORT)
    client.run()
