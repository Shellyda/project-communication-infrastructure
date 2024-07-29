import socket as skt
from threading import Thread, Event
import env_props as env
import struct

MAX_BUFF_SIZE = env.MAX_BUFF_SIZE
target_address = env.SERVER_ADDRESS

class Client:
    def __init__(self, socket_family=skt.AF_INET, socket_type=skt.SOCK_DGRAM):
        self.client_socket = skt.socket(socket_family, socket_type)
        self.server_address = target_address
        self.username = None
        self.login_event = Event() 

    def send_message(self, message):
        message_encode = message.encode()
        sequence_number =  int(self.stateS[-1])
        packet_length = len(message_encode)
        data = bytearray(4 + packet_length)
        data = struct.pack(f'i {packet_length}s', sequence_number, message_encode)
        self.client_socket.sendto(data, self.server_address)
        print('\x1b[1;34;40m' + f'packet {sequence_number} sent' + '\x1b[0m')
        self.stateS = f"wait_ack_{sequence_number}"

    def receive_message(self):
        while True:
            data, _ = self.client_socket.recvfrom(MAX_BUFF_SIZE)
            message = data.decode()
            print(message)
            if message.startswith("Login successful"):
                self.username = message.split()[-1]
                self.login_event.set() 
            elif message.startswith("Username already in use"):
                self.login_event.set() 
                self.username = None

    def login(self, username):
        self.send_message(f"login {username}")
        self.waiting_for_ack()

    def logout(self):
        self.send_message(f"logout {self.username}")
        self.username = None
        #precisa tirar a maquina que deu logout do dicionario de state do server

    def create_accommodation(self, name, location):
        self.send_message(f"create {name} {location}")
        self.waiting_for_ack()

    def list_my_accommodations(self):
        self.send_message(f"list:myacmd")
        self.waiting_for_ack()

    def list_accommodations(self):
        self.send_message("list:acmd")
        self.waiting_for_ack()

    def list_my_reservations(self):
        self.send_message(f"list:myrsv")
        self.waiting_for_ack()

    def book_accommodation(self, owner, acmd_id, day):
        self.send_message(f"book {owner} {acmd_id} {day}")
        self.waiting_for_ack()

    def cancel_reservation(self, owner, acmd_id, day):
        self.send_message(f"cancel {owner} {acmd_id} {day}")
        self.waiting_for_ack()

    def show_help(self):
        self.send_message("--help")
        self.waiting_for_ack()

    def run(self):
        Thread(target=self.receive_message).start()
        while True:
            if self.username is None:
                command = input("Enter your username to login: ")
                self.login_event.clear()  
                self.login(command)
                self.login_event.wait() 
            else:
                print('Use --help to see available commands')
                command = input(f"{self.username}@client:~$ ")
                if command.startswith("login"):
                    print("You are already logged in.")
                elif command.startswith("logout"):
                    self.logout()
                elif command.startswith("create"):
                    _, name, location = command.split(maxsplit=3)
                    self.create_accommodation(name, location)
                elif command.startswith("list:myacmd"):
                    self.list_my_accommodations()
                elif command.startswith("list:acmd"):
                    self.list_accommodations()
                elif command.startswith("list:myrsv"):
                    self.list_my_reservations()
                elif command.startswith("book"):
                    _, owner, acmd_id, day = command.split()
                    self.book_accommodation(owner, acmd_id, day)
                elif command.startswith("cancel"):
                    _, owner, acmd_id, day = command.split()
                    self.cancel_reservation(owner, acmd_id, day)
                elif command.startswith("--help"):
                    self.show_help()
                else:
                    print('Command not valid! Use --help to see available commands.')
                    self.send_message(command)

if __name__ == "__main__":
    client = Client()
    client.run()
