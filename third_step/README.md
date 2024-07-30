## Project Third Step: Accommodation Reservation System

In this last phase of the project, it's implemented an Accommodation Reservation System based in a reliable data transfer (RDT 3.0) system using UDP for network communication between a client and a server. 

### Structure

- `client.py`: A user interface for interacting with the server, sending commands, and receiving responses.
- `server.py`: Manages client connections, processes commands, and maintains data about accommodations and reservations.
- `rdt_sender.py`: Manages the finite state machine based on sending packets and waiting acknowledgements messages.
- `rdt_receiver.py`: Manages the finite state machine based on waiting packets and sending acknowledgements messages.
- `env_props.py`: File containing environment configurations.

### Usage Instructions

#### 1. Environment Configuration
   The `env_props.py` file contains the following configured variables:

   ```python
   SERVER_ADDRESS = ('localhost', 6060)  # Example server configuration
   MAX_BUFF_SIZE = 1024  # Buffer size in bytes
   ```
#### 2. Run the Server
   In a terminal, navigate to the project second step folder directory and run the server script:

   ```python
   python3 server.py
   ```

   ```python
   python server.py
   ```
   ##### Use "python server.py" only if the computer contains different versions of python

   You will see the following message indicating the server is running:
   ```python
   Accommodation server started. Waiting for connections...
   ```

#### 3. Run the Client
  Open another terminal, navigate to the project first step folder directory, and run the client script:

   ```python
   python3 client.py
   ```

   ```python
   python client.py
   ```
   ##### Use "python client.py" only if the computer contains different versions of python

   You will see the following message indicating the client is running:
   ```python
    Enter your username to login: # Your name goes here
   ```