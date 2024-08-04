import carla


class CustomTrafficLight:
    __world: carla.World = None
    __traffic_light = carla.TrafficLight = None

    def __init__(self, world: carla.World, traffic_light: carla.TrafficLight):
        self.__world = world
        self.__traffic_light = traffic_light

    def get_state(self):
        pass
