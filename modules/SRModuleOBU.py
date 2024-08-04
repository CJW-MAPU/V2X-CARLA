import json
import socket
import threading
import time
import logging


class SRModuleOBU:
    def __init__(self, obu_id):
        self.__client_socket = None
        self.__obu_id = obu_id
        self.__states = {}
        self.__state = {}

    def init(self, port, host = 'localhost'):
        self.__client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__client_socket.connect((host, port))

    def heartbeat_gps(self):
        try:
            while True:
                print('[ SRModule.heartbeat_gps ]')
                loc_data = self.__state
                message = json.dumps(loc_data)
                self.__client_socket.send(message.encode('utf-8'))
                time.sleep(1)
        except ConnectionResetError:
            print('Connection lost')
        finally:
            self.__client_socket.close()
        pass

    def get_gps_all_objects(self):
        try:
            while True:
                print('[ SRModule.get_gps_all_objects ]')
                response = self.__client_socket.recv(1024).decode('utf-8')
                if not response:
                    break
                print(f'Received from server: {response}')
                self.__states = json.loads(response)
        except ConnectionResetError:
            print('Connection lost')
        finally:
            self.__client_socket.close()

    def run(self):
        threading.Thread(target = self.heartbeat_gps()).start()
        threading.Thread(target = self.get_gps_all_objects()).start()

    def set_state(self, state):
        self.__state = state

