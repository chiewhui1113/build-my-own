# Socket is one endpoint of the internet connection 
import socket

# '' means listen on every network interface
HOST, PORT = '', 8888

# AF_INET = IPv4; SOCK_STREAM = TCP
listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# SO_REUSEADDR means ok to reuse address immediately (x affected by TIME_WAIT)
listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# Attach socket to an address 
listen_socket.bind((HOST, PORT))
# Allow 1 pending connection to wait in the queue 
listen_socket.listen(1)
print(f'Serving HTTP on port {PORT} ...')
while True:
    # Blocks until someone connects 
    client_connection, client_address = listen_socket.accept()
    # Read up to 1024 bytes 
    request_data = client_connection.recv(1024)
    print(request_data.decode('utf-8'))

    http_response = b"""\
    HTTP/1.1 200 OK

    Hello, World!
    """
    # Send until all bytes have been transmitted 
    client_connection.sendall(http_response)
    client_connection.close()