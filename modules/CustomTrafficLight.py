import carla


class CustomTrafficLight:
    __world: carla.World = None
    __traffic_light = carla.TrafficLight = None

    @classmethod
    def __init__(cls, world: carla.World, traffic_light: carla.TrafficLight):
        cls.__world = world
        cls.__traffic_light = traffic_light

    @classmethod
    def get_state(cls):
        pass
