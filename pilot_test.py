from modules.CustomVehicle import CustomVehicle

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


def main():
    client = carla.Client('127.0.0.1', 2000)
    client.set_timeout(2.0)

    world = client.get_world()

    custom_vehicle = CustomVehicle(world = world)

    custom_vehicle.spawn_vehicle()

    custom_vehicle.pilot()


    time.sleep(20)
    custom_vehicle.destroy_vehicle()


if __name__ == '__main__':
    main()
