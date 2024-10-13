import asyncio
import time

# List to store latency for each client
latency_log = []

# Function to handle each client task
async def client_task(client_id):
    reader, writer = await asyncio.open_connection('127.0.0.1', 8080)
    
    try:
        message = f"Hello from client {client_id}"
        start_time = time.time()
        
        # Sending message to server
        writer.write(message.encode())
        await writer.drain()

        # Receiving server response
        data = await reader.read(100)
        end_time = time.time()
        latency = end_time - start_time
        
        # Store latency result in a shared list
        latency_log.append((client_id, latency))
        
        print(f"Client {client_id} - Server response: {data.decode()}")
        print(f"Client {client_id} - Latency: {latency:.6f} seconds")
    
    except Exception as e:
        print(f"Client {client_id} - Error: {e}")
    
    finally:
        writer.close()
        await writer.wait_closed()

# Function to run multiple clients concurrently
async def run_clients_concurrently(num_clients):
    tasks = []
    for i in range(num_clients):
        # Each client runs concurrently
        task = asyncio.create_task(client_task(i))
        tasks.append(task)
    
    # Wait for all clients to finish
    await asyncio.gather(*tasks)

    # After all clients have finished, write the latency logs in order
    latency_log.sort()  # Sort by client ID for sequential logging
    with open("client_latency_log.txt", "w") as log_file:
        for client_id, latency in latency_log:
            log_file.write(f"Client {client_id} - Latency: {latency:.6f} seconds\n")

if __name__ == "__main__":
    # Set the number of clients you want to run
    number_of_clients = 20  # Change this to the desired number of clients
    asyncio.run(run_clients_concurrently(number_of_clients))
