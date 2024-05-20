import carla


def show_waypoints(world, all_waypoints):
    debug_helper = world.debug
    for waypoint in all_waypoints:
        debug_helper.draw_point(waypoint.transform.location, size = 0.1, color = carla.Color(0, 0, 255), life_time = 0)
        # print("Waypoint 위치:", waypoint.transform.location)
        
def show_waypoints2(world, all_waypoints):
    debug_helper = world.debug
    for waypoint in all_waypoints:
        debug_helper.draw_point(waypoint.transform.location, size = 0.1, color = carla.Color(0, 255, 0), life_time = 0)
        # print("Waypoint 위치:", waypoint.transform.location)

