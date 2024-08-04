from modules.CustomVehicle import CustomVehicle
from modules.CustomTrafficLight import CustomTrafficLight
from modules.debug_tools import show_waypoints
from modules.GPSCentre import GPSCentre
from modules.SRModuleOBU import SRModuleOBU

import glob
import os
import sys
import multiprocessing
import logging

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla
import time


def manage_vehicle_lifecycle(obu_id):
    client = carla.Client('127.0.0.1', 2000)
    client.set_timeout(2.0)

    world: carla.World = client.get_world()

    custom_vehicle = CustomVehicle(world = world, obu_id = obu_id)
    custom_vehicle.run()


def manage_gps_centre_lifecycle():
    gps_server = GPSCentre()
    gps_server.run()


def main():
    processes = []

    gps_process = multiprocessing.Process(target = manage_gps_centre_lifecycle, args = ())
    gps_process.start()
    processes.append(gps_process)

    for i in range(1):
        vehicle_process = multiprocessing.Process(target = manage_vehicle_lifecycle, args = (f"OBU_{i}",))
        vehicle_process.start()
        processes.append(vehicle_process)

    for p in processes:
        p.join()


    # traffic_lights = world.get_actors().filter('traffic.traffic_light')
    # print(traffic_lights)
    # print(len(traffic_lights))
    #
    # traffic_light: carla.TrafficLight = traffic_lights[0]
    #
    # print(traffic_light.get_location())
    # # Point 시각화
    # world.debug.draw_point(traffic_light.get_location(), size = 0.1, color = carla.Color(r = 255, g = 0, b = 0), life_time = 60.0)
    #
    # # 텍스트 시각화
    # world.debug.draw_string(traffic_light.get_location(), text = 'Debug Point', draw_shadow = False,
    #                         color = carla.Color(r = 255, g = 255, b = 255), life_time = 60.0)
    #
    # print(traffic_light.get_affected_lane_waypoints())
    # print(traffic_light.get_stop_waypoints())
    # show_waypoints(world, traffic_light.get_affected_lane_waypoints())
    # show_waypoints(world, traffic_light.get_stop_waypoints())
    # for item in traffic_light.get_affected_lane_waypoints():
    #     print(item.transform.location)
    #
    # for item in traffic_light.get_stop_waypoints():
    #     print(item.transform.location)


if __name__ == '__main__':
    main()
