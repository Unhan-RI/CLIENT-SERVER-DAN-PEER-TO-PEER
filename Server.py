import asyncio
import logging
import time

# Setup logging
logging.basicConfig(filename='async_server_log.txt', level=logging.INFO, 
                    format='%(asctime)s - %(message)s')

total_requests = 0  # Variable to count total number of requests processed
start_time = time.time()  # Record the start time for throughput calculation

# Asynchronous function to handle each client connection
async def handle_client(reader, writer):
    global total_requests
    
    address = writer.get_extra_info('peername')
    
    # Log the time the client connects
    logging.info(f"Client connected from {address}")
    
    while True:
        data = await reader.read(100)  # Reading 100 bytes from the client
        if not data:
            break
        message = data.decode()
        
        # Log the message received and timestamp
        logging.info(f"Received message from {address}: {message}")
        
        # Measure response time
        request_received_time = time.time()
        
        # Sending response back to the client
        response = f"Message received: {message}"
        writer.write(response.encode())
        await writer.drain()

        # Log when the message is sent
        response_sent_time = time.time()
        response_time = response_sent_time - request_received_time
        
        logging.info(f"Sent response to {address}: {response}, Response Time: {response_time:.6f} seconds")
        
        total_requests += 1  # Count each request
    
    # Log the client disconnection
    logging.info(f"Client from {address} disconnected.")
    writer.close()
    await writer.wait_closed()

# Function to start the server asynchronously
async def start_server():
    server = await asyncio.start_server(handle_client, '127.0.0.1', 8080)
    addr = server.sockets[0].getsockname()
    print(f'Server started at {addr}')
    
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt:
        end_time = time.time()
        total_time = end_time - start_time
        # Calculate throughput as total requests processed divided by total time
        throughput = total_requests / total_time if total_time > 0 else 0
        print(f"Total Requests: {total_requests}")
        print(f"Total Time: {total_time:.2f} seconds")
        print(f"Throughput: {throughput:.2f} requests per second")
