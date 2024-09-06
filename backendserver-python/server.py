import socket
import threading

def handle_client(client_socket):
    with client_socket:
        print("Client connected.")
        data = client_socket.recv(1024)

        if not data:
            return
        
        data = data.decode('utf-8')
        print(data)
        print(f"query value: {data}")

        client_socket.sendall(data.encode())
        print("Client disconnected.")

def start_server(host='localhost', port=8000):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen()
    print(f"Server listening on {host}:{port}")

    while True:
        client_socket, addr = server_socket.accept()
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

if __name__ == "__main__":
    start_server()
