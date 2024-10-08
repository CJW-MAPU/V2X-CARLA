import json
import socket
import threading
import time


class GPSCentre:
    def __init__(self, host = 'localhost', port = 55555):
        self.__server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server_socket.bind((host, port))
        self.__server_socket.listen(100)
        self.__clients = list()
        self.__state = {}
        self.lock = threading.Lock()

    def handle_client(self, client_socket):
        while True:
            try:
                message = client_socket.recv(1024).decode('utf-8')
                if not message:
                    break
                data = json.loads(message)
                for key, value in data.items():
                    with self.lock:
                        self.__state[key] = value
            except ConnectionResetError:
                break
            except json.JSONDecodeError:
                print("Received invalid JSON, GPS")
        self.__clients.remove(client_socket)
        client_socket.close()

    def broadcast(self):
        while True:
            # print('[ GPSCentre.broadcast ]')
            # print(f'Send to client: {self.__state}')
            with self.lock:
                state_copy = self.__state.copy()
            for client in self.__clients:
                try:
                    client.send(json.dumps(state_copy).encode('utf-8'))
                except Exception as e:
                    print(f'Error broadcasting to client: {e}')
                    self.__clients.remove(client)
            time.sleep(0.001)

    def run(self):
        # print(f'Server started and waiting for connections...')
        broadcast_thread = threading.Thread(target = self.broadcast)
        broadcast_thread.daemon = True
        broadcast_thread.start()

        while True:
            client_socket, addr = self.__server_socket.accept()
            self.__clients.append(client_socket)
            # print(f"Connection from {addr}")
            client_handler = threading.Thread(target = self.handle_client, args = (client_socket, ))
            # client_handler.daemon = True
            client_handler.start()
