import threading
import time
import math
import carla
import random

from modules.debug_tools import show_waypoints
from modules.SRModuleOBU import SRModuleOBU


class CustomVehicle(SRModuleOBU):
    __vehicle: carla.Vehicle = None
    __world: carla.World = None
    __current_waypoint: carla.Waypoint = None
    __path: list = list()
    __obu_id = None
    __port = None

    def __init__(self, world: carla.World, obu_id, port):
        self.__world = world
        self.__obu_id = obu_id
        self.__port = port
        super().__init__(obu_id = obu_id, vehicle_port = port)
        super().init(gps_port = 55555)

    def __heartbeat(self):
        while True:
            if self.__vehicle:
                location = self.__vehicle.get_location()
                lane_id = self.__world.get_map().get_waypoint(location).lane_id
                road_id = self.__world.get_map().get_waypoint(location).road_id
                super().set_state(
                    {
                        self.__obu_id: {
                            "loc_x": location.x,
                            "loc_y": location.y,
                            "loc_z": location.z,
                            "lane_id": lane_id,
                            "road_id": road_id,
                            "comm_port": self.__port
                        }
                    }
                )

    def __spawn_vehicle(self):
        blueprint_library = self.__world.get_blueprint_library()
        # bp = random.choice(blueprint_library.filter('vehicle'))
        bp = blueprint_library.find('vehicle.tesla.model3')

        world_map = self.__world.get_map()

        if bp.has_attribute('color'):
            color = random.choice(bp.get_attribute('color').recommended_values)
            bp.set_attribute('color', color)

        transform = random.choice(world_map.get_spawn_points())

        self.__vehicle = self.__world.spawn_actor(bp, transform)
        self.__current_waypoint = world_map.get_waypoint(transform.location,
                                                         project_to_road = True,
                                                         lane_type = carla.LaneType.Driving)
        if self.__current_waypoint.is_junction:
            if self.__vehicle is not None:
                self.__vehicle.destroy()
                self.__spawn_vehicle()

        debug_helper = self.__world.debug
        debug_helper.draw_point(self.__current_waypoint.transform.location, size = 0.1, color = carla.Color(255, 0, 0), life_time = 20)

    def destroy_vehicle(self) -> None:
        if self.__vehicle is not None:
            self.__vehicle.destroy()

    def __pilot(self) -> None:
        while True:
            if not self.__current_waypoint.is_junction:
                self.__get_lane_path()
                self.__lane_autopilot()
            else:
                self.__get_junction_path()
                self.__junction_autopilot()

    def __lane_autopilot(self):
        for i, target_waypoint in enumerate(self.__path):
            print(f'waypoint len : {len(self.__path)}')
            print(f'waypoint num : {i + 1}')
            while True:
                control = self.__calculate_control(target_waypoint)
                self.__vehicle.apply_control(control)
                time.sleep(0.05)

                if self.__vehicle.get_location().distance(target_waypoint.transform.location) < 2.0:
                    break

    def __junction_autopilot(self):
        for target_waypoint in self.__path:
            while True:
                control = self.__calculate_control(target_waypoint)
                self.__vehicle.apply_control(control)
                time.sleep(0.05)

                if self.__vehicle.get_location().distance(target_waypoint.transform.location) < 2.0:
                    break

    def __get_lane_path(self):
        self.__path = self.__current_waypoint.next_until_lane_end(2.0)
        self.__current_waypoint = self.__path[-1].next(2)[0]
        show_waypoints(self.__world, self.__path)

    def __get_junction_path(self) -> None:
        self.__path = self.__current_waypoint.get_junction().get_waypoints(carla.LaneType.Driving)

        debug_helper = self.__world.debug

        for source, destination in self.__path:
            if self.__current_waypoint.road_id == source.road_id and self.__current_waypoint.road_id == destination.road_id\
                    and self.__current_waypoint.lane_id == source.lane_id and self.__current_waypoint.lane_id == destination.lane_id:
                debug_helper.draw_point(source.transform.location, size = 0.1, color = carla.Color(0, 255, 0),
                                        life_time = 20)
                debug_helper.draw_point(destination.transform.location, size = 0.1, color = carla.Color(0, 255, 0),
                                        life_time = 20)
                self.__path = source.next_until_lane_end(2.0)
                self.__current_waypoint = destination.next(2)[0]
                show_waypoints(self.__world, self.__path)
                break

    def __calculate_control(self, target_waypoint) -> carla.VehicleControl:
        control = carla.VehicleControl()
        vehicle_transform = self.__vehicle.get_transform()
        vehicle_location = vehicle_transform.location
        target_location = target_waypoint.transform.location

        direction_vector = target_location - vehicle_location
        direction_vector = direction_vector.make_unit_vector()
        vehicle_forward_vector = vehicle_transform.get_forward_vector()
        dot = direction_vector.x * vehicle_forward_vector.x + direction_vector.y * vehicle_forward_vector.y
        cross = direction_vector.y * vehicle_forward_vector.x - direction_vector.x * vehicle_forward_vector.y

        control.steer = max(-1.0, min(1.0, math.atan2(cross, dot) * 2.0))

        control.throttle = 0.4
        control.brake = 0.0
        # control.hand_brake = False

        try:
            traffic_light_state = self.traffic_light_state["light_state"]
            stop_waypoint_x = self.traffic_light_state["waypoint_x"]
            stop_waypoint_y = self.traffic_light_state["waypoint_y"]
            stop_waypoint_z = self.traffic_light_state["waypoint_z"]

            stop_location = carla.Location(x = stop_waypoint_x, y = stop_waypoint_y, z = stop_waypoint_z)

            # 차량 현재 위치에서 시작하는 waypoint를 가져옴
            current_waypoint = self.__world.get_map().get_waypoint(vehicle_location)
            stop_waypoint = self.__world.get_map().get_waypoint(stop_location)

            # 곡선 거리 계산
            total_distance = 0.0
            while current_waypoint.transform.location.distance(stop_waypoint.transform.location) > 1.0:  # 멈출 위치까지 거리 확인
                next_waypoints = current_waypoint.next(1.0)  # 1.0 미터 떨어진 다음 waypoint
                if next_waypoints:
                    next_waypoint = next_waypoints[0]  # 첫 번째 다음 waypoint 선택
                    total_distance += current_waypoint.transform.location.distance(next_waypoint.transform.location)
                    current_waypoint = next_waypoint
                else:
                    break  # 더 이상 waypoint가 없으면 종료

            if traffic_light_state in [carla.TrafficLightState.Red, carla.TrafficLightState.Yellow]:
                if total_distance <= 10.0:
                    control.throttle = 0.0
                    control.brake = 1.0
                    # control.hand_brake = True
        except KeyError:
            pass

        return control

    def run(self):
        threads = [
            threading.Thread(target = self.__pilot),
            threading.Thread(target = self.__heartbeat),
        ]
        self.__spawn_vehicle()
        for thread in threads:
            # thread.daemon = True
            thread.start()
        super().run()

