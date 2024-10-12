import threading
import time
import math

import carla

from modules.SRModuleRSU import SRModuleRSU


def calculate_distance(base, target):
    return math.sqrt(
        (base.transform.location.x - target["loc_x"]) ** 2 +
        (base.transform.location.y - target["loc_y"]) ** 2 +
        (base.transform.location.z - target["loc_z"]) ** 2
    )


def compare_state(base, target, threshold = 30.0) -> bool:
    distance = calculate_distance(base, target)

    # condition = ((base.previous(threshold)[0].lane_id == target['lane_id']) and
    #              (base.previous(threshold)[0].road_id == target['road_id']))

    return (distance <= threshold) and ((base.previous(threshold)[0].lane_id == target['lane_id']) and
                                        (base.previous(threshold)[0].road_id == target['road_id']))
    # return base.lane_id == target['lane_id'] and base.road_id == target['road_id']


class CustomTrafficLight(SRModuleRSU):
    __world: carla.World = None
    __traffic_light = carla.TrafficLight = None
    __rsu_id = None

    def __init__(self, world: carla.World, traffic_light: carla.TrafficLight, rsu_id):
        self.__world = world
        self.__traffic_light = traffic_light
        self.__rsu_id = rsu_id
        super().__init__(rsu_id, traffic_light)
        super().init(port = 55555)

    def filter_vehicles_by_traffic_light(self):
        traffic_light_waypoint = self.__traffic_light.get_stop_waypoints()
        debug_helper = self.__world.debug
        for waypoint in traffic_light_waypoint:
            debug_helper.draw_point(waypoint.transform.location, size = 0.1, color = carla.Color(0, 0, 0),
                                    life_time = 0)

        while True:
            states = super().get_states()
            for obu_id, state in states.items():
                try:
                    temp = list()
                    for waypoint in traffic_light_waypoint:
                        if compare_state(waypoint, state):
                            temp.append({obu_id: state["comm_port"]})
                            super().set_communication_list(temp)
                            super().handle_client(waypoint)
                    if not temp:
                        super().set_communication_list([])
                except KeyError:
                    continue
            time.sleep(0.1)

    def set_light_state(self):
        while True:
            super().set_light(self.__traffic_light.get_state())
            time.sleep(0.0001)

    def run(self):
        threads = [
            threading.Thread(target = self.filter_vehicles_by_traffic_light),
            threading.Thread(target = self.set_light_state)
        ]
        for thread in threads:
            # thread.daemon = True
            thread.start()
        super().run()
