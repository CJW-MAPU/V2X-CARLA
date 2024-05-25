from modules.CustomVehicle import CustomVehicle

import glob
import os
import sys
import threading
import asyncio

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass


import carla
import time


# async def manage_vehicle_lifecycle(world):
#     custom_vehicle = CustomVehicle(world = world)
#
#     custom_vehicle.spawn_vehicle()
#
#     await custom_vehicle.pilot()
#     time.sleep(40)
#
#     custom_vehicle.destroy_vehicle()


def main():
    client = carla.Client('127.0.0.1', 2000)
    client.set_timeout(2.0)

    world = client.get_world()

    custom_vehicle = CustomVehicle(world = world)
    try:
        custom_vehicle.spawn_vehicle()

        custom_vehicle.pilot()
        time.sleep(40)
    except KeyboardInterrupt:
        custom_vehicle.destroy_vehicle()
    # tasks = []
    # for i in range(5):
    #     task = asyncio.create_task(manage_vehicle_lifecycle(world))
    #     tasks.append(task)
    #
    # await asyncio.gather(*tasks)


if __name__ == '__main__':
    # asyncio.run(main())
    main()