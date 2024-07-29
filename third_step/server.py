import socket as skt
from threading import Thread
import env_props as env
import struct

MAX_BUFF_SIZE = env.MAX_BUFF_SIZE

class Server:
    def __init__(self, host, port):
        self.server_socket = skt.socket(skt.AF_INET, skt.SOCK_DGRAM)
        self.server_socket.bind((host, port))
        self.clients = {}  # {username: (address, port)}
        self.accommodations = {}  # {(name, location): {'id': id, 'owner': (username, addr), 'description': description, 'available_days': [days], 'reservations': {day: (username, addr)}}}
        self.reservations = {}  # {(owner, id, day): (guest_name, guest_addr)}
        self.available_days = ["17/07/2024", "18/07/2024", "19/07/2024", "20/07/2024", "21/07/2024", "22/07/2024"]
        self.stateS={} #{(address, port): (stateS)}
        self.stateR={} #{(address, port): (stateR)}

    def send_acknowledgement(self, ack, addr):
        print('\x1b[1;34;40m' + f'ACK {ack} sent' + '\x1b[0m')
        data = struct.pack('i', ack)
        self.server_socket.sendto(data, addr) # Sends the data to the destination 
        if ack == 0:
            self.stateR[addr] = "wait_seq_1"# Change state to wait_seq_1
        elif ack == 1:
            self.stateR[addr] = "wait_seq_0"# Change state to wait_seq_1
            
    def machine_is_logged(self, addr):
        return addr in self.clients.values() 
    
    def send_message(self, message, addr):
        sequence_number = int(self.stateS[addr][-1]) 
        packet_length = len(message)
        data = bytearray(4 + packet_length)
        data = struct.pack(f'i {packet_length}s', sequence_number, message)
        self.server_socket.sendto(data, addr)
        print('\x1b[1;34;40m' + f'packet {sequence_number} sent' + '\x1b[0m')
        self.stateS[addr] = f"wait_ack_{sequence_number}"
        print(self.stateS)

    def handle_client(self, data, addr):
        length = len(data) - 4
        data1 = struct.unpack_from(f'i {length}s', data)
        sequence_number = data1[0]
        payload = data1[1:]

        #print(sequence_number,payload)

        command = data.decode().split()
        action = command[0].lstrip('\x00') 

        # print(repr(command[1]))
        # print(action=="login")
        # print(type(action))

        print('\x1b[1;34;40m' + f'packet {sequence_number} received' + '\x1b[0m')

        self.send_acknowledgement(sequence_number,addr)

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
            self.send_message("Username already in use.".encode(), addr)
        else:
            self.clients[username] = addr
            self.send_message(f"Login successful {username}".encode(), addr)
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
            self.stateS[addr]="wait_call_0"
            self.stateR[addr]="wait_seq_0"

if __name__ == "__main__":
    server = Server(env.SERVER_HOST, env.SERVER_PORT)
    server.run()
