import socket as skt
import struct
from threading import Thread
import env_props as env # Environment props

MAX_BUFF_SIZE = env.MAX_BUFF_SIZE

class Server:
    def __init__(self, host, port):
        # Create a UDP socket and bind it to the specified address
        self.server_socket = skt.socket(skt.AF_INET, skt.SOCK_DGRAM)
        self.server_socket.bind((host, port))
        self.clients = {}  # Dictionary to store connected clients
        self.accommodations = {}  # Dictionary to store accommodations
        self.reservations = {}  # Dictionary to store reservations

    def handle_client(self, data, addr):
        # Process the received message from the client
        command = data.decode().split()
        action = command[0]

        # Perform the action corresponding to the received command
        if action == "login":
            self.login(command[1], addr)
        elif action == "logout":
            self.logout(command[1], addr)
        elif action == "create":
            self.create_accommodation(command[1], command[2], command[3], addr)
        elif action == "list:myacmd":
            self.list_my_accommodations(command[1], addr)
        elif action == "list:acmd":
            self.list_accommodations(addr)
        elif action == "list:myrsv":
            self.list_my_reservations(command[1], addr)
        elif action == "book":
            self.book_accommodation(command[1], command[2], command[3], command[4], command[5], addr)
        elif action == "cancel":
            self.cancel_reservation(command[1], command[2], command[3], command[4], addr)
        elif action == "--help":
            self.show_help(addr)

    def login(self, username, addr):
        # Add the client to the connected clients list
        if username in self.clients:
            self.server_socket.sendto("Username already in use.".encode(), addr)
        else:
            self.clients[username] = addr
            self.server_socket.sendto("You are online!".encode(), addr)
    
    def logout(self, username, addr):
        # Remove the client from the connected clients list
        if username in self.clients:
            del self.clients[username]
            self.server_socket.sendto("You are offline!".encode(), addr)
        else:
            self.server_socket.sendto("You need to be logged!".encode(), addr)
    
    def create_accommodation(self, name, location, description, addr):
        # Create a new accommodation
        if (name, location) in self.accommodations:
            self.server_socket.sendto("Accommodation already exists.".encode(), addr)
        else:
            self.accommodations[(name, location)] = {
                'description': description,
                'owner': addr,
                'reservations': {}
            }
            self.notify_all_clients(f"Accommodation {name} in {location} created successfully!")
    
    def list_my_accommodations(self, username, addr):
        # List accommodations owned by the client
        my_acmds = [f"{name} in {location}: {details['description']}" 
                    for (name, location), details in self.accommodations.items() 
                    if details['owner'] == addr]
        response = "\n".join(my_acmds) if my_acmds else "You have no accommodations."
        self.server_socket.sendto(response.encode(), addr)
    
    def list_accommodations(self, addr):
        # List all available accommodations
        acmds = [f"{name} in {location}: {details['description']}" 
                 for (name, location), details in self.accommodations.items()]
        response = "\n".join(acmds) if acmds else "No accommodations available."
        self.server_socket.sendto(response.encode(), addr)
    
    def list_my_reservations(self, username, addr):
        # List reservations made by the client
        my_rsvs = [f"{owner} {name} in {location} on {day}: Room {room}" 
                   for (owner, name, location, day), room in self.reservations.items() 
                   if room['guest'] == addr]
        response = "\n".join(my_rsvs) if my_rsvs else "You have no reservations."
        self.server_socket.sendto(response.encode(), addr)
    
    def book_accommodation(self, owner, name, location, day, room, addr):
        # Book an accommodation for the client
        key = (owner, name, location, day)
        if key in self.reservations:
            self.server_socket.sendto("Accommodation already booked for this day.".encode(), addr)
        else:
            self.reservations[key] = {'room': room, 'guest': addr}
            self.server_socket.sendto("Booking successful.".encode(), addr)
            self.notify_owner(owner, f"Booking made by {addr} for {name} in {location} on {day}")
    
    def cancel_reservation(self, owner, name, location, day, addr):
        # Cancel a reservation for the client
        key = (owner, name, location, day)
        if key in self.reservations and self.reservations[key]['guest'] == addr:
            del self.reservations[key]
            self.server_socket.sendto("Reservation cancelled successfully.".encode(), addr)
            self.notify_owner(owner, f"Reservation cancelled by {addr} for {name} in {location} on {day}")
        else:
            self.server_socket.sendto("Reservation not found.".encode(), addr)
    
    def notify_all_clients(self, message):
        # Notify all connected clients
        for client_addr in self.clients.values():
            self.server_socket.sendto(message.encode(), client_addr)
    
    def notify_owner(self, owner, message):
        # Notify the owner of an accommodation
        owner_addr = self.clients.get(owner)
        if owner_addr:
            self.server_socket.sendto(message.encode(), owner_addr)

    def show_help(self, addr):
        # Display a list of available commands
        help_message = """
Available commands:
- login <username>: Log in with a username
- logout <username>: Log out
- create <name> <location> <description>: Create a new accommodation
- list:myacmd <username>: List your accommodations
- list:acmd: List all available accommodations
- list:myrsv <username>: List your reservations
- book <owner> <name> <location> <day> <room>: Book an accommodation
- cancel <owner> <name> <location> <day>: Cancel a reservation
- --help: Display this help message
"""
        self.server_socket.sendto(help_message.encode(), addr)


    def run(self):
        # Start the server and wait for connections
        print("Accommodation server started. Waiting for connections...")
        while True:
            data, addr = self.server_socket.recvfrom(MAX_BUFF_SIZE)
            Thread(target=self.handle_client, args=(data, addr)).start()

if __name__ == "__main__":
    server = Server(env.SERVER_HOST, env.SERVER_PORT)
    server.run()
