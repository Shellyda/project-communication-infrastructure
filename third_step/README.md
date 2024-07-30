## Accommodation Reservation System 

### Overview
This project involves implementing an accommodation reservation system using a client-server architecture. The system supports user login, accommodation creation, listing accommodations, booking, and canceling reservations. The communication between the client and server is handled using a reliable data transfer protocol (RDT 3.0).

## Table of Contents

- [Structure](#structure)
- [Running the System](#running-the-system)
- [Example Interaction](#example-interaction)

## Structure
- `Client`: Handles user input and communication with the server.
- `Server`: Manages accommodations, reservations, and user sessions.
- `RDT_Receiver`: Ensures reliable data reception.
- `RDT_Sender`: Ensures reliable data transmission.

### 1. Environment Properties
The `env_props.py` file contains the following configured variables:

 ```python
   SERVER_ADDRESS = ('localhost', 6060)  # Example server configuration
   MAX_BUFF_SIZE = 1024  # Buffer size in bytes
 ```

### 2. Client
The client manages user interactions and communicates with the server to perform various operations.

#### Features
- **Login/Logout:** User authentication.
- **Create Accommodation:** Allows users to create new accommodations.
- **List Accommodations:** Lists all or user's accommodations.
- **Book Accommodation:** Users can book available accommodations.
- **Cancel Reservation:** Users can cancel their reservations.
- **Help:** Displays available commands.

#### Usage
1. **Login:** Enter your username to log in.
3. **Commands:**
- `create <name> <location>`: Create a new accommodation.
- `list:myacmd`: List your accommodations.
- `list:acmd`: List all accommodations.
- `book <owner> <id> <day>`: Book an accommodation.
- `cancel <owner> <id> <day>`: Cancel a reservation.
- `logout`: Log out of the system.
- `--help`: Display help message.

### 3. Server
The server handles client requests, manages accommodations, and reservations.

#### Features
- **User Management:** Handles login and logout.
- **Accommodation Management:** Create, list, and manage accommodations.
- **Reservation Management:** Book and cancel reservations.

#### Usage
The server runs continuously, awaiting client requests.

### 4. Reliable Data Transfer (RDT) Protocol
The RDT protocol ensures reliable communication between the client and server, handling potential data loss and ensuring message integrity.

#### RDT_Receiver
- **Receive Messages:** Handles incoming messages and sends acknowledgments.
- **States:** Manages the state transitions for expected sequence numbers.

#### RDT_Sender
- **Send Messages:** Handles outgoing messages with sequence numbers and retransmissions.
- **Timeouts:** Implements timeout handling for reliable communication.

## Running the System

#### 1. Run the Server
   In a terminal, navigate to the project third step folder directory and run the server script:

   ```python
   python3 server.py
   ```

   ```python
   python server.py
   ```
   ##### Use "python server.py" only if the computer contains different versions of python

#### 2. Run the Client
  Open another terminal, navigate to the project third step folder directory, and run the client script:

   ```python
   python3 client.py
   ```

   ```python
   python client.py
   ```
   ##### Use "python client.py" only if the computer contains different versions of python

## Example Interaction
#### 1. Login:
```python
Enter your username to login: finn_the_human
```
- Output: `Login successful finn_the_human`
- Output at Server terminal: `User [finn_the_human/127.0.0.1:61374] is connected!`

#### 2. Create Accommodation:

```python
finn_the_human@client:~$ create BeachHouse Hawaii
```
- Output: `Accommodation BeachHouse created successfully!`
- Output for all users connected: `[finn_the_human/127.0.0.1:61374] New accommodation BeachHouse in Hawaii created!`

#### 3. List Accommodations:
```python
finn_the_human@client:~$ list:acmd
```
- Output: `ID 1: BeachHouse in Hawaii - Available: ["17/07/2024", ...,"22/07/2024"] - Owner: finn_the_human`

#### 4. Book Accommodation:
##### In other terminal run the Client and follow below instructions:
```python
Enter your username to login: jake_the_dog
jake_the_dog@client:~$ book finn_the_human 1 17/07/2024
```
- Output at Server terminal: `User [jake_the_dog/127.0.0.1:52278] is connected!`
- Output for user jake_the_dog: `Booking successful for BeachHouse on 17/07/2024.`
- Output for user finn_the_human: `[jake_the_dog/127.0.0.1:52278] Reservation for BeachHouse on 17/07/2024`

#### 5. Cancel Reservation:
```python
jake_the_dog@client:~$ cancel finn_the_human 1 17/07/2024
```
- Output for user jake_the_dog: `Reservation cancelled successfully.`
- Output for user finn_the_human: `[jake_the_dog/127.0.0.1:52278] Cancellation for BeachHouse on 17/07/2024`
- Output for all other users connected: `[finn_the_human/127.0.0.1:61374] New availability for BeachHouse in Hawaii on 17/07/2024`

#### 6. Logout 
```python
jake_the_dog@client:~$ logout
```
- Output at Server terminal: `User [jake_the_dog/127.0.0.1:52278] disconnected!`

## Contributors
- Lucas Torres - ljat@cin.ufpe.br
- Shellyda Barbosa - sfsb2@cin.ufpe.br
