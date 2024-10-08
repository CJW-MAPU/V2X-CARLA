import signal

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


def manage_vehicle_lifecycle(obu_id, port):
    def handle_terminate_signal(signum, frame):
        custom_vehicle.destroy_vehicle()
        exit(0)

    signal.signal(signal.SIGINT, handle_terminate_signal)
    client = carla.Client('127.0.0.1', 2000)
    client.set_timeout(2.0)

    world: carla.World = client.get_world()

    custom_vehicle = CustomVehicle(world = world, obu_id = obu_id, port = port)
    custom_vehicle.run()


def manage_gps_centre_lifecycle():
    gps_server = GPSCentre()
    gps_server.run()


def manage_traffic_light_lifecycle(index, rsu_id):
    client = carla.Client('127.0.0.1', 2000)
    client.set_timeout(2.0)

    world: carla.World = client.get_world()

    traffic_light = world.get_actors().filter('traffic.traffic_light')[index]

    custom_traffic_light = CustomTrafficLight(world = world, traffic_light = traffic_light, rsu_id = rsu_id)
    custom_traffic_light.run()


def main():
    client = carla.Client('127.0.0.1', 2000)
    client.set_timeout(2.0)

    world: carla.World = client.get_world()

    processes = []

    gps_process = multiprocessing.Process(target = manage_gps_centre_lifecycle, args = ())
    # gps_process.start()
    processes.append(gps_process)

    base_vehicle_port = 20000
    for i in range(1):
        vehicle_process = multiprocessing.Process(target = manage_vehicle_lifecycle, args = (f"OBU_{i}",
                                                                                             base_vehicle_port))
        # vehicle_process.start()
        processes.append(vehicle_process)
        base_vehicle_port += 10

    # TODO : TrafficLight List -> Process
    # TODO : TrafficLight Location <-> Vehicle Location

    traffic_lights = world.get_actors().filter('traffic.traffic_light')
    #
    for i, traffic_light in enumerate(traffic_lights):
        traffic_light_process = multiprocessing.Process(target = manage_traffic_light_lifecycle,
                                                        args = (i, f"RSU_{i + 1}"))
        # traffic_light_process.start()
        processes.append(traffic_light_process)
        # break

    for p in processes:
        p.start()

    try:
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        for p in processes:
            p.terminate()
        for p in processes:
            p.join()


if __name__ == '__main__':
    main()
