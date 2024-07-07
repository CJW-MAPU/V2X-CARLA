import threading

from modules.CustomVehicle import CustomVehicle
from modules.CustomTrafficLight import CustomTrafficLight
from modules.debug_tools import show_waypoints
from modules.GPSCentre import GPSCentre
from modules.SRModule import SRModule

import glob
import os
import sys

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla
import time


# def main():
#     client = carla.Client('127.0.0.1', 2000)
#     client.set_timeout(2.0)
#
#     world: carla.World = client.get_world()
#
#     traffic_lights = world.get_actors().filter('traffic.traffic_light')
#     print(traffic_lights)
#     print(len(traffic_lights))
#
#     traffic_light: carla.TrafficLight = traffic_lights[0]
#
#     print(traffic_light.get_location())
#     # Point 시각화
#     world.debug.draw_point(traffic_light.get_location(), size = 0.1, color = carla.Color(r = 255, g = 0, b = 0), life_time = 60.0)
#
#     # 텍스트 시각화
#     world.debug.draw_string(traffic_light.get_location(), text = 'Debug Point', draw_shadow = False,
#                             color = carla.Color(r = 255, g = 255, b = 255), life_time = 60.0)
#
#     print(traffic_light.get_affected_lane_waypoints())
#     print(traffic_light.get_stop_waypoints())
#     show_waypoints(world, traffic_light.get_affected_lane_waypoints())
#     show_waypoints(world, traffic_light.get_stop_waypoints())
#     for item in traffic_light.get_affected_lane_waypoints():
#         print(item.transform.location)
#
#     for item in traffic_light.get_stop_waypoints():
#         print(item.transform.location)

    #
    # custom_vehicle = CustomVehicle(world = world)
    # try:
    #     custom_vehicle.spawn_vehicle()
    #
    #     custom_vehicle.pilot()
    #     time.sleep(40)
    # except KeyboardInterrupt:
    #     custom_vehicle.destroy_vehicle()

def main():
    gps_server = GPSCentre()

    sr_module_1 = SRModule(obu_id = 'OBU_10')
    sr_module_1.init(port = 55555)
    sr_module_2 = SRModule(obu_id = 'OBU_20')
    sr_module_2.init(port = 55555)
    threading.Thread(target = gps_server.start_server).start()
    threading.Thread(target = sr_module_1.heartbeat_gps).start()
    threading.Thread(target = sr_module_1.get_gps_all_objects).start()
    threading.Thread(target = sr_module_2.heartbeat_gps).start()
    threading.Thread(target = sr_module_2.get_gps_all_objects).start()


if __name__ == '__main__':
    main()
