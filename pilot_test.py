from modules.CustomVehicle import CustomVehicle

import glob
import os
import sys, threading

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass


import carla
import time


def manage_vehicle_lifecycle(thread_name, world):
    print(f'{thread_name} is started!!!')
    custom_vehicle = CustomVehicle(world = world)
    custom_vehicle.spawn_vehicle()
    custom_vehicle.pilot()
    time.sleep(30)
    custom_vehicle.destroy_vehicle()
    
def main():
    client = carla.Client('127.0.0.1', 2000)
    client.set_timeout(2.0)

    world = client.get_world()
   # manage_vehicle_lifecycle(world=world)
    
    threads = []
    num_of_threads=5
    for i in range(num_of_threads):
        thread_name = f"Thread-{i+1}"
        thread = threading.Thread(target=manage_vehicle_lifecycle, args=(thread_name, world))
        threads.append(thread)
        thread.start()

    # 모든 스레드가 종료될 때까지 대기
    for thread in threads:
        thread.join()
    print(f'All Threads are ended!!!')

if __name__ == '__main__':
    main()
