import socket as skt
from threading import Thread
import env_props as env

MAX_BUFF_SIZE = env.MAX_BUFF_SIZE

class Server:
    def __init__(self, host, port):
        self.server_socket = skt.socket(skt.AF_INET, skt.SOCK_DGRAM)
        self.server_socket.bind((host, port))
        self.clients = {}  # {username: (address, port)}
        self.accommodations = {}  # {(name, location): {'id': id, 'owner': (username, addr), 'description': description, 'available_days': [days], 'reservations': {day: (username, addr)}}}
        self.reservations = {}  # {(owner, id, day): (guest_name, guest_addr)}
        self.available_days = ["17/07/2024", "18/07/2024", "19/07/2024", "20/07/2024", "21/07/2024", "22/07/2024"]

    def handle_client(self, data, addr):
        command = data.decode().split()
        action = command[0]

        if action == "login":
            self.login(command[1], addr)
        elif action == "logout":
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

    def login(self, username, addr):
        if username in self.clients:
            self.server_socket.sendto("Username already in use.".encode(), addr)
        else:
            self.clients[username] = addr
            self.server_socket.sendto(f"Login successful {username}".encode(), addr)
            print(f'User [{username}/{addr[0]}:{addr[1]}] is connected!')
    
    def logout(self, addr):
        username = self.get_username_by_address(addr)
        if username in self.clients:
            del self.clients[username]
            print(f'User [{username}/{addr[0]}:{addr[1]}] disconnected!')

    
    def create_accommodation(self, name, location, addr):
        if (name, location) in self.accommodations:
            self.server_socket.sendto("Accommodation already exists.".encode(), addr)
        else:
            accommodation_id = len(self.accommodations) + 1
            self.accommodations[(name, location)] = {
                'id': accommodation_id,
                'owner': addr,
                'available_days': self.available_days.copy(),
                'reservations': {}
            }
            owner_name = self.get_username_by_address(addr)
            self.server_socket.sendto(f"Accommodation {name} created successfully!".encode(), addr)
            self.notify_all_clients(f"[{owner_name}/{addr[0]}:{addr[1]}] New accommodation {name} in {location} created!", exclude=addr)
    
    def list_my_accommodations(self, addr):
        my_acmds = []
        for (name, location), details in self.accommodations.items():
            if details['owner'] == addr:
                res = details['reservations']
                acmd_info = f"ID {details['id']}: {name} in {location} \n- Available: {details['available_days']}\n - Reserved: {[(d, self.get_username_by_address(u)) for d, u in res.items()]}"
                my_acmds.append(acmd_info)
        response = "\n".join(my_acmds) if my_acmds else "You have no accommodations."
        self.server_socket.sendto(response.encode(), addr)
    
    def list_accommodations(self, addr):
        acmds = []
        for (name, location), details in self.accommodations.items():
            owner_name = self.get_username_by_address(details['owner'])
            acmd_info = f"ID {details['id']}: {name} in {location} - Available: {details['available_days']} - Owner: {owner_name}"
            acmds.append(acmd_info)
        response = "\n".join(acmds) if acmds else "No accommodations available."
        self.server_socket.sendto(response.encode(), addr)
    
    def list_my_reservations(self, addr):
        my_rsvs = []
        for (owner, id, day), (guest_name, guest_addr) in self.reservations.items():
            if guest_addr == addr:
                owner_name = self.get_username_by_address(owner)
                my_rsvs.append(f"[{owner_name}/{owner[0]}:{owner[1]}] Reservation: Accommodation ID {id} on {day}")
        response = "\n".join(my_rsvs) if my_rsvs else "You have no reservations."
        self.server_socket.sendto(response.encode(), addr)
    
    def book_accommodation(self, owner_name, acmd_id, day, addr):
        owner_addr = self.get_addr_by_username(owner_name)
        if owner_addr and (owner_addr, acmd_id, day) in self.reservations:
            self.server_socket.sendto("Accommodation already booked for this day.".encode(), addr)
        else:
            if (owner_addr, acmd_id, day) not in self.reservations:
                for (name, location), details in self.accommodations.items():
                    if details['id'] == int(acmd_id) and day in details['available_days']:
                        details['available_days'].remove(day)
                        details['reservations'][day] = addr
                        self.reservations[(owner_addr, acmd_id, day)] = (self.get_username_by_address(addr), addr)
                        self.server_socket.sendto(f"Booking successful for {name} on {day}.".encode(), addr)
                        self.notify_owner(owner_addr, f"[{self.get_username_by_address(addr)}/{addr[0]}:{addr[1]}] Reservation for {name} on {day}", subject="reservation")
                        return
            self.server_socket.sendto("Accommodation or day unavailable.".encode(), addr)
    
    def cancel_reservation(self, owner_name, acmd_id, day, addr):
        owner_addr = self.get_addr_by_username(owner_name)
        if owner_addr and (owner_addr, acmd_id, day) in self.reservations and self.reservations[(owner_addr, acmd_id, day)][1] == addr:
            del self.reservations[(owner_addr, acmd_id, day)]
            for (name, location), details in self.accommodations.items():
                if details['id'] == int(acmd_id):
                    details['available_days'].append(day)
                    del details['reservations'][day]
                    self.server_socket.sendto("Reservation cancelled successfully.".encode(), addr)
                    self.notify_owner(owner_addr, f"[{self.get_username_by_address(addr)}/{addr[0]}:{addr[1]}] Cancellation for {name} on {day}", subject="cancellation")
                    self.notify_all_clients(f"[{self.get_username_by_address(owner_addr)}/{owner_addr[0]}:{owner_addr[1]}] New availability for {name} in {location} on {day}", exclude=owner_addr)
                    return
        self.server_socket.sendto("Reservation not found.".encode(), addr)
    
    def notify_all_clients(self, message, exclude=None):
        for client_addr in self.clients.values():
            if client_addr != exclude:
                self.server_socket.sendto(message.encode(), client_addr)
    
    def notify_owner(self, owner_addr, message, subject):
        if owner_addr:
            self.server_socket.sendto(message.encode(), owner_addr)
    
    def show_help(self, addr):
        help_message = """
Available commands:
- login <username>: Log in with a username
- logout: Log out
- create <name> <location>: Create a new accommodation
- list:myacmd: List your accommodations
- list:acmd: List all available accommodations
- list:myrsv: List your reservations
- book <owner> <id> <day>: Book an accommodation
- cancel <owner> <id> <day>: Cancel a reservation
- --help: Display this help message
"""
        self.server_socket.sendto(help_message.encode(), addr)
    
    def get_username_by_address(self, addr):
        for username, client_addr in self.clients.items():
            if client_addr == addr:
                return username
        return None

    def get_addr_by_username(self, username):
        return self.clients.get(username, None)

    def run(self):
        print("Accommodation server started. Waiting for connections...")
        while True:
            data, addr = self.server_socket.recvfrom(MAX_BUFF_SIZE)
            Thread(target=self.handle_client, args=(data, addr)).start()

if __name__ == "__main__":
    server = Server(env.SERVER_HOST, env.SERVER_PORT)
    server.run()
