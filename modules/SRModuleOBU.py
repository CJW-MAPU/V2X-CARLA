import json
import socket
import threading
import time


class SRModuleOBU:
    def __init__(self, obu_id, vehicle_port, host = 'localhost'):
        self.__gps_socket = None
        self.__vehicle_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__vehicle_socket.bind((host, vehicle_port))
        self.__vehicle_socket.listen(30)
        self.__obu_id = obu_id
        self.__states = {}
        self.__state = {}
        self.traffic_light_state = {}
        self.lock = threading.Lock()

    def init(self, gps_port, host = 'localhost'):
        self.__gps_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__gps_socket.connect((host, gps_port))

    def heartbeat_gps(self):
        while True:
            try:
                loc_data = self.__state.copy()
                message = json.dumps(loc_data)
                self.__gps_socket.send(message.encode('utf-8'))
                time.sleep(0.001)
            except ConnectionResetError:
                print('Connection lost')
            except KeyboardInterrupt:
                self.__gps_socket.close()

    def get_gps_all_objects(self):
        while True:
            try:
                response = self.__gps_socket.recv(1024).decode('utf-8')
                if not response:
                    break
                self.__states = json.loads(response)
            except ConnectionResetError:
                print('Connection lost')
            except json.JSONDecodeError:
                print("Received invalid JSON, OBU")
            except KeyboardInterrupt:
                self.__gps_socket.close()

    def get_traffic_light_state(self):
        client_socket = None
        while True:
            try:
                if client_socket is None:
                    client_socket, client_addr = self.__vehicle_socket.accept()
                    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

                response = client_socket.recv(1024).decode('utf-8')
                if not response:
                    client_socket.close()
                    client_socket = None
                    continue
                message = json.loads(response)
                print(f'OBU Response: {message}')
                self.traffic_light_state = message
            except ConnectionResetError:
                print('Connection lost')
                if client_socket:
                    client_socket = None
            except json.JSONDecodeError:
                print("Received invalid JSON, OBU")
            except KeyboardInterrupt:
                if client_socket:
                    client_socket.close()
                self.__vehicle_socket.close()
                break

    def run(self):
        threads = [
            threading.Thread(target = self.heartbeat_gps),
            threading.Thread(target = self.get_gps_all_objects),
            threading.Thread(target = self.get_traffic_light_state)
        ]

        for thread in threads:
            # thread.daemon = True
            thread.start()

    def set_state(self, state):
        self.__state = state

