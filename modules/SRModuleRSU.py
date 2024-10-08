import json
import socket
import threading
import time


class SRModuleRSU:
    def __init__(self, rsu_id):
        self.__gps_socket = None
        self.__obu_sockets = []
        self.__rsu_id = rsu_id
        self.__vehicle_states = {}
        self.__communication_list = list()
        self.lock = threading.Lock()

    def init(self, port, host = 'localhost'):
        self.__gps_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__gps_socket.connect((host, port))

    def get_gps_all_objects(self):
        while True:
            try:
                # print(f'[ SRModuleRSU.get_gps_all_objects : RSU_ID = {self.__rsu_id} ]')
                response = self.__gps_socket.recv(1024).decode('utf-8')
                if not response:
                    break
                # print(f'Received from server: {response}')
                self.__vehicle_states = json.loads(response)
            except ConnectionResetError:
                print('Connection lost')
            except json.JSONDecodeError:
                print("Received invalid JSON, RSU")
            except KeyboardInterrupt:
                self.__gps_socket.close()

    def set_communication_list(self, communication_list):
        self.__communication_list = communication_list

    def handle_client(self, host = 'localhost'):
        while True:
            if len(self.__communication_list) == 0:
                continue
            else:
                with self.lock:
                    list_copy = self.__communication_list.copy()
                for client in list_copy:
                    print(client)
                    for data in client.items():
                        obu_id, comm_port = data
                        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        client_socket.connect((host, comm_port))
                        try:
                            data = {
                                # 'waypoint': self.__traffic_light.get_stop_waypoints().
                            }
                            client_socket.send(json.dumps(data).encode('utf-8'))
                        except ConnectionRefusedError:
                            print('Connection lost')
                        finally:
                            client_socket.close()
            self.__communication_list = []
            time.sleep(0.001)

    def get_states(self):
        return self.__vehicle_states

    def run(self):
        threads = [
            threading.Thread(target = self.get_gps_all_objects)
        ]
        for thread in threads:
            # thread.daemon = True
            thread.start()

