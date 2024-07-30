import socket as skt
from threading import Thread, Event
import env_props as env
from rdt_receiver import RDT_Receiver

# Constants from the environment configuration
MAX_BUFF_SIZE = env.MAX_BUFF_SIZE
target_address = env.SERVER_ADDRESS

class Client:
    def __init__(self, socket_family=skt.AF_INET, socket_type=skt.SOCK_DGRAM):
        # Initialize the client socket with the specified socket family and type
        self.client_socket = skt.socket(socket_family, socket_type)
        self.server_address = target_address
        self.username = None
        self.has_current_response = False
        self.login_event = Event()  # Event to manage login synchronization
        self.receiver = RDT_Receiver()  # Reliable Data Transfer receiver instance

    def send_message(self, message):
        # Send a message using the reliable data transfer protocol
        self.receiver.send(message, self.server_address)

    def receive_message(self):
        while True:
            # Continuously receive messages from the server
            message = self.receiver.receive()  
            self.has_current_response = True
            print('\n\x1b[1;37;96m' + message + '\x1b[37m')  # Display the received message
            if message.startswith('Login successful'):
                self.username = message.split()[-1]  # Extract username from the success message
                self.login_event.set()  # Signal that login is successful
            elif message.startswith('Username already in use'):
                self.login_event.set()
                self.username = None

    def login(self, username):
        # Send a login request with the specified username
        self.send_message(f'login {username}')

    def logout(self):
        # Send a logout request and reset the username
        self.send_message(f'logout {self.username}')
        self.username = None

    def create_accommodation(self, name, location):
        # Send a request to create an accommodation with the specified name and location
        self.send_message(f'create {name} {location}')

    def list_my_accommodations(self):
        # Send a request to list accommodations created by the user
        self.send_message(f'list:myacmd')

    def list_accommodations(self):
        # Send a request to list all available accommodations
        self.send_message('list:acmd')

    def list_my_reservations(self):
        # Send a request to list reservations made by the user
        self.send_message(f'list:myrsv')

    def book_accommodation(self, owner, acmd_id, day):
        # Send a request to book an accommodation with the specified owner, ID, and day
        self.send_message(f'book {owner} {acmd_id} {day}')

    def cancel_reservation(self, owner, acmd_id, day):
        # Send a request to cancel a reservation with the specified owner, ID, and day
        self.send_message(f'cancel {owner} {acmd_id} {day}')

    def show_help(self):
        # Send a request to show help information
        self.send_message('--help')
        
    def handle_command(self, command):
        self.has_current_response = False
        print('\x1b[1;37;95m' +'\nLoading your request...' + '\x1b[37m\n')

        if command.startswith('login'):
            print('\x1b[1;37;93m' + '\nYou are already logged in.' + '\x1b[37m')
            self.has_current_response = True
        elif command.startswith('logout'):
            self.logout()
        elif command.startswith('create'):
            _, name, location = command.split(maxsplit=3)
            self.create_accommodation(name, location)
        elif command.startswith('list:myacmd'):
            self.list_my_accommodations()
        elif command.startswith('list:acmd'):
            self.list_accommodations()
        elif command.startswith('list:myrsv'):
            self.list_my_reservations()
        elif command.startswith('book'):
            _, owner, acmd_id, day = command.split()
            self.book_accommodation(owner, acmd_id, day)
        elif command.startswith('cancel'):
            _, owner, acmd_id, day = command.split()
            self.cancel_reservation(owner, acmd_id, day)
        elif command.startswith('--help'):
            self.show_help()
        else:
            print('\x1b[1;31;40m' + '\nCommand not valid! Use --help to see available commands.\n' + '\x1b[37m')
            self.has_current_response = True

    def run(self):
        # Start the thread for receiving messages from the server
        Thread(target=self.receive_message).start()
        while True:
            if self.username is None:
                # Prompt for username if not logged in
                command = input('\x1b[1;37;40m' + 'Enter your username to login: ' + '\x1b[37m')
                print('\x1b[1;37;95m' +'\nLoading your request...' + '\x1b[37m')
                self.login_event.clear()  
                self.login(command)
                self.login_event.wait() 
            else:
                if self.has_current_response:
                    # Prompt for command if there is a current response
                    print('\nUse --help to see available commands')
                    command = input(f'{self.username}@client:~$ ')
                    self.handle_command(command)
                else:
                    pass

if __name__ == '__main__':
    # Create a client instance and run it
    client = Client()
    client.run()
