## Project Second Step: Implementing Reliable Transfer with RDT 3.0

In this second phase of the project, the task is to implement a reliable data transfer protocol using UDP and the RDT 3.0 method. This phase builds upon the first phase, where basic UDP communication for file sending and receiving was established.

### Structure

- `client.py`: UDP client script.
- `server.py`: UDP server script.
- `env_props.py`: File containing environment configurations.

### Usage Instructions

#### 1. Environment Configuration
   The `env_props.py` file contains the following configured variables:

   ```python
   CLIENT_HOST = ('localhost', 8080)  # Example client configuration
   SERVER_HOST = ('localhost', 6060)  # Example server configuration
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

   The server will prompt for the name of the file to send to the client. Input the file name (e.g., `image.png` or `text.txt`) and press Enter:
   ```python
   💬 Enter the file name to send to client, you can choose 'image.png' or 'text.txt': image.png # Here goes your input
   ```
   ##### obs.: The image is large so its transmission takes longer than the text transmission


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
   🚀 Client is running on 127.0.0.1 with PORT 8080!   
   ```

#### 4. File Transfer
   The server will send the specified file to the client and wait to receive the Acknowledgment packet back. Informative messages will be displayed in both the client and server terminals indicating the progress of the transfer.

#### 5. Terminate the Connection
   After the transfer is complete, the client and server will display messages indicating the termination of operations and will close the sockets.
   ```python
   # In Client terminal 
   🛑 Stopping client socket!

   # In Server terminal
   🛑 Stopping server socket!
   ```

### Conclusion
   In the project second step folder directory, after carrying out the above process, there will be new `.png` or `.txt` files, *depending* on what you chose in *step 2*, renamed to confirm that the file transfer took place.

### Classmates Team 01
- João Victor - jvnms@cin.ufpe.br
- Edenn Weslley - ewss@cin.ufpe.br
- Paulo Nascimento - pmn@cin.ufpe.br
- Lucas Torres - ljat@cin.ufpe.br
- Shellyda Barbosa - sfsb2@cin.ufpe.br
    
    



