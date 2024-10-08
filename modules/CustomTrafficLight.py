import threading
import time
import socket
import json

import carla

from modules.SRModuleRSU import SRModuleRSU


def compare_state(base, target) -> bool:
    return base.lane_id == target['lane_id'] and base.road_id == target['road_id']


class CustomTrafficLight(SRModuleRSU):
    __world: carla.World = None
    __traffic_light = carla.TrafficLight = None

    def __init__(self, world: carla.World, traffic_light: carla.TrafficLight, rsu_id):
        self.__world = world
        self.__traffic_light = traffic_light
        super().__init__(rsu_id)
        super().init(port = 55555)

    def filter_vehicles_by_traffic_light(self):
        traffic_light_waypoint = self.__traffic_light.get_stop_waypoints()
        debug_helper = self.__world.debug
        for waypoint in traffic_light_waypoint:
            debug_helper.draw_point(waypoint.transform.location, size = 0.1, color = carla.Color(0, 0, 0),
                                    life_time = 0)
            debug_helper.draw_point(waypoint.previous(50)[0].transform.location, size = 0.1, color = carla.Color(0, 0, 0),
                                    life_time = 0)

        while True:
            states = super().get_states()

            for obu_id, state in states.items():
                for waypoint in traffic_light_waypoint:
                    if compare_state(waypoint.previous(30)[0], state):
                        self.__communication_list.append({obu_id: state["comm_port"]})
                        super().set_communication_list(self.__communication_list)
                        super().handle_client()
                    else:
                        self.__communication_list = list()
                    # print(self.__communication_list)

            time.sleep(0.0001)

    def run(self):
        threads = [
            threading.Thread(target = self.filter_vehicles_by_traffic_light)
        ]
        for thread in threads:
            # thread.daemon = True
            thread.start()
        super().run()
