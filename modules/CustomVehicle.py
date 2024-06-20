import time
import math
import carla
import random

from modules.debug_tools import show_waypoints


class CustomVehicle:
    __vehicle: carla.Vehicle = None
    __world: carla.World = None
    __current_waypoint: carla.Waypoint = None
    __path: list = list()

    @classmethod
    def __init__(cls, world: carla.World):
        cls.__world = world

    @classmethod
    def spawn_vehicle(cls):
        blueprint_library = cls.__world.get_blueprint_library()
        bp = random.choice(blueprint_library.filter('vehicle'))

        world_map = cls.__world.get_map()

        if bp.has_attribute('color'):
            color = random.choice(bp.get_attribute('color').recommended_values)
            bp.set_attribute('color', color)

        transform = random.choice(world_map.get_spawn_points())

        cls.__vehicle = cls.__world.spawn_actor(bp, transform)
        cls.__current_waypoint = world_map.get_waypoint(transform.location,
                                                        project_to_road = True,
                                                        lane_type = carla.LaneType.Driving)
        if cls.__current_waypoint.is_junction:
            if cls.__vehicle is not None:
                cls.__vehicle.destroy()
                cls.spawn_vehicle()

        debug_helper = cls.__world.debug
        debug_helper.draw_point(cls.__current_waypoint.transform.location, size = 0.1, color = carla.Color(255, 0, 0), life_time = 0)

    @classmethod
    def destroy_vehicle(cls) -> None:
        if cls.__vehicle is not None:
            cls.__vehicle.destroy()

    @classmethod
    def pilot(cls) -> None:
        while True:
            if not cls.__current_waypoint.is_junction:
                cls.__get_lane_path()
                cls.__lane_autopilot()
            else:
                cls.__get_junction_path()
                cls.__junction_autopilot()

    @classmethod
    def __lane_autopilot(cls):
        for target_waypoint in cls.__path:
            while True:
                control = cls.__calculate_control(target_waypoint)
                cls.__vehicle.apply_control(control)
                time.sleep(0.05)

                if cls.__vehicle.get_location().distance(target_waypoint.transform.location) < 2.0:
                    break

    @classmethod
    def __junction_autopilot(cls):
        for target_waypoint in cls.__path:
            while True:
                control = cls.__calculate_control(target_waypoint)
                cls.__vehicle.apply_control(control)
                time.sleep(0.05)

                if cls.__vehicle.get_location().distance(target_waypoint.transform.location) < 2.0:
                    break

    @classmethod
    def __get_lane_path(cls):
        cls.__path = cls.__current_waypoint.next_until_lane_end(2.0)
        cls.__current_waypoint = cls.__path[-1].next(2)[0]
        show_waypoints(cls.__world, cls.__path)

    @classmethod
    def __get_junction_path(cls) -> None:
        cls.__path = cls.__current_waypoint.get_junction().get_waypoints(carla.LaneType.Driving)

        debug_helper = cls.__world.debug

        for source, destination in cls.__path:
            if cls.__current_waypoint.road_id == source.road_id and cls.__current_waypoint.road_id == destination.road_id\
                    and cls.__current_waypoint.lane_id == source.lane_id and cls.__current_waypoint.lane_id == destination.lane_id:
                debug_helper.draw_point(source.transform.location, size = 0.1, color = carla.Color(0, 255, 0),
                                        life_time = 0)
                debug_helper.draw_point(destination.transform.location, size = 0.1, color = carla.Color(0, 255, 0),
                                        life_time = 0)
                cls.__path = source.next_until_lane_end(2.0)
                cls.__current_waypoint = destination.next(2)[0]
                show_waypoints(cls.__world, cls.__path)
                break

    @classmethod
    def __calculate_control(cls, target_waypoint) -> carla.VehicleControl:
        control = carla.VehicleControl()
        vehicle_transform = cls.__vehicle.get_transform()
        vehicle_location = vehicle_transform.location
        target_location = target_waypoint.transform.location

        direction_vector = target_location - vehicle_location
        direction_vector = direction_vector.make_unit_vector()
        vehicle_forward_vector = vehicle_transform.get_forward_vector()
        dot = direction_vector.x * vehicle_forward_vector.x + direction_vector.y * vehicle_forward_vector.y
        cross = direction_vector.y * vehicle_forward_vector.x - direction_vector.x * vehicle_forward_vector.y

        control.steer = max(-1.0, min(1.0, math.atan2(cross, dot) * 2.0))

        control.throttle = 0.5
        control.brake = 0.0

        return control
