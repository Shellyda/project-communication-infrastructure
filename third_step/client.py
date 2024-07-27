import socket as skt
from threading import Thread
import env_props as env

MAX_BUFF_SIZE = env.MAX_BUFF_SIZE

class Client:
    def __init__(self, host, port):
        self.client_socket = skt.socket(skt.AF_INET, skt.SOCK_DGRAM)
        self.server_address = (host, port)
        self.username = None

    def send_message(self, message):
        self.client_socket.sendto(message.encode(), self.server_address)

    def receive_message(self):
        while True:
            data, _ = self.client_socket.recvfrom(MAX_BUFF_SIZE)
            print(data.decode())

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

        command = input("Enter your username to login: ")
        self.login(command)

        while True:
            if self.username is None:
                command = input("Enter your username to login: ")
                self.login(command)
            else:
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
    client = Client(env.SERVER_HOST, env.SERVER_PORT)
    client.run()
