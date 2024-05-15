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
import random
import time


def main():
    # 생성한 Object 를 기록할 List
    actor_list = []

    # CalraUE4.exe 실행 시 2000 포트로 서버 실행
    # 해당 서버(시뮬레이터)에 명령하기 위해 연결하는 코드
    client = carla.Client('127.0.0.1', 2000)
    client.set_timeout(2.0)

    # 실행된 서버가 생성한 월드 정보를 불러온다.
    world = client.get_world()

    # Object 생성을 위한 Blueprint Library 호출
    blueprint_library = world.get_blueprint_library()

    # 차종을 랜덤 선택하는 blueprint
    bp = random.choice(blueprint_library.filter('vehicle'))

    # 차종 설정
    if bp.has_attribute('color'):
        color = random.choice(bp.get_attribute('color').recommended_values)
        bp.set_attribute('color', color)

    # Object Spawn Point Random 설정
    transform = random.choice(world.get_map().get_spawn_points())

    # transform 위치에 bp Spawn
    vehicle = world.spawn_actor(bp, transform)

    actor_list.append(vehicle)
    print('created %s' % vehicle.type_id)

    # 차량 오토파일럿 설정
    vehicle.set_autopilot(True)

    location = vehicle.get_location()
    location.x += 40
    vehicle.set_location(location)
    print('moved vehicle to %s' % location)

    # 추가적인 차량 생성 프로세스
    transform.location += carla.Location(x = 40, y = -3.2)
    transform.rotation.yaw = -180.0
    for _ in range(0, 10):
        transform.location.x += 8.0

        bp = random.choice(blueprint_library.filter('vehicle'))

        npc = world.try_spawn_actor(bp, transform)
        if npc is not None:
            actor_list.append(npc)
            npc.set_autopilot(True)
            print('created %s' % npc.type_id)

    time.sleep(100)

    # 생성한 Object 파괴
    print('destroying actors')
    client.apply_batch([carla.command.DestroyActor(x) for x in actor_list])
    print('done.')


if __name__ == '__main__':
    main()
