import time
import numpy as np
import matplotlib.pyplot as plt
from my_map import Map
from utils_np import distance_to_object


class Robot():
    ''' Robot class containing all data related to the robot '''
    def __init__(self, init_state, map_object, dt, sensor_noise_cov=None):
        (x0, y0, v0, phi0, dphi0) = init_state
        self.x = x0
        self.y = y0
        self.v = v0
        self.phi = phi0
        self.dphi = dphi0
        self.dt = dt
        self.T = 0

        self.ray = None
        self.collision_point = None
        self.dist = -1

        self.sensor_noise_cov = sensor_noise_cov
        self.map_object = map_object

    def update(self, dv, dphi, f=None):
        '''f is optional filewriter'''
        self.T += self.dt

        self.dphi = dphi

        self.x += self.dt * self.v * np.cos(self.phi)
        self.y += self.dt * self.v * np.sin(self.phi)

        self.phi += dphi * self.dt
        self.v += dv * self.dt

        self.ray, self.collision_point, self.dist = self.distance_to_object()

        if self.sensor_noise_cov is not None:  # add noise to the sensor
            self.dist += np.random.normal(scale=np.sqrt(self.sensor_noise_cov))

        if f is not None:
            f.write(self.get_state_as_string())

    def get_state_as_string(self):
        state_arr = '%.5f, %.5f, %.5f, %.5f, %.5f, %.5f, %.5f\n' % \
            (self.T, self.x, self.y, self.v, self.phi, self.dphi, self.dist)
        return state_arr

    def distance_to_object(self):
        st = np.array([self.x, self.y, self.phi])
        return distance_to_object(st[0], st[1], st[2], self.map_object.room, self.map_object.boundry)


class RobotIllustrator():
    '''Creates and removes plots associated with a robot class'''

    def __init__(self, ax, robot):
        self.ax = ax
        self.robot = robot

        self.p_handles = []
        self.t_handles = []

    def draw_robot(self):
        _, collision_point, dist = self.robot.distance_to_object()

        laser_ray = np.vstack(([self.robot.x, self.robot.y], collision_point))
        status_string = \
            'r: %.3f, v: %.3f, T: %.3f' % (dist[0], self.robot.v, self.robot.T)
        self.t_handles.append(self.ax.text(7, 11, status_string))
        self.p_handles.append(self.ax.plot(self.robot.x, self.robot.y, 'bo')[0])
        self.p_handles.append(self.ax.plot(laser_ray[:, 0], laser_ray[:, 1], 'r:')[0])
        self.p_handles.append(self.ax.plot(collision_point[:, 0], collision_point[:, 1], 'rx')[0])

    def remove_robot(self):
        for h in self.p_handles:
            h.remove()
        for h in self.t_handles:
            h.remove()

        self.p_handles = []
        self.t_handles = []


# ============================================================================================
#
#   TESTS
#
# ============================================================================================


if __name__ == '__main__':

    fig, ax = plt.subplots()

    my_map = Map(ax)
    dt = 0.1  # samplig time
    robot = Robot((4.5, 1.0, 0, np.pi / 2, 0), my_map, dt)
    keep_running = True

    def press(event):
        global f, keep_running
        if event.key == 'up':
            robot.update(1, 0, f)
        if event.key == 'down':
            robot.update(-1, 0, f)
        if event.key == 'left':
            robot.update(0, np.pi / 10, f)
        if event.key == 'right':
            robot.update(0, -np.pi / 10, f)
        if event.key == 'enter':
            keep_running = False

    fig.canvas.mpl_connect('key_press_event', press)

    illustrator = RobotIllustrator(ax, robot)
    illustrator.draw_robot()

    my_map.draw_map()

    f = open('data/robot_log5.txt', 'w')
    f.write(robot.get_state_as_string())  # get initial state at T=0
    while keep_running:
        start_time = time.time()

        illustrator.remove_robot()
        robot.update(0, 0, f)
        illustrator.draw_robot()
        ex = time.time() - start_time
        print(ex)
        plt.pause(0.1 - ex)

    f.close()
