import socket as skt
from threading import Thread
import struct
import env_props as env
from RDT_3_0 import RDT_Receiver, RDT_Sender

MAX_BUFF_SIZE = env.MAX_BUFF_SIZE
bind_address = env.SERVER_ADDRESS

class Server:
    def __init__(self, socket_family=skt.AF_INET, socket_type=skt.SOCK_DGRAM, socket_binding=bind_address):
        self.receiver = RDT_Receiver(socket_family, socket_type, socket_binding)
        self.sender = RDT_Sender(socket_family, socket_type, ('', 0))  # Para enviar pacotes de volta
        self.clients = {}  # {username: (address, port)}
        self.accommodations = {}  # {(name, location): {'id': id, 'owner': (username, addr), 'description': description, 'available_days': [days], 'reservations': {day: (username, addr)}}}
        self.reservations = {}  # {(owner, id, day): (guest_name, guest_addr)}
        self.available_days = ["17/07/2024", "18/07/2024", "19/07/2024", "20/07/2024", "21/07/2024", "22/07/2024"]
        self.stateS = {}  # {(address, port): (stateS)}
        self.stateR = {}  # {(address, port): (stateR)}

    def send_acknowledgement(self, ack, addr):
        print('\x1b[1;34;40m' + f'ACK {ack} sent' + '\x1b[0m')
        self.receiver.send_acknowledgement(ack, addr)
        if ack == 0:
            self.stateR[addr] = "wait_seq_1"  # Change state to wait_seq_1
        elif ack == 1:
            self.stateR[addr] = "wait_seq_0"  # Change state to wait_seq_1

    def machine_is_logged(self, addr):
        return addr in self.clients.values()

    def send_message(self, message, addr):
        sequence_number = int(self.stateS[addr][-1]) if addr in self.stateS else 0
        self.sender.handle_send_message(message, addr)
        self.stateS[addr] = f"wait_ack_{sequence_number}"

    def handle_client(self, data, addr):
        sequence_number, payload = self.receiver.waiting_for_packet(int(self.stateR[addr][-1]))
        if sequence_number is not None:
            command = payload[0].decode().split()
            action = command[0]

            print('\x1b[1;34;40m' + f'packet {sequence_number} received' + '\x1b[0m')

            self.send_acknowledgement(sequence_number, addr)

            if action == "login":
                self.login(command[1], addr)
            else:
                if self.machine_is_logged(addr):
                    if action == "logout":
                        self.logout(addr)
                    elif action == "create":
                        self.create_accommodation(command[1], command[2], addr)
                    elif action == "list:myacmd":
                        self.list_my_accommodations(addr)
                    elif action == "list:acmd":
                        self.list_accommodations(addr)
                    elif action == "list:myrsv":
                        self.list_my_reservations(addr)
                    elif action == "book":
                        self.book_accommodation(command[1], command[2], command[3], addr)
                    elif action == "cancel":
                        self.cancel_reservation(command[1], command[2], command[3], addr)
                    elif action == "--help":
                        self.show_help(addr)
                else:
                    print("nao logado, precisa implementar")

    def login(self, username, addr):
        if username in self.clients:
            self.send_message("Username already in use.", addr)
        else:
            self.clients[username] = addr
            self.send_message(f"Login successful {username}", addr)
            print(f'User [{username}/{addr[0]}:{addr[1]}] is connected!')

    def logout(self, addr):
        username = self.get_username_by_address(addr)
        if username in self.clients:
            del self.clients[username]
            self.send_message("Logout successful.", addr)
            print(f'User [{username}/{addr[0]}:{addr[1]}] is disconnected!')

    def create_accommodation(self, name, location, addr):
        owner = self.get_username_by_address(addr)
        accommodation_id = len(self.accommodations) + 1
        self.accommodations[(name, location)] = {
            'id': accommodation_id,
            'owner': (owner, addr),
            'description': f"Accommodation {name} at {location}.",
            'available_days': self.available_days.copy(),
            'reservations': {}
        }
        self.send_message(f"Accommodation {name} created successfully.", addr)

    def list_my_accommodations(self, addr):
        username = self.get_username_by_address(addr)
        my_accommodations = [acmd for acmd, details in self.accommodations.items() if details['owner'][0] == username]
        response = "Your accommodations:\n" + "\n".join(f"{name} at {location}" for name, location in my_accommodations)
        self.send_message(response, addr)

    def list_accommodations(self, addr):
        response = "All accommodations:\n" + "\n".join(f"{name} at {location}" for name, location in self.accommodations.keys())
        self.send_message(response, addr)

    def list_my_reservations(self, addr):
        username = self.get_username_by_address(addr)
        my_reservations = [f"{owner} {acmd_id} on {day}" for (owner, acmd_id, day), (guest, guest_addr) in self.reservations.items() if guest == username]
        response = "Your reservations:\n" + "\n".join(my_reservations)
        self.send_message(response, addr)

    def book_accommodation(self, owner, acmd_id, day, addr):
        acmd_key = next((key for key, details in self.accommodations.items() if details['owner'][0] == owner and details['id'] == int(acmd_id)), None)
        if acmd_key:
            if day in self.accommodations[acmd_key]['available_days']:
                guest = self.get_username_by_address(addr)
                self.reservations[(owner, int(acmd_id), day)] = (guest, addr)
                self.accommodations[acmd_key]['available_days'].remove(day)
                self.send_message(f"Reservation for {acmd_key[0]} on {day} booked successfully.", addr)
            else:
                self.send_message(f"Accommodation not available on {day}.", addr)
        else:
            self.send_message("Accommodation not found.", addr)

    def cancel_reservation(self, owner, acmd_id, day, addr):
        reservation_key = (owner, int(acmd_id), day)
        if reservation_key in self.reservations:
            del self.reservations[reservation_key]
            acmd_key = next((key for key, details in self.accommodations.items() if details['owner'][0] == owner and details['id'] == int(acmd_id)), None)
            if acmd_key:
                self.accommodations[acmd_key]['available_days'].append(day)
            self.send_message(f"Reservation for {acmd_key[0]} on {day} canceled successfully.", addr)
        else:
            self.send_message("Reservation not found.", addr)

    def show_help(self, addr):
        help_message = "Available commands: login, logout, create, list:myacmd, list:acmd, list:myrsv, book, cancel"
        self.send_message(help_message, addr)

    def get_username_by_address(self, addr):
        return next((username for username, address in self.clients.items() if address == addr), None)

    def receive_messages(self):
        while True:
            data, addr = self.receiver.socket.recvfrom(MAX_BUFF_SIZE)
            if addr not in self.stateR:
                self.stateR[addr] = "wait_seq_0"
                self.stateS[addr] = "wait_ack_0"
            Thread(target=self.handle_client, args=(data, addr)).start()

    def run(self):
        print('Server is running and listening...')
        self.receive_messages()

if __name__ == "__main__":
    server = Server()
    server.run()
