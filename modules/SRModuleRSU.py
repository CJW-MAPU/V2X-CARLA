import json
import socket
import threading
import time
import carla


class SRModuleRSU:
    def __init__(self, rsu_id, traffic_light):
        self.__gps_socket = None
        self.__obu_sockets = []
        self.__rsu_id = rsu_id
        self.__vehicle_states = {}
        self.__communication_list = list()
        self.lock = threading.Lock()
        self.__traffic_light = traffic_light
        self.__light = None

    def init(self, port, host = 'localhost'):
        self.__gps_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__gps_socket.connect((host, port))

    def get_gps_all_objects(self):
        while True:
            try:
                response = self.__gps_socket.recv(1024).decode('utf-8')
                if not response:
                    break
                self.__vehicle_states = json.loads(response)
            except ConnectionResetError:
                print('Connection lost')
            except json.JSONDecodeError:
                print(f"Received invalid JSON, RSU: {self.__rsu_id}")
            except KeyboardInterrupt:
                self.__gps_socket.close()

    def set_communication_list(self, communication_list):
        self.__communication_list = communication_list

    def handle_client(self, waypoint: carla.Waypoint, host = 'localhost'):
        client_sockets = {}  # 각 클라이언트별 소켓을 저장할 딕셔너리

        if len(self.__communication_list) == 0:
            # communication_list가 비워졌으면 모든 소켓 닫기
            for client_socket in client_sockets.values():
                client_socket.close()
            client_sockets.clear()  # 소켓 리스트 초기화

            time.sleep(0.0001)  # 리스트가 비어있으면 대기
        else:
            with self.lock:
                list_copy = self.__communication_list.copy()
            for client in list_copy:
                for obu_id, comm_port in client.items():
                    # 만약 소켓이 없으면 새로 생성
                    if comm_port not in client_sockets:
                        try:
                            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            client_socket.connect((host, comm_port))
                            client_sockets[comm_port] = client_socket  # 생성한 소켓 저장
                        except ConnectionRefusedError:
                            print(f"Connection lost for port {comm_port}")
                            continue  # 연결 실패 시 다음 클라이언트로

                    # 소켓이 이미 연결되어 있으면 데이터 전송
                    try:
                        data = {
                            'rsu_id': self.__rsu_id,
                            'light_state': self.__light,
                            'waypoint_x': waypoint.transform.location.x,
                            'waypoint_y': waypoint.transform.location.y,
                            'waypoint_z': waypoint.transform.location.z
                        }
                        message = json.dumps(data)
                        client_sockets[comm_port].send(message.encode('utf-8'))
                        time.sleep(0.001)
                    except ConnectionRefusedError:
                        print(f"Connection lost for port {comm_port}")
                        client_sockets[comm_port].close()
                        del client_sockets[comm_port]  # 문제가 발생한 소켓 삭제
                        continue
            # 통신 완료 후 communication_list 초기화
            self.__communication_list = []
            time.sleep(0.0001)
        # while True:
        #     if len(self.__communication_list) == 0:
        #         continue
        #     else:
        #         with self.lock:
        #             list_copy = self.__communication_list.copy()
        #         for client in list_copy:
        #             print(client)
        #             for data in client.items():
        #                 obu_id, comm_port = data
        #                 client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #                 client_socket.connect((host, comm_port))
        #                 try:
        #                     data = {
        #                         'light_state': self.__light,
        #                         'waypoint_x': waypoint.transform.location.x,
        #                         'waypoint_y': waypoint.transform.location.y,
        #                         'waypoint_z': waypoint.transform.location.z
        #                     }
        #                     message = json.dumps(data)
        #                     client_socket.send(message.encode('utf-8'))
        #                     time.sleep(0.001)
        #                 except ConnectionRefusedError:
        #                     print('Connection lost')
        #
        #     self.__communication_list = []
        #     time.sleep(0.0001)

    def get_states(self):
        return self.__vehicle_states

    def set_light(self, light):
        self.__light = light

    def run(self):
        threads = [
            threading.Thread(target = self.get_gps_all_objects)
        ]
        for thread in threads:
            thread.start()

