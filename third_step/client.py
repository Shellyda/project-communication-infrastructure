import socket as skt
from threading import Thread, Event
import env_props as env
from rdt_receiver import RDT_Receiver

MAX_BUFF_SIZE = env.MAX_BUFF_SIZE
target_address = env.SERVER_ADDRESS

class Client:
    def __init__(self, socket_family=skt.AF_INET, socket_type=skt.SOCK_DGRAM):
        self.client_socket = skt.socket(socket_family, socket_type)
        self.server_address = target_address
        self.username = None
        self.login_event = Event()  
        self.receiver = RDT_Receiver()

    def send_message(self, message):
        self.receiver.send(message, self.server_address)

    def receive_message(self):
        while True:
            data = self.receiver.receive()  # Usa o método receive do RDT_Receiver para receber dados
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

    def logout(self):
        self.send_message(f"logout {self.username}")
        self.username = None

    def create_accommodation(self, name, location):
        self.send_message(f"create {name} {location}")

    def list_my_accommodations(self):
        self.send_message(f"list:myacmd")

    def list_accommodations(self):
        self.send_message("list:acmd")

    def list_my_reservations(self):
        self.send_message(f"list:myrsv")

    def book_accommodation(self, owner, acmd_id, day):
        self.send_message(f"book {owner} {acmd_id} {day}")

    def cancel_reservation(self, owner, acmd_id, day):
        self.send_message(f"cancel {owner} {acmd_id} {day}")

    def show_help(self):
        self.send_message("--help")

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
