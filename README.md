# Communication Infrastructure Project

This project is part of the Communication Infrastructure course at CIn/UFPE. It is divided into three main phases, each building upon the previous one. The project explores various aspects of network communication, focusing on UDP and the RDT 3.0 protocol. 
![image](https://github.com/user-attachments/assets/ab9f0ccd-12b4-47d6-b0a8-27f32b472d35)

### Table of Contents
- [Phase 1: File Transmission with UDP](#phase-1-file-transmission-with-udp)
- [Phase 2: Reliable Data Transfer with RDT 3.0](#phase-2-reliable-data-transfer-with-rdt-30)
- [Phase 3: Accommodation Reservation System](#phase-3-accommodation-reservation-system)
- [Installation and Setup](#installation-and-setup)
- [Contributing](#contributing)

### Phase 1: File Transmission with UDP

- **Objective**: Implement file transmission using UDP in Python.
- **Details**: 
  - Use the Socket library to send and receive files of at least two different types (e.g., .txt and images).
  - Files are sent from the client, stored on the server, and returned to the client.
  - Implement packet fragmentation for files larger than 1024 bytes and ensure reassembly at the receiver.

### Phase 2: Reliable Data Transfer with RDT 3.0

- **Objective**: Implement a basic reliable data transfer protocol using RDT 3.0 over UDP.
- **Details**: 
  - Use the code from Phase 1 and enhance it to handle reliable transmission using RDT 3.0.
  - Simulate random packet loss and timeouts to demonstrate the protocol's reliability.
  - Display each step of the algorithm execution in the command line for better understanding.

### Phase 3: Accommodation Reservation System

- **Objective**: Develop a client-server system for managing accommodation bookings using the concepts from previous phases.
- **Details**: 
  - Implement a command-line interface for users to manage accommodations and bookings.
  - Ensure simultaneous operation for multiple clients without interrupting the service.
  - Incorporate the RDT 3.0 protocol for reliable communication.
  - Deliver a video demonstration explaining the code and showing the system in action.

### Installation and Setup

1. **Clone the repository**:
    ```bash
    git clone https://github.com/Shellyda/project-communication-infrastructure.git
    cd project-communication-infrastructure
    ```

2. **Install Python**:
    Ensure you have Python installed. You can download it from [python.org](https://www.python.org/).

3. **Instructions**:
    Each phase has its own folder with the necessary code and a detailed README with execution instructions and additional notes.

### Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a pull request.
