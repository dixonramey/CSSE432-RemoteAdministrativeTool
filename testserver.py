import socket

HOST = ''  # empty string means listen on all available interfaces
PORT = 8888

# Create a socket object
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    # Bind the socket to a specific interface and port
    s.bind((HOST, PORT))
    # Listen for incoming connections
    s.listen()
    print(f"Listening on port {PORT}...")
    # Accept incoming connections and handle them one at a time
    while True:
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            # Receive data from the client and send it back
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                conn.sendall(data.decode().upper().encode())
