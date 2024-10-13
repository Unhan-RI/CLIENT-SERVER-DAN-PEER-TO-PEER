import socket
import threading
import time
import random

class Node:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((self.host, self.port))
        self.nodes = []  # List of known nodes
        self.files = {}  # Dictionary of files available in this node

    def start_server(self):
        print(f"Node {self.host}:{self.port} is listening for connections...")
        threading.Thread(target=self.listen).start()

    def listen(self):
        while True:
            data, addr = self.server_socket.recvfrom(1024)
            message = data.decode()
            self.handle_message(message, addr)

    def handle_message(self, message, addr):
        print(f"Received message from {addr}: {message}")
        if message.startswith("SEARCH"):
            self.search_file(message.split()[1], addr)
        elif message.startswith("FILE_REQUEST"):
            self.send_file(message.split()[1], addr)

    def add_node(self, node):
        if node not in self.nodes:
            self.nodes.append(node)

    def search_file(self, filename, addr, use_random_walk=False):
        # Flooding algorithm
        if not use_random_walk:
            print(f"Flooding: Searching for {filename}...")
            start_time = time.time()
            for node in self.nodes:
                self.server_socket.sendto(f"SEARCH {filename}".encode(), node)

            # Wait for a brief period to receive responses
            time.sleep(1)
            end_time = time.time()
            self.log_performance(start_time, end_time, len(filename))
        else:
            print(f"Random Walk: Searching for {filename}...")
            start_time = time.time()
            self.random_walk_search(filename)

            # Wait for a brief period to receive responses
            time.sleep(1)
            end_time = time.time()
            self.log_performance(start_time, end_time, len(filename))

    def random_walk_search(self, filename):
        if self.nodes:
            random_node = random.choice(self.nodes)
            self.server_socket.sendto(f"SEARCH {filename}".encode(), random_node)

    def send_file(self, filename, addr):
        if filename in self.files:
            file_data = self.files[filename]
            self.server_socket.sendto(file_data.encode(), addr)
            print(f"Sent file {filename} to {addr}")

    def add_file(self, filename, data):
        self.files[filename] = data
        print(f"File {filename} added to node {self.host}:{self.port}")

    def request_file(self, filename, node):
        self.server_socket.sendto(f"FILE_REQUEST {filename}".encode(), node)

    def log_performance(self, start_time, end_time, file_size):
        response_time = end_time - start_time
        # Prevent division by zero
        if response_time > 0:
            throughput = file_size / response_time  # bytes per second
            print(f"Response time: {response_time:.2f}s, Throughput: {throughput:.2f} B/s")
        else:
            print("Response time was too short to measure.")

if __name__ == "__main__":
    nodes = []

    # Allow user to specify number of nodes
    num_nodes = int(input("Enter the number of nodes (5, 10, or 20): "))
    if num_nodes not in [5, 10, 20]:
        print("Invalid number of nodes. Please enter 5, 10, or 20.")
        exit(1)

    # Create nodes
    for i in range(num_nodes):
        node = Node(f"localhost", 10000 + i)
        node.start_server()
        nodes.append(node)

    # Example of adding files and searching
    for node in nodes:
        node.add_file("example.txt", "This is a sample file content.")
        time.sleep(1)  # To avoid collisions

    # Choose the search method
    search_method = input("Choose search method (flooding/random walk): ").strip().lower()
    
    if search_method not in ["flooding", "random walk"]:
        print("Invalid search method. Please enter 'flooding' or 'random walk'.")
        exit(1)

    # Start searching for a file
    for node in nodes:
        node.search_file("example.txt", ("localhost", 10000), use_random_walk=(search_method == "random walk"))
