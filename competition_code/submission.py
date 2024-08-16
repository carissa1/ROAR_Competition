
"""
Competition instructions:
Please do not change anything else but fill out the to-do sections.
"""

from collections import deque
from functools import reduce
from typing import List, Tuple, Dict, Optional
import math
import numpy as np
import roar_py_interface


def normalize_rad(rad : float):
    return (rad + np.pi) % (2 * np.pi) - np.pi

def distance_p_to_p(p1: roar_py_interface.RoarPyWaypoint, p2: roar_py_interface.RoarPyWaypoint):
    return np.linalg.norm(p2.location[:2] - p1.location[:2])

def filter_waypoints(location : np.ndarray, current_idx: int, waypoints : List[roar_py_interface.RoarPyWaypoint]) -> int:
    def dist_to_waypoint(waypoint : roar_py_interface.RoarPyWaypoint):
        return np.linalg.norm(
            location[:2] - waypoint.location[:2]
        )
    for i in range(current_idx, len(waypoints) + current_idx):
        if dist_to_waypoint(waypoints[i%len(waypoints)]) < 3:
            return i % len(waypoints)
    return current_idx

def new_x_y(x, y):
        new_location = np.array([x, y, 0])
        return roar_py_interface.RoarPyWaypoint(location=new_location, 
                                                roll_pitch_yaw=np.array([0,0,0]), 
                                                lane_width=5)

class RoarCompetitionSolution:
    def __init__(
        self,
        maneuverable_waypoints: List[roar_py_interface.RoarPyWaypoint],
        vehicle : roar_py_interface.RoarPyActor,
        camera_sensor : roar_py_interface.RoarPyCameraSensor = None,
        location_sensor : roar_py_interface.RoarPyLocationInWorldSensor = None,
        velocity_sensor : roar_py_interface.RoarPyVelocimeterSensor = None,
        rpy_sensor : roar_py_interface.RoarPyRollPitchYawSensor = None,
        occupancy_map_sensor : roar_py_interface.RoarPyOccupancyMapSensor = None,
        collision_sensor : roar_py_interface.RoarPyCollisionSensor = None,
    ) -> None:
        # self.maneuverable_waypoints = maneuverable_waypoints[:1962] + maneuverable_waypoints[1967:]
        # startInd = 1953
        startInd_8 = 1800
        endInd_8 = 2006
        startInd_12 = 2586
        # endInd = 1967
        # endInd = startInd+len(NEW_WAYPOINTS)
        # self.maneuverable_waypoints = \
        #     maneuverable_waypoints[:startInd_8] + SEC_8_WAYPOINTS \
        #         + maneuverable_waypoints[endInd_8:] 
        # self.maneuverable_waypoints = \
        #     maneuverable_waypoints[:startInd_8] + SEC_8_WAYPOINTS \
        #         + maneuverable_waypoints[endInd_8:startInd_12] \
        #         + SEC_12_WAYPOINTS
        self.maneuverable_waypoints = DOC_WAYPOINTS[:2592] + SEC_12_WAYPOINTS        # self.maneuverable_waypoints = self.modified_points(maneuverable_waypoints)
        self.vehicle = vehicle
        self.camera_sensor = camera_sensor
        self.location_sensor = location_sensor
        self.velocity_sensor = velocity_sensor
        self.rpy_sensor = rpy_sensor
        self.occupancy_map_sensor = occupancy_map_sensor
        self.collision_sensor = collision_sensor
        self.lat_pid_controller = LatPIDController(config=self.get_lateral_pid_config())
        self.throttle_controller = ThrottleController()
        self.section_indeces = []
        self.num_ticks = 0
        self.section_start_ticks = 0
        self.current_section = -1

    async def initialize(self) -> None:
        num_sections = 12
        #indexes_per_section = len(self.maneuverable_waypoints) // num_sections
        #self.section_indeces = [indexes_per_section * i for i in range(0, num_sections)]
        # self.section_indeces = [198, 438, 547, 691, 803, 884, 1287, 1508, 1854, 1968, 2264, 2662, 2770]
<<<<<<< Updated upstream
        self.section_indeces = [198, 438, 547, 691, 803, 884, 1287, 1508, 1854, 1968, 2264, 2592, 2770]
        print(f"1 lap length: {len(self.maneuverable_waypoints)}")
        print(f"indexes: {self.section_indeces}")

=======
        #self.section_indeces = [198, 438, 547, 691, 803, 884, 1287, 1508, 1854, 1968, 2264, 2592, 2770]
        #self.section_indeces = [202, 442, 551, 695, 807, 893, 1287, 1508, 1854, 1968, 2264, 2592, 2770] # -- kinda altered
        self.section_indeces = [198, 438, 547, 691, 803, 893, 1287, 1505, 1851, 1968, 2264, 2592,2700, 2773] #original
        # [198, 438, 547, 691, 803, 893, 1287, 1508, 1854, 1968, 2264, 2592, 2779]
        #self.section_indeces = [202,442,551, 695, 807, 888, 1297, 1504, 1850, 1967, 2255, 2592, 2770] #-- fullly altered
        print(f"1 lap length: {len(self.maneuverable_waypoints)}")
        print(f"indexes: {self.section_indeces}")

        

>>>>>>> Stashed changes
        # Receive location, rotation and velocity data 
        vehicle_location = self.location_sensor.get_last_gym_observation()
        vehicle_rotation = self.rpy_sensor.get_last_gym_observation()
        vehicle_velocity = self.velocity_sensor.get_last_gym_observation()

        self.current_waypoint_idx = 10
        self.current_waypoint_idx = filter_waypoints(
            vehicle_location,
            self.current_waypoint_idx,
            self.maneuverable_waypoints
        )

    # def modified_points(self, waypoints):
    #     new_points = []
    #     for ind, waypoint in enumerate(waypoints):
    #         if ind == 1964:
    #             new_points.append(self.new_x(waypoint, -151))
    #         elif ind == 1965:
    #             new_points.append(self.new_x(waypoint, -153))
    #         elif ind == 1966:
    #             new_points.append(self.new_x(waypoint, -155))
    #         else:
    #             new_points.append(waypoint)
    #     return new_points
        
    def modified_points_bad(self, waypoints):
        end_ind = 1964
        num_points = 50
        start_ind = end_ind - num_points
        shift_vector = np.array([0.5, 0, 0])
        step_vector = shift_vector / num_points

        s2 = 1965
        num_points2 = 150
        shift_vector2 = np.array([0, 2.0, 0])


        new_points = []
        for ind, waypoint in enumerate(waypoints):
            p = waypoint
            if ind >= start_ind and ind < end_ind:
                p = self.point_plus_vec(p, step_vector * (ind - start_ind))
            if ind >= s2 and ind < s2 + num_points2:
                 p = self.point_plus_vec(p, shift_vector2)
            new_points.append(p)
        return new_points

    def modified_points_good(self, waypoints):
        start_ind = 1920
        num_points = 100
        end_ind = start_ind + num_points
        shift_vector = np.array([2.8, 0, 0])
        step_vector = shift_vector / num_points

        s2 = 1965
        num_points2 = 150
        shift_vector2 = np.array([0, 3.5, 0])

        s3 = 1920
        num_points3 = 195
        shift_vector3 = np.array([0.0, 0, 0])

        new_points = []
        for ind, waypoint in enumerate(waypoints):
            p = waypoint
            if ind >= start_ind and ind < end_ind:
                p = self.point_plus_vec(p, step_vector * (end_ind - ind))
                # p = self.point_plus_vec(p, step_vector * (end_ind - ind))
            if ind >= s2 and ind < s2 + num_points2:
                p = self.point_plus_vec(p, shift_vector2)
            if ind >= s3 and ind < s3 + num_points3:
                p = self.point_plus_vec(p, shift_vector3)
            new_points.append(p)
        return new_points

    def point_plus_vec(self, waypoint, vector):
        new_location = waypoint.location + vector
        # new_location = np.array([waypoint.location[0], new_y, waypoint.location[2]])
        return roar_py_interface.RoarPyWaypoint(location=new_location,
                                                roll_pitch_yaw=waypoint.roll_pitch_yaw,
                                                lane_width=waypoint.lane_width)


    def modified_points_also_bad(self, waypoints):
        new_points = []
        for ind, waypoint in enumerate(waypoints):
            if ind >= 1962 and ind <= 2027:
                new_points.append(self.new_point(waypoint, self.new_y(waypoint.location[0])))
            else:
                new_points.append(waypoint)
        return new_points
    

    def new_x(self, waypoint, new_x):
        new_location = np.array([new_x, waypoint.location[1], waypoint.location[2]])
        return roar_py_interface.RoarPyWaypoint(location=new_location, 
                                                roll_pitch_yaw=waypoint.roll_pitch_yaw, 
                                                lane_width=waypoint.lane_width)
    def new_point(self, waypoint, new_y):
        new_location = np.array([waypoint.location[0], new_y, waypoint.location[2]])
        return roar_py_interface.RoarPyWaypoint(location=new_location, 
                                                roll_pitch_yaw=waypoint.roll_pitch_yaw, 
                                                lane_width=waypoint.lane_width)
    def new_y(self, x):

        y = -math.sqrt(102**2 - (x + 210)**2) - 962
        #print(str(x) + ',' + str(y))
        return y
        
        # a=0.000322627
        # b=2.73377
        # y = a * ( (abs(x + 206))**b ) - 1063.5
        # return y

    async def step(
        self
    ) -> None:
        """
        This function is called every world step.
        Note: You should not call receive_observation() on any sensor here, instead use get_last_observation() to get the last received observation.
        You can do whatever you want here, including apply_action() to the vehicle.
        """
        self.num_ticks += 1

        # Receive location, rotation and velocity data 
        vehicle_location = self.location_sensor.get_last_gym_observation()
        vehicle_rotation = self.rpy_sensor.get_last_gym_observation()
        vehicle_velocity = self.velocity_sensor.get_last_gym_observation()
        vehicle_velocity_norm = np.linalg.norm(vehicle_velocity)
        current_speed_kmh = vehicle_velocity_norm * 3.6
        
        # Find the waypoint closest to the vehicle
        self.current_waypoint_idx = filter_waypoints(
            vehicle_location,
            self.current_waypoint_idx,
            self.maneuverable_waypoints
        )

        # compute and print section timing
        for i, section_ind in enumerate(self.section_indeces):
            if section_ind -2 <= self.current_waypoint_idx \
                and self.current_waypoint_idx <= section_ind + 2 \
                    and i != self.current_section:
                elapsed_ticks = self.num_ticks - self.section_start_ticks
                self.section_start_ticks = self.num_ticks
                self.current_section = i
                print(f"Section {i}: {elapsed_ticks}")

        new_waypoint_index = self.get_lookahead_index(current_speed_kmh)
        waypoint_to_follow = self.next_waypoint_smooth(current_speed_kmh)
        #waypoint_to_follow = self.maneuverable_waypoints[new_waypoint_index]

        # Proportional controller to steer the vehicle
        steer_control = self.lat_pid_controller.run(
            vehicle_location, vehicle_rotation, current_speed_kmh, self.current_section, waypoint_to_follow)

        # Proportional controller to control the vehicle's speed
        waypoints_for_throttle = \
            (self.maneuverable_waypoints + self.maneuverable_waypoints)[new_waypoint_index:new_waypoint_index + 300]
        throttle, brake, gear = self.throttle_controller.run(
            self.current_waypoint_idx, waypoints_for_throttle, vehicle_location, current_speed_kmh, self.current_section)

        control = {
            "throttle": np.clip(throttle, 0.0, 1.0),
            "steer": np.clip(steer_control, -1.0, 1.0),
            "brake": np.clip(brake, 0.0, 1.0),
            "hand_brake": 0.0,
            "reverse": 0,
            "target_gear": gear
        }

        # print("--- " + str(throttle) + " " + str(brake) 
        #             + " steer " + str(steer_control)
        #             + " loc: " + str(vehicle_location)
        #             + " cur_ind: " + str(self.current_waypoint_idx)
        #             + " cur_sec: " + str(self.current_section)
        #             ) 


        await self.vehicle.apply_action(control)
        return control

    def get_lookahead_value(self, speed):
        speed_to_lookahead_dict = {
            70: 12,
            90: 12,
            110: 13,
            130: 14,
            160: 16,
            180: 20,
            200: 24,
            300: 24
        }
        num_waypoints = 3
        for speed_upper_bound, num_points in speed_to_lookahead_dict.items():
            if speed < speed_upper_bound:
              num_waypoints = num_points
              break
            
            if self.current_section in [6,7]:
                num_waypoints = num_points*3//2

        return num_waypoints

    def get_lookahead_index(self, speed):
        num_waypoints = self.get_lookahead_value(speed)
        # print("speed " + str(speed) 
        #       + " cur_ind " + str(self.current_waypoint_idx) 
        #       + " num_points " + str(num_waypoints) 
        #       + " index " + str((self.current_waypoint_idx + num_waypoints) % len(self.maneuverable_waypoints)) )
        return (self.current_waypoint_idx + num_waypoints) % len(self.maneuverable_waypoints)
    
    def get_lateral_pid_config(self):
        conf = {
            "30": {
                "Kp": 1.00,
                "Kd": 0.03,
                "Ki": 0.02
            },
            "40": {
                "Kp": 0.90,
                "Kd": 0.04,
                "Ki": 0.03
            },
            "50": {
                "Kp": 0.85,
                "Kd": 0.05,
                "Ki": 0.04
            },
            "60": {
                "Kp": 0.8034,
                "Kd": 0.0521,
                "Ki": 0.0518
            },
            "70": {
                "Kp": 0.7025,
                "Kd": 0.0698,
                "Ki": 0.0712
            },
            "80": {
                "Kp": 0.6621,
                "Kd": 0.0807,
                "Ki": 0.0804
            },
            "90": {
                "Kp": 0.6289,
                "Kd": 0.0903,
                "Ki": 0.0921
            },
            "100": {
                "Kp": 0.6012,
                "Kd": 0.1005,
                "Ki": 0.1013
            },
            "120": {
                "Kp": 0.5243,
                "Kd": 0.0987,
                "Ki": 0.1004
            },
            "130": {
                "Kp": 0.5114,
                "Kd": 0.1012,
                "Ki": 0.0905
            },
            "140": {
                "Kp": 0.4489,
                "Kd": 0.0995,
                "Ki": 0.0899
            },
            "160": {
                "Kp": 0.3987,
                "Kd": 0.0502,
                "Ki": 0.0589
            },
            "180": {
                "Kp": 0.2874,
                "Kd": 0.0221,
                "Ki": 0.0517
            },
            "200": {
                "Kp": 0.2876,
                "Kd": 0.0312,
                "Ki": 0.0421
            },
            "230": {
                "Kp": 0.2658,
                "Kd": 0.0401,
                "Ki": 0.0504
            },
            "250": {
                "Kp": 0.2500,
                "Kd": 0.0350,
                "Ki": 0.0450
            },
            "270": {
                "Kp": 0.2450,
                "Kd": 0.0320,
                "Ki": 0.0400
            },
            "300": {
                "Kp": 0.2065,
                "Kd": 0.0082,
                "Ki": 0.0181
            }
        }
        return conf

    # The idea and code for averaging points is from smooth_waypoint_following_local_planner.py
    def next_waypoint_smooth(self, current_speed: float):
        if current_speed > 70 and current_speed < 300:
            target_waypoint = self.average_point(current_speed)
        else:
            new_waypoint_index = self.get_lookahead_index(current_speed)
            target_waypoint = self.maneuverable_waypoints[new_waypoint_index]
        return target_waypoint

    def average_point(self, current_speed):
        next_waypoint_index = self.get_lookahead_index(current_speed)
        lookahead_value = self.get_lookahead_value(current_speed)
        num_points = lookahead_value * 2
        
<<<<<<< Updated upstream
        # if self.current_section in [12]:
        #     num_points = lookahead_value
        if self.current_section in [8,9]:
            # num_points = lookahead_value // 2
            num_points = lookahead_value * 2
=======
        if self.current_section in [12]:
            num_points = lookahead_value
        if self.current_section in [8,9]:
            # num_points = lookahead_value // 2
            num_points = lookahead_value * 2
        
        # if self.current_section in[6,7]:
        #     num_points = lookahead_value //2
        
>>>>>>> Stashed changes
            # num_points = lookahead_value
            # num_points = 1
        start_index_for_avg = (next_waypoint_index - (num_points // 2)) % len(self.maneuverable_waypoints)

        next_waypoint = self.maneuverable_waypoints[next_waypoint_index]
        next_location = next_waypoint.location
  
        sample_points = [(start_index_for_avg + i) % len(self.maneuverable_waypoints) for i in range(0, num_points)]
        if num_points > 3:
            location_sum = reduce(lambda x, y: x + y,
                                  (self.maneuverable_waypoints[i].location for i in sample_points))
            num_points = len(sample_points)
            new_location = location_sum / num_points
            shift_distance = np.linalg.norm(next_location - new_location)
            max_shift_distance = 2.0
            if self.current_section in [1,2]:
<<<<<<< Updated upstream
                max_shift_distance = 0.2
            if self.current_section in [6, 7]:
                max_shift_distance = 1.0
            if self.current_section in [8,9]:
                max_shift_distance = 2.8
            if self.current_section in [10,11]:
                max_shift_distance = 0.2
            if self.current_section in [12]:
                max_shift_distance = 0.4
=======
                max_shift_distance = 0.1
            if self.current_section in [6, 7]:
                max_shift_distance = 0.65
            if self.current_section in [8,9]:
                max_shift_distance = 3.8
            if self.current_section in [10,11]:
                max_shift_distance = 0.2
            if self.current_section in [12]:
                max_shift_distance =0.4
            if self.current_section in [13]:
                max_shift_distance = -0.6
>>>>>>> Stashed changes
            if shift_distance > max_shift_distance:
                uv = (new_location - next_location) / shift_distance
                new_location = next_location + uv*max_shift_distance

            target_waypoint = roar_py_interface.RoarPyWaypoint(location=new_location, 
                                                               roll_pitch_yaw=np.ndarray([0, 0, 0]), 
                                                               lane_width=0.0)
            # if next_waypoint_index > 1900 and next_waypoint_index < 2300:
            #   print("AVG: next_ind:" + str(next_waypoint_index) + " next_loc: " + str(next_location) 
            #       + " new_loc: " + str(new_location) + " shift:" + str(shift_distance)
            #       + " num_points: " + str(num_points) + " start_ind:" + str(start_index_for_avg)
            #       + " curr_speed: " + str(current_speed))

        else:
            target_waypoint =  self.maneuverable_waypoints[next_waypoint_index]

        return target_waypoint

class LatPIDController():
    def __init__(self, config: dict, dt: float = 0.05):
        self.config = config
        self.steering_boundary = (-1.0, 1.0)
        self._error_buffer = deque(maxlen=10)
        self._dt = dt

    def run(self, vehicle_location, vehicle_rotation, current_speed, cur_section, next_waypoint) -> float:
        """
        Calculates a vector that represent where you are going.
        Args:
            next_waypoint ():
            **kwargs ():

        Returns:
            lat_control
        """
        # calculate a vector that represent where you are going
        v_begin = vehicle_location
        direction_vector = np.array([
            np.cos(normalize_rad(vehicle_rotation[2])),
            np.sin(normalize_rad(vehicle_rotation[2])),
            0])
        v_end = v_begin + direction_vector

        v_vec = np.array([(v_end[0] - v_begin[0]), (v_end[1] - v_begin[1]), 0])
        
        # calculate error projection
        w_vec = np.array(
            [
                next_waypoint.location[0] - v_begin[0],
                next_waypoint.location[1] - v_begin[1],
                0,
            ]
        )

        v_vec_normed = v_vec / np.linalg.norm(v_vec)
        w_vec_normed = w_vec / np.linalg.norm(w_vec)
        error = np.arccos(min(max(v_vec_normed @ w_vec_normed.T, -1), 1)) # makes sure arccos input is between -1 and 1, inclusive
        _cross = np.cross(v_vec_normed, w_vec_normed)

        if _cross[2] > 0:
            error *= -1
        self._error_buffer.append(error)
        if len(self._error_buffer) >= 2:
            _de = (self._error_buffer[-1] - self._error_buffer[-2]) / self._dt
            _ie = sum(self._error_buffer) * self._dt
        else:
            _de = 0.0
            _ie = 0.0

        k_p, k_d, k_i = self.find_k_values(cur_section, current_speed=current_speed, config=self.config)

        lat_control = float(
            np.clip((k_p * error) + (k_d * _de) + (k_i * _ie), self.steering_boundary[0], self.steering_boundary[1])
        )
        
        # PIDFastController.sdprint("steer: " + str(lat_control) + " err" + str(error) + " k_p=" + str(k_p) + " de" + str(_de) + " k_d=" + str(k_d) 
        #     + " ie" + str(_ie) + " k_i=" + str(k_i) + " sum" + str(sum(self._error_buffer)))
        # print("cross " + str(_cross))
        # print("loc " + str(vehicle_location) + " rot "  + str(vehicle_rotation))
        # print(" next.loc " + str(next_waypoint.location))

        # print("steer: " + str(lat_control) + " speed: " + str(current_speed) + " err" + str(error) + " k_p=" + str(k_p) + " de" + str(_de) + " k_d=" + str(k_d) 
        #     + " ie" + str(_ie) + " k_i=" + str(k_i) + " sum" + str(sum(self._error_buffer)))
        # print("   err P " + str(k_p * error) + " D " + str(k_d * _de) + " I " + str(k_i * _ie))

        return lat_control
    
    def find_k_values(self, cur_section, current_speed: float, config: dict) -> np.array:
        k_p, k_d, k_i = 1, 0, 0
        if cur_section in [8, 9, 10, 11]:
        #   return np.array([0.3, 0.1, 0.25]) # ok for mu=1.2
        #   return np.array([0.2, 0.03, 0.15])
        #   return np.array([0.3, 0.06, 0.03]) # ok for mu=1.8
        #   return np.array([0.42, 0.05, 0.02]) # ok for mu=2.0
        #   return np.array([0.45, 0.05, 0.02]) # ok for mu=2.2
          return np.array([0.58, 0.05, 0.02]) # 
        # if cur_section in [12]:
        #   return np.array([0.4, 0.05, 0.02]) # 

        for speed_upper_bound, kvalues in config.items():
            speed_upper_bound = float(speed_upper_bound)
            if current_speed < speed_upper_bound:
                k_p, k_d, k_i = kvalues["Kp"], kvalues["Kd"], kvalues["Ki"]
                break
        return np.array([k_p, k_d, k_i])

    
    def normalize_rad(rad : float):
        return (rad + np.pi) % (2 * np.pi) - np.pi

class SpeedData:
    def __init__(self, distance_to_section, current_speed, target_speed, recommended_speed):
        self.current_speed = current_speed
        self.distance_to_section = distance_to_section
        self.target_speed_at_distance = target_speed
        self.recommended_speed_now = recommended_speed
        self.speed_diff = current_speed - recommended_speed

class ThrottleController():
    # display_debug = False
    # debug_strings = deque(maxlen=1000)

    def __init__(self):
        self.max_radius = 10000
        self.max_speed = 300
        self.intended_target_distance = [0, 30, 60, 90, 120, 150, 180]
        self.target_distance = [0, 30, 60, 90, 120, 150, 180]
        self.close_index = 0
        self.mid_index = 1
        self.far_index = 2
        self.tick_counter = 0
        self.previous_speed = 1.0
        self.brake_ticks = 0

        # for testing how fast the car stops
        self.brake_test_counter = 0
        self.brake_test_in_progress = False

    # def __del__(self):
    #     print("done")
        # for s in self.__class__.debug_strings:
        #     print(s)

    def run(self, cur_wp_index, waypoints, current_location, current_speed, current_section) -> (float, float, int):
        self.tick_counter += 1
        throttle, brake = self.get_throttle_and_brake(cur_wp_index, current_location, current_speed, current_section, waypoints)
        gear = max(1, (int)(current_speed / 60))
        if throttle == -1:
            gear = -1

        # self.dprint("--- " + str(throttle) + " " + str(brake) 
        #             + " steer " + str(steering)
        #             + "     loc x,z" + str(self.agent.vehicle.transform.location.x)
        #             + " " + str(self.agent.vehicle.transform.location.z)) 

        self.previous_speed = current_speed
        if self.brake_ticks > 0 and brake > 0:
            self.brake_ticks -= 1

        # throttle = 0.05 * (100 - current_speed)
        return throttle, brake, gear

    def get_throttle_and_brake(self, cur_wp_index, current_location, current_speed, current_section, waypoints):

        wp = self.get_next_interesting_waypoints(current_location, waypoints)
        r1 = self.get_radius(wp[self.close_index : self.close_index + 3])
        r2 = self.get_radius(wp[self.mid_index : self.mid_index + 3])
        r3 = self.get_radius(wp[self.far_index : self.far_index + 3])

        target_speed1 = self.get_target_speed(r1, current_section, current_speed)
        target_speed2 = self.get_target_speed(r2, current_section, current_speed)
        target_speed3 = self.get_target_speed(r3, current_section, current_speed)

        close_distance = self.target_distance[self.close_index] + 3
        mid_distance = self.target_distance[self.mid_index]
        far_distance = self.target_distance[self.far_index]
        speed_data = []
        speed_data.append(self.speed_for_turn(close_distance, target_speed1, current_speed))
        speed_data.append(self.speed_for_turn(mid_distance, target_speed2, current_speed))
        speed_data.append(self.speed_for_turn(far_distance, target_speed3, current_speed))

        if current_speed > 100:
            # at high speed use larger spacing between points to look further ahead and detect wide turns.
            r4 = self.get_radius([wp[self.close_index], wp[self.close_index+3], wp[self.close_index+6]])
            target_speed4 = self.get_target_speed(r4, current_section, current_speed)
            speed_data.append(self.speed_for_turn(close_distance, target_speed4, current_speed))

        update = self.select_speed(speed_data)

        # self.print_speed(" -- SPEED: ", 
        #                  speed_data[0].recommended_speed_now, 
        #                  speed_data[1].recommended_speed_now, 
        #                  speed_data[2].recommended_speed_now,
        #                  (0 if len(speed_data) < 4 else speed_data[3].recommended_speed_now), 
        #                  current_speed)

        t, b = self.speed_data_to_throttle_and_brake(update)
        #self.dprint("--- (" + str(cur_wp_index) + ") throt " + str(t) + " brake " + str(b) + "---")
        return t, b

    def speed_data_to_throttle_and_brake(self, speed_data: SpeedData):
        percent_of_max = speed_data.current_speed / speed_data.recommended_speed_now

        # self.dprint("dist=" + str(round(speed_data.distance_to_section)) + " cs=" + str(round(speed_data.current_speed, 2)) 
        #             + " ts= " + str(round(speed_data.target_speed_at_distance, 2)) 
        #             + " maxs= " + str(round(speed_data.recommended_speed_now, 2)) + " pcnt= " + str(round(percent_of_max, 2)))

        percent_change_per_tick = 0.07 # speed drop for one time-tick of braking
        speed_up_threshold = 0.99
        throttle_decrease_multiple = 0.7
        throttle_increase_multiple = 1.25
        percent_speed_change = (speed_data.current_speed - self.previous_speed) / (self.previous_speed + 0.0001) # avoid division by zero

        if percent_of_max > 1:
            # Consider slowing down
            brake_threshold_multiplier = 1.0
            if speed_data.current_speed > 200:
                brake_threshold_multiplier = 1.0
            if percent_of_max > 1 + (brake_threshold_multiplier * percent_change_per_tick):
                if self.brake_ticks > 0:
                   # self.dprint("tb: tick" + str(self.tick_counter) + " brake: counter" + str(self.brake_ticks))
                    return -1, 1
                # if speed is not decreasing fast, hit the brake.
                if self.brake_ticks <= 0 and not self.speed_dropping_fast(percent_change_per_tick, speed_data.current_speed):
                    # start braking, and set for how many ticks to brake
                    self.brake_ticks = math.floor((percent_of_max - 1) / percent_change_per_tick)
                    # TODO: try 
                    # self.brake_ticks = 1, or (1 or 2 but not more)
                    #self.dprint("tb: tick" + str(self.tick_counter) + " brake: initiate counter" + str(self.brake_ticks))
                    return -1, 1
                else:
                    # speed is already dropping fast, ok to throttle because the effect of throttle is delayed
                    #self.dprint("tb: tick" + str(self.tick_counter) + " brake: throttle early1: sp_ch=" + str(percent_speed_change))
                    self.brake_ticks = 0 # done slowing down. clear brake_ticks
                    return 1, 0
            else:
                if self.speed_dropping_fast(percent_change_per_tick, speed_data.current_speed):
                    # speed is already dropping fast, ok to throttle because the effect of throttle is delayed
                    #self.dprint("tb: tick" + str(self.tick_counter) + " brake: throttle early2: sp_ch=" + str(percent_speed_change))
                    self.brake_ticks = 0 # done slowing down. clear brake_ticks
                    return 1, 0
                throttle_to_maintain = self.get_throttle_to_maintain_speed(speed_data.current_speed)
                if percent_of_max > 1.02 or percent_speed_change > (-percent_change_per_tick / 2):
                    #self.dprint("tb: tick" + str(self.tick_counter) + " brake: throttle down: sp_ch=" + str(percent_speed_change))
                    return throttle_to_maintain * throttle_decrease_multiple, 0 # coast, to slow down
                else:
                    # self.dprint("tb: tick" + str(self.tick_counter) + " brake: throttle maintain: sp_ch=" + str(percent_speed_change))
                    return throttle_to_maintain, 0
        else:
            self.brake_ticks = 0 # done slowing down. clear brake_ticks
            # Consider speeding up
            if self.speed_dropping_fast(percent_change_per_tick, speed_data.current_speed):
                # speed is dropping fast, ok to throttle because the effect of throttle is delayed
                #self.dprint("tb: tick" + str(self.tick_counter) + " throttle: full speed drop: sp_ch=" + str(percent_speed_change))
                return 1, 0
            if percent_of_max < speed_up_threshold:
                #self.dprint("tb: tick" + str(self.tick_counter) + " throttle full: p_max=" + str(percent_of_max))
                return 1, 0
            throttle_to_maintain = self.get_throttle_to_maintain_speed(speed_data.current_speed)
            if percent_of_max < 0.98 or percent_speed_change < -0.01:
               # self.dprint("tb: tick" + str(self.tick_counter) + " throttle up: sp_ch=" + str(percent_speed_change))
                return throttle_to_maintain * throttle_increase_multiple, 0 
            else:
              #
              # 
              # 
              # 
              #   self.dprint("tb: tick" + str(self.tick_counter) + " throttle maintain: sp_ch=" + str(percent_speed_change))
                return throttle_to_maintain, 0

    # used to detect when speed is dropping due to brakes applied earlier. speed delta has a steep negative slope.
    def speed_dropping_fast(self, percent_change_per_tick: float, current_speed):
        percent_speed_change = (current_speed - self.previous_speed) / (self.previous_speed + 0.0001) # avoid division by zero
        return percent_speed_change < (-percent_change_per_tick / 2)

    # find speed_data with smallest recommended speed
    def select_speed(self, speed_data: [SpeedData]):
        min_speed = 1000
        index_of_min_speed = -1
        for i, sd in enumerate(speed_data):
            if sd.recommended_speed_now < min_speed:
                min_speed = sd.recommended_speed_now
                index_of_min_speed = i

        if index_of_min_speed != -1:
            return speed_data[index_of_min_speed]
        else:
            return speed_data[0]
    
    def get_throttle_to_maintain_speed(self, current_speed: float):
        throttle = 0.6 + current_speed/1000
        return throttle

    def speed_for_turn(self, distance: float, target_speed: float, current_speed: float):
        d = (1/675) * (target_speed**2) + distance
        max_speed = math.sqrt(675 * d)
        return SpeedData(distance, current_speed, target_speed, max_speed)

    def speed_for_turn_fix_physics(self, distance: float, target_speed: float, current_speed: float):
        # fix physics
        braking_decceleration = 66.0 # try 11, 14, 56
        max_speed = math.sqrt((target_speed**2) + 2 * distance * (braking_decceleration + 9.81))
        return SpeedData(distance, current_speed, target_speed, max_speed)

    def get_next_interesting_waypoints(self, current_location, more_waypoints):
        # return a list of points with distances approximately as given 
        # in intended_target_distance[] from the current location.
        points = []
        dist = [] # for debugging
        start = roar_py_interface.RoarPyWaypoint(current_location, np.ndarray([0, 0, 0]), 0.0)
        # start = self.agent.vehicle.transform
        points.append(start)
        curr_dist = 0
        num_points = 0
        for p in more_waypoints:
            end = p
            num_points += 1
            # print("start " + str(start) + "\n- - - - -\n")
            # print("end " + str(end) +     "\n- - - - -\n")
            curr_dist += distance_p_to_p(start, end)
            # curr_dist += start.location.distance(end.location)
            if curr_dist > self.intended_target_distance[len(points)]:
<<<<<<< Updated upstream
                self.target_distance[len(points)] = curr_dist  #update target distance
                points.append(end)  #store waypoint end
                dist.append(curr_dist)  #add distance 
            start = end  #update the new start
            if len(points) >= len(self.target_distance):   #if the number of poitns is > the intended target distance, break
=======
                self.target_distance[len(points)] = curr_dist
                points.append(end)
                dist.append(curr_dist)
            start = end
            if len(points) >= len(self.target_distance):
>>>>>>> Stashed changes
                break

        #self.dprint("wp dist " +  str(dist))
        return points

    def get_radius(self, wp):
        point1 = (wp[0].location[0], wp[0].location[1])
        point2 = (wp[1].location[0], wp[1].location[1])
        point3 = (wp[2].location[0], wp[2].location[1])

        # Calculating length of all three sides
        len_side_1 = round( math.dist(point1, point2), 3)
        len_side_2 = round( math.dist(point2, point3), 3)
        len_side_3 = round( math.dist(point1, point3), 3)
        small_num = 0.01
        if len_side_1 < small_num or len_side_2 < small_num or len_side_3 < small_num:
            return self.max_radius

        # sp is semi-perimeter
        sp = (len_side_1 + len_side_2 + len_side_3) / 2

        # Calculating area using Herons formula
        area_squared = sp * (sp - len_side_1) * (sp - len_side_2) * (sp - len_side_3)
        if area_squared < small_num:
            return self.max_radius
        # Calculating curvature using Menger curvature formula
        radius = (len_side_1 * len_side_2 * len_side_3) / (4 * math.sqrt(area_squared))
        return radius
    
    def get_target_speed(self, radius: float, current_section, current_speed):
        if radius >= self.max_radius:
            return self.max_speed
        mu = 2.5
        if current_section == 0:
            mu = 2.5
            # mu = 1
        if current_section == 1:
            mu = 2.15
        if current_section == 2:
            mu = 1.92
        if current_section == 3:
            mu = 2.8
            # mu = 1
        if current_section == 4:
            mu = 3.25
        if current_section == 5:
            mu = 3.4
        if current_section == 6:
            mu = 2.7
            # mu = 1.95
        if current_section == 7:
            mu = 1.2
            # mu = 0.6
        # if current_section == 7 and current_speed<150:
        #     mu = 1.8
        if current_section == 8:
            mu = 3.9
        if current_section == 9:
            mu = 3.8
        if current_section == 10:
            mu = 3.8
        if current_section == 11:
            mu = 2.2
            # mu = 1.9
        if current_section == 12:
            mu = 1.77
        if current_section == 13:
            mu = 1.47
        target_speed = math.sqrt(mu*9.81*radius) * 3.6
        return max(20, min(target_speed, self.max_speed))  # clamp between 20 and max_speed

DOC_WAYPOINTS = [
  new_x_y(-285.0, 395.2),
  new_x_y(-285.6,396.758056640625),
  new_x_y(-285.9,398.7),
  new_x_y(-286.7, 400.5),
  new_x_y(-287.9494140625, 402.758056640625),
  new_x_y(-288.494140625, 405.758056640625),
  new_x_y(-289.493133544921, 407.9544677734375),
  new_x_y(-290.138977050781, 409.8473205566406),
  new_x_y(-290.784790039062, 411.74017333984375),
  new_x_y(-291.430633544921,413.633056640625),
  new_x_y(-292.076446533203, 415.5259094238281),
  new_x_y(-292.722290039062, 417.41876220703125),
  new_x_y(-293.368103027343, 419.3116149902344),
  new_x_y(-294.013946533203, 421.2044677734375),
  new_x_y(-294.659759521484, 423.0973205566406),
  new_x_y(-295.305603027343, 424.99017333984375),
  new_x_y(-295.951416015625,426.883056640625),
  new_x_y(-296.597259521484, 428.7759094238281),
  new_x_y(-297.243072509765, 430.66876220703125),
  new_x_y(-297.888916015625, 432.5616149902344),
  new_x_y(-298.534729003906, 434.4544677734375),
  new_x_y(-299.180572509765, 436.3473205566406),
  new_x_y(-299.826385498046, 438.24017333984375),
  new_x_y(-300.419982910156,439.97998046875),
  new_x_y(-301.065826416015, 441.8728332519531),
  new_x_y(-301.711639404296, 443.76568603515625),
  new_x_y(-302.357482910156, 445.6585388183594),
  new_x_y(-303.003295898437, 447.5513916015625),
  new_x_y(-303.649139404296, 449.44427490234375),
  new_x_y(-304.294952392578, 451.3371276855469),
  new_x_y(-304.940795898437,453.22998046875),
  new_x_y(-305.586608886718, 455.1228332519531),
  new_x_y(-306.232452392578, 457.01568603515625),
  new_x_y(-306.878265380859, 458.9085388183594),
  new_x_y(-307.524108886718, 460.8013916015625),
  new_x_y(-308.169921875, 462.6942443847656),
  new_x_y(-308.815765380859, 464.5871276855469),
  new_x_y(-309.46157836914,466.47998046875),
  new_x_y(-310.107360839843, 468.37286376953125),
  new_x_y(-310.746337890625, 470.26800537109375),
  new_x_y(-311.374267578125, 472.1669006347656),
  new_x_y(-311.991058349609, 474.06939697265625),
  new_x_y(-312.596771240234, 475.9754638671875),
  new_x_y(-313.191314697265, 477.88507080078125),
  new_x_y(-313.774688720703,479.798095703125),
  new_x_y(-314.346893310546, 481.7144775390625),
  new_x_y(-314.907897949218, 483.6341857910156),
  new_x_y(-315.45767211914,485.55712890625),
  new_x_y(-315.996215820312, 487.4832458496094),
  new_x_y(-316.523498535156, 489.4124755859375),
  new_x_y(-317.039489746093, 491.34478759765625),
  new_x_y(-317.544189453125,493.280029296875),
  new_x_y(-318.03759765625, 495.2182312011719),
  new_x_y(-318.519653320312, 497.1592712402344),
  new_x_y(-318.99038696289, 499.10308837890625),
  new_x_y(-319.449737548828, 501.0495910644531),
  new_x_y(-319.897735595703,502.998779296875),
  new_x_y(-320.334320068359, 504.9505615234375),
  new_x_y(-320.759521484375, 506.9048156738281),
  new_x_y(-321.173278808593, 508.8615417480469),
  new_x_y(-321.575622558593, 510.8206787109375),
  new_x_y(-321.966491699218, 512.7821044921875),
  new_x_y(-322.345916748046, 514.7457885742188),
  new_x_y(-322.7138671875, 516.7116088867188),
  new_x_y(-323.0703125, 518.6796264648438),
  new_x_y(-323.415252685546,520.649658203125),
  new_x_y(-323.748718261718, 522.6216430664062),
  new_x_y(-324.070617675781, 524.5955810546875),
  new_x_y(-324.38101196289,526.5712890625),
  new_x_y(-324.678466796875,528.549072265625),
  new_x_y(-324.961364746093, 530.5289916992188),
  new_x_y(-325.229675292968, 532.5109252929688),
  new_x_y(-325.4833984375, 534.4947509765625),
  new_x_y(-325.722503662109, 536.4804077148438),
  new_x_y(-325.947021484375, 538.4677124023438),
  new_x_y(-326.15689086914, 540.4566650390625),
  new_x_y(-326.352142333984, 542.4471435546875),
  new_x_y(-326.53271484375,544.43896484375),
  new_x_y(-326.698638916015, 546.4320678710938),
  new_x_y(-326.849914550781, 548.4263305664062),
  new_x_y(-326.98648071289,550.421630859375),
  new_x_y(-327.108367919921, 552.4179077148438),
  new_x_y(-327.215576171875,554.4150390625),
  new_x_y(-327.30810546875, 556.4129028320312),
  new_x_y(-327.38589477539,558.411376953125),
  new_x_y(-327.449005126953,560.410400390625),
  new_x_y(-327.497375488281, 562.4097900390625),
  new_x_y(-327.531066894531, 564.4094848632812),
  new_x_y(-327.550048828125,566.409423828125),
  new_x_y(-327.554290771484,568.409423828125),
  new_x_y(-327.543823242187, 570.4093627929688),
  new_x_y(-327.518646240234, 572.4092407226562),
  new_x_y(-327.478759765625, 574.4088134765625),
  new_x_y(-327.424133300781, 576.4080810546875),
  new_x_y(-327.354827880859, 578.4068603515625),
  new_x_y(-327.270812988281, 580.4050903320312),
  new_x_y(-327.172088623046, 582.4026489257812),
  new_x_y(-327.058685302734,584.3994140625),
  new_x_y(-326.930603027343, 586.3953247070312),
  new_x_y(-326.793182373046, 588.3905639648438),
  new_x_y(-326.655670166015, 590.3858032226562),
  new_x_y(-326.518127441406,592.381103515625),
  new_x_y(-326.380584716796, 594.3763427734375),
  new_x_y(-326.243072509765,596.37158203125),
  new_x_y(-326.105529785156, 598.3668823242188),
  new_x_y(-325.967987060546, 600.3621215820312),
  new_x_y(-325.830474853515,602.357421875),
  new_x_y(-325.691436767578, 604.3526000976562),
  new_x_y(-325.541931152343, 606.3469848632812),
  new_x_y(-325.38052368164, 608.3404541015625),
  new_x_y(-325.20718383789, 610.3329467773438),
  new_x_y(-325.02197265625, 612.3243408203125),
  new_x_y(-324.824829101562, 614.3145751953125),
  new_x_y(-324.615844726562, 616.3036499023438),
  new_x_y(-324.394927978515, 618.2913818359375),
  new_x_y(-324.162170410156,620.27783203125),
  new_x_y(-323.917541503906, 622.2628173828125),
  new_x_y(-323.661041259765, 624.2462768554688),
  new_x_y(-323.392700195312, 626.2282104492188),
  new_x_y(-323.112548828125, 628.2084350585938),
  new_x_y(-322.820526123046,630.18701171875),
  new_x_y(-322.516723632812,632.163818359375),
  new_x_y(-322.201080322265, 634.1387329101562),
  new_x_y(-321.873657226562, 636.1117553710938),
  new_x_y(-321.534454345703,638.082763671875),
  new_x_y(-321.183471679687,640.0517578125),
  new_x_y(-320.820739746093,642.0185546875),
  new_x_y(-320.446258544921, 643.9832153320312),
  new_x_y(-320.06005859375,645.945556640625),
  new_x_y(-319.662109375, 647.9055786132812),
  new_x_y(-319.252471923828, 649.8631591796875),
  new_x_y(-318.831146240234, 651.8182373046875),
  new_x_y(-318.398162841796, 653.7708129882812),
  new_x_y(-317.953491210937, 655.7207641601562),
  new_x_y(-317.497192382812, 657.6680297851562),
  new_x_y(-317.029052734375, 659.6124877929688),
  new_x_y(-316.541839599609, 661.5521850585938),
  new_x_y(-316.031799316406,663.486083984375),
  new_x_y(-315.4990234375, 665.4137573242188),
  new_x_y(-314.943603515625, 667.3350830078125),
  new_x_y(-314.365539550781, 669.2496948242188),
  new_x_y(-313.765014648437, 671.1574096679688),
  new_x_y(-313.142028808593, 673.0579223632812),
  new_x_y(-312.496673583984,674.950927734375),
  new_x_y(-311.8291015625,676.836181640625),
  new_x_y(-311.139343261718, 678.7135009765625),
  new_x_y(-310.427551269531,680.58251953125),
  new_x_y(-309.693786621093, 682.4430541992188),
  new_x_y(-308.938110351562, 684.2947998046875),
  new_x_y(-308.160705566406, 686.1375122070312),
  new_x_y(-307.361663818359,687.970947265625),
  new_x_y(-306.541076660156, 689.7947998046875),
  new_x_y(-305.699035644531,691.60888671875),
  new_x_y(-304.835693359375, 693.4129638671875),
  new_x_y(-303.951171875, 695.2067260742188),
  new_x_y(-303.045593261718, 696.9899291992188),
  new_x_y(-302.119049072265, 698.7623291015625),
  new_x_y(-301.171691894531, 700.5237426757812),
  new_x_y(-300.203674316406, 702.2738647460938),
  new_x_y(-299.215087890625,704.012451171875),
  new_x_y(-298.206085205078,705.7392578125),
  new_x_y(-297.176818847656, 707.4540405273438),
  new_x_y(-296.12744140625, 709.1566162109375),
  new_x_y(-295.058074951171,710.8466796875),
  new_x_y(-293.979766845703, 712.5310668945312),
  new_x_y(-292.901458740234, 714.2155151367188),
  new_x_y(-291.82241821289,715.8994140625),
  new_x_y(-290.737579345703, 717.5797119140625),
  new_x_y(-289.646026611328, 719.2554931640625),
  new_x_y(-288.547790527343,720.927001953125),
  new_x_y(-287.44287109375, 722.5941162109375),
  new_x_y(-286.331298828125, 724.2567138671875),
  new_x_y(-285.213073730468, 725.9149169921875),
  new_x_y(-284.088256835937,727.568603515625),
  new_x_y(-282.956787109375, 729.2178344726562),
  new_x_y(-281.818756103515, 730.8624877929688),
  new_x_y(-280.674163818359, 732.5025634765625),
  new_x_y(-279.523010253906, 734.1380615234375),
  new_x_y(-278.365325927734, 735.7689208984375),
  new_x_y(-277.201110839843, 737.3951416015625),
  new_x_y(-276.03042602539, 739.0167236328125),
  new_x_y(-274.853240966796,740.633544921875),
  new_x_y(-273.669616699218, 742.2457275390625),
  new_x_y(-272.479553222656, 743.8531494140625),
  new_x_y(-271.283050537109, 745.4557495117188),
  new_x_y(-270.080169677734, 747.0535888671875),
  new_x_y(-268.870880126953, 748.6466064453125),
  new_x_y(-267.655242919921, 750.2347412109375),
  new_x_y(-266.43325805664, 751.8179931640625),
  new_x_y(-265.204956054687, 753.3963623046875),
  new_x_y(-263.97036743164, 754.9698486328125),
  new_x_y(-262.729461669921,756.538330078125),
  new_x_y(-261.482971191406, 758.1024169921875),
  new_x_y(-260.23550415039, 759.6657104492188),
  new_x_y(-258.988067626953, 761.2289428710938),
  new_x_y(-257.740600585937,762.792236328125),
  new_x_y(-256.4931640625, 764.3555297851562),
  new_x_y(-255.245712280273, 765.9188232421875),
  new_x_y(-253.998260498046, 767.4821166992188),
  new_x_y(-252.75080871582,769.04541015625),
  new_x_y(-251.499084472656,770.605224609375),
  new_x_y(-250.235580444335, 772.1555786132812),
  new_x_y(-248.960205078125, 773.6961669921875),
  new_x_y(-247.673034667968, 775.2269287109375),
  new_x_y(-246.374160766601, 776.7477416992188),
  new_x_y(-245.063644409179,778.258544921875),
  new_x_y(-243.741561889648, 779.7592163085938),
  new_x_y(-242.407989501953,781.249755859375),
  new_x_y(-241.063018798828, 782.7299194335938),
  new_x_y(-239.706726074218, 784.1997680664062),
  new_x_y(-238.33918762207,785.6591796875),
  new_x_y(-236.960479736328, 787.1080322265625),
  new_x_y(-235.570693969726, 788.5462036132812),
  new_x_y(-234.169891357421, 789.9737548828125),
  new_x_y(-232.758193969726, 791.3904418945312),
  new_x_y(-231.335632324218, 792.7962646484375),
  new_x_y(-229.90234375, 794.1911010742188),
  new_x_y(-228.458374023437,795.574951171875),
  new_x_y(-227.003814697265, 796.9476318359375),
  new_x_y(-225.538772583007,798.30908203125),
  new_x_y(-224.06330871582, 799.6593017578125),
  new_x_y(-222.577529907226, 800.9981079101562),
  new_x_y(-221.081512451171,802.325439453125),
  new_x_y(-219.57534790039, 803.6412963867188),
  new_x_y(-218.059112548828,804.945556640625),
  new_x_y(-216.532928466796, 806.2380981445312),
  new_x_y(-214.996856689453, 807.5189208984375),
  new_x_y(-213.450988769531,808.787841796875),
  new_x_y(-211.895431518554,810.044921875),
  new_x_y(-210.330261230468,811.2900390625),
  new_x_y(-208.755584716796, 812.5230712890625),
  new_x_y(-207.171478271484, 813.7439575195312),
  new_x_y(-205.578048706054,814.95263671875),
  new_x_y(-203.975387573242, 816.1490478515625),
  new_x_y(-202.363571166992, 817.3331909179688),
  new_x_y(-200.742721557617,818.5048828125),
  new_x_y(-199.112930297851,819.6640625),
  new_x_y(-197.474288940429, 820.8106689453125),
  new_x_y(-195.826873779296, 821.9447021484375),
  new_x_y(-194.174407958984, 823.0714111328125),
  new_x_y(-192.521881103515,824.197998046875),
  new_x_y(-190.869369506835, 825.3245239257812),
  new_x_y(-189.216842651367, 826.4511108398438),
  new_x_y(-187.564331054687, 827.5776977539062),
  new_x_y(-185.911804199218, 828.7042846679688),
  new_x_y(-184.258483886718, 829.8297119140625),
  new_x_y(-182.594146728515,830.938720703125),
  new_x_y(-180.915924072265,832.026611328125),
  new_x_y(-179.224029541015, 833.0931396484375),
  new_x_y(-177.518768310546, 834.1381225585938),
  new_x_y(-175.800399780273, 835.1614379882812),
  new_x_y(-174.069213867187, 836.1629028320312),
  new_x_y(-172.325469970703,837.142333984375),
  new_x_y(-170.569458007812,838.099609375),
  new_x_y(-168.801483154296, 839.0346069335938),
  new_x_y(-167.021789550781, 839.9470825195312),
  new_x_y(-165.230682373046, 840.8369750976562),
  new_x_y(-163.428436279296,841.7041015625),
  new_x_y(-161.615356445312, 842.5482788085938),
  new_x_y(-159.791717529296, 843.3694458007812),
  new_x_y(-157.95783996582,844.16748046875),
  new_x_y(-156.113998413085, 844.9421997070312),
  new_x_y(-154.367950439453,846.057373046875),
  new_x_y(-152.55679321289, 846.9325561523438),
  new_x_y(-150.70344543457, 847.7677001953125),
  new_x_y(-148.876831054687, 848.5831909179688),
  new_x_y(-147.03807067871,849.3896484375),
  new_x_y(-145.185089111328, 850.1881103515625),
  new_x_y(-143.335479736328,850.983154296875),
  new_x_y(-141.438583374023, 851.7215576171875),
  new_x_y(-139.547088623046,852.4189453125),
  new_x_y(-137.624252319335, 853.1213989257812),
  new_x_y(-135.679443359375, 853.7489624023438),
  new_x_y(-133.767578125,854.356201171875),
  new_x_y(-131.838165283203,854.968505859375),
  new_x_y(-129.772628784179, 855.6014404296875),
  new_x_y(-127.674339294433, 856.1951293945312),
  new_x_y(-125.722526550292,856.756103515625),
  new_x_y(-123.794616699218, 857.3106079101562),
  new_x_y(-121.846405029296, 857.8703002929688),
  new_x_y(-119.861442565917, 858.4368286132812),
  new_x_y(-117.915733337402, 858.9888305664062),
  new_x_y(-115.961502075195, 859.5438232421875),
  new_x_y(-113.989463806152, 860.1044311523438),
  new_x_y(-112.032890319824,860.659423828125),
  new_x_y(-110.069412231445,861.21630859375),
  new_x_y(-108.09536743164, 861.7774047851562),
  new_x_y(-106.087867736816, 862.3458251953125),
  new_x_y(-104.087516784667, 862.8329467773438),
  new_x_y(-102.114852905273,863.329833984375),
  new_x_y(-100.109100341796,863.835693359375),
  new_x_y(-98.1087875366211,864.339111328125),
  new_x_y(-96.1285934448242,864.83740234375),
  new_x_y(-94.1058959960937,865.25390625),
  new_x_y(-92.1097412109375,865.667236328125),
  new_x_y(-90.1331787109375, 866.0759887695312),
  new_x_y(-88.0953216552734, 866.4987182617188),
  new_x_y(-86.106460571289, 866.9581298828125),
  new_x_y(-84.1097412109375,867.43359375),
  new_x_y(-82.1314315795898, 867.9024047851562),
  new_x_y(-80.1045455932617, 868.3023071289062),
  new_x_y(-78.0959701538086, 868.7196044921875),
  new_x_y(-76.1387176513671, 869.1990356445312),
  new_x_y(-74.1393356323242, 869.6703491210938),
  new_x_y(-72.1468658447265, 870.1027221679688),
  new_x_y(-70.1634216308593, 870.5419311523438),
  new_x_y(-68.1628341674804, 870.9840698242188),
  new_x_y(-66.1786651611328, 871.4223022460938),
  new_x_y(-64.2076721191406, 871.8572998046875),
  new_x_y(-62.1918334960937, 872.3031005859375),
  new_x_y(-60.1986274719238, 872.7432861328125),
  new_x_y(-58.2325553894043, 873.1782836914062),
  new_x_y(-56.2407112121582,873.618408203125),
  new_x_y(-54.2263793945312, 874.0639038085938),
  new_x_y(-52.241340637207, 874.5026245117188),
  new_x_y(-50.2482185363769, 874.9442138671875),
  new_x_y(-48.215648651123,875.392822265625),
  new_x_y(-46.2180938720703, 875.8348388671875),
  new_x_y(-44.2216987609863, 876.2759399414062),
  new_x_y(-42.1874504089355, 876.7252807617188),
  new_x_y(-40.1757774353027,877.169677734375),
  new_x_y(-38.1687088012695, 877.6128540039062),
  new_x_y(-36.1597366333007, 878.0563354492188),
  new_x_y(-34.1289634704589, 878.5047607421875),
  new_x_y(-32.1066360473632,878.952880859375),
  new_x_y(-30.0864868164062, 879.3995971679688),
  new_x_y(-28.0420932769775, 879.8510131835938),
  new_x_y(-25.9999675750732, 880.3024291992188),
  new_x_y(-23.9594917297363, 880.7537841796875),
  new_x_y(-21.8921184539794, 881.1619873046875),
  new_x_y(-19.8402843475341, 881.5512084960938),
  new_x_y(-17.7924423217773, 881.9407348632812),
  new_x_y(-15.7233247756958, 882.3345336914062),
  new_x_y(-13.6619310379028,882.727294921875),
  new_x_y(-11.6208581924438, 883.1163940429688),
  new_x_y(-9.57780933380127, 883.5059204101562),
  new_x_y(-7.52943992614746, 883.8958129882812),
  new_x_y(-5.47676134109497, 884.2868041992188),
  new_x_y(-3.43150901794433,884.6767578125),
  new_x_y(-1.37877571582794,884.9990234375),
  new_x_y(0.6551559567451477, 885.3225708007812),
  new_x_y(2.6909375190734863,885.646484375),
  new_x_y(4.768572807312012, 885.9769287109375),
  new_x_y(6.819311141967773, 886.3031616210938),
  new_x_y(8.851128578186035, 886.6261596679688),
  new_x_y(10.952326774597168, 886.9524536132812),
  new_x_y(13.005718231201172,887.271728515625),
  new_x_y(15.052348136901855,887.508544921875),
  new_x_y(17.09379768371582, 887.7367553710938),
  new_x_y(19.140380859375, 887.9671630859375),
  new_x_y(21.152267456054688,888.193603515625),
  new_x_y(23.175113677978516,888.4609375),
  new_x_y(25.21249771118164,888.751220703125),
  new_x_y(27.22637367248535, 889.0358276367188),
  new_x_y(29.2480411529541,889.3212890625),
  new_x_y(31.306772232055664, 889.6118774414062),
  new_x_y(33.31977081298828, 889.8853149414062),
  new_x_y(35.34669494628906, 890.1417236328125),
  new_x_y(37.383201599121094, 890.4027709960938),
  new_x_y(39.406494140625,890.631103515625),
  new_x_y(41.43008804321289, 890.8630981445312),
  new_x_y(43.449344635009766, 891.0764770507812),
  new_x_y(45.5091552734375,891.288330078125),
  new_x_y(47.542938232421875, 891.4973754882812),
  new_x_y(49.56647491455078, 891.7055053710938),
  new_x_y(51.62203598022461, 891.9166259765625),
  new_x_y(53.65696334838867, 892.1266479492188),
  new_x_y(55.68870162963867,892.334716796875),
  new_x_y(57.75621032714844, 892.5472412109375),
  new_x_y(59.80052185058594, 892.7576904296875),
  new_x_y(61.83844757080078,892.966796875),
  new_x_y(63.88750457763672,893.17724609375),
  new_x_y(66.03363800048828,893.397216796875),
  new_x_y(68.09015655517578, 893.5742797851562),
  new_x_y(70.14085388183594, 893.7584838867188),
  new_x_y(72.21057891845703, 893.9450073242188),
  new_x_y(74.23670196533203, 894.1272583007812),
  new_x_y(76.30012512207031, 894.3133544921875),
  new_x_y(78.36811065673828,894.498779296875),
  new_x_y(80.4090347290039, 894.6820678710938),
  new_x_y(82.47021484375, 894.8667602539062),
  new_x_y(84.5287857055664, 895.0514526367188),
  new_x_y(86.59842681884766, 895.2374877929688),
  new_x_y(88.65918731689453,895.422607421875),
  new_x_y(90.73540496826172, 895.6096801757812),
  new_x_y(92.8222427368164, 895.7975463867188),
  new_x_y(94.88494110107422, 895.9780883789062),
  new_x_y(96.94379425048828, 896.1558227539062),
  new_x_y(99.0518569946289, 896.3374633789062),
  new_x_y(101.16486358642578, 896.5202026367188),
  new_x_y(103.25045013427734,896.7001953125),
  new_x_y(105.3270492553711, 896.8787841796875),
  new_x_y(107.39311981201172, 897.0569458007812),
  new_x_y(109.43415069580078, 897.2980346679688),
  new_x_y(111.48505401611328, 897.5369873046875),
  new_x_y(113.56121826171875, 897.7686767578125),
  new_x_y(115.57569122314453, 897.9718627929688),
  new_x_y(117.64411163330078, 898.1856079101562),
  new_x_y(119.71046447753906,898.3984375),
  new_x_y(121.75749969482422,898.60888671875),
  new_x_y(123.7805404663086, 898.8175048828125),
  new_x_y(125.84166717529297, 899.0296020507812),
  new_x_y(127.8831787109375, 899.2391357421875),
  new_x_y(129.91355895996094,899.447265625),
  new_x_y(131.96983337402344, 899.6586303710938),
  new_x_y(134.02664184570312, 899.8472290039062),
  new_x_y(136.06422424316406, 900.0293579101562),
  new_x_y(138.10646057128906, 900.2003173828125),
  new_x_y(140.15354919433594, 900.3108520507812),
  new_x_y(142.194091796875, 900.4359741210938),
  new_x_y(144.2500457763672, 900.5611572265625),
  new_x_y(146.3067169189453, 900.6873168945312),
  new_x_y(148.31723022460938, 900.8815307617188),
  new_x_y(150.36607360839844, 901.0647583007812),
  new_x_y(152.4544219970703, 901.2508544921875),
  new_x_y(154.4845428466797, 901.4322509765625),
  new_x_y(156.53749084472656, 901.6155395507812),
  new_x_y(158.59957885742188, 901.8002319335938),
  new_x_y(160.70826721191406,901.988037109375),
  new_x_y(162.77243041992188, 902.1731567382812),
  new_x_y(164.83778381347656,902.357421875),
  new_x_y(166.93478393554688,902.5439453125),
  new_x_y(168.99411010742188, 902.7282104492188),
  new_x_y(171.06224060058594,902.912841796875),
  new_x_y(173.15652465820312,903.098876953125),
  new_x_y(175.2406005859375, 903.2854614257812),
  new_x_y(177.31634521484375, 903.4715576171875),
  new_x_y(179.3948974609375, 903.6566772460938),
  new_x_y(181.45333862304688, 903.8409423828125),
  new_x_y(183.51150512695312,904.024658203125),
  new_x_y(185.58314514160156, 904.2107543945312),
  new_x_y(187.66824340820312, 904.3971557617188),
  new_x_y(189.7214813232422, 904.5804443359375),
  new_x_y(191.79025268554688,904.765625),
  new_x_y(193.89498901367188, 904.9530029296875),
  new_x_y(195.96109008789062,905.1376953125),
  new_x_y(198.01527404785156,905.320556640625),
  new_x_y(200.11485290527344, 905.5079345703125),
  new_x_y(202.16903686523438, 905.6912231445312),
  new_x_y(204.2289581298828, 905.8754272460938),
  new_x_y(206.29896545410156, 906.0601196289062),
  new_x_y(208.37692260742188, 906.2457885742188),
  new_x_y(210.42477416992188, 906.4281005859375),
  new_x_y(212.47146606445312, 906.6109008789062),
  new_x_y(214.60096740722656,906.72412109375),
  new_x_y(216.66427612304688,906.814208984375),
  new_x_y(218.69488525390625,906.905029296875),
  new_x_y(220.74569702148438, 906.9963989257812),
  new_x_y(222.7841796875,907.09912109375),
  new_x_y(224.8072052001953, 907.3267211914062),
  new_x_y(226.85801696777344,907.53076171875),
  new_x_y(228.88645935058594, 907.7318725585938),
  new_x_y(230.90478515625, 907.9320068359375),
  new_x_y(232.9270782470703, 908.1321411132812),
  new_x_y(234.9722442626953,908.334716796875),
  new_x_y(237.0029296875, 908.5358276367188),
  new_x_y(239.03378295898438, 908.7378540039062),
  new_x_y(241.09353637695312, 908.9423217773438),
  new_x_y(243.1121826171875, 909.1424560546875),
  new_x_y(245.1516571044922,909.344482421875),
  new_x_y(247.22909545898438, 909.5241088867188),
  new_x_y(249.25840759277344, 909.6548461914062),
  new_x_y(251.3125457763672, 909.7962036132812),
  new_x_y(253.35560607910156, 909.9359130859375),
  new_x_y(255.4447784423828, 910.0792236328125),
  new_x_y(257.47869873046875, 910.2188720703125),
  new_x_y(259.53973388671875, 910.3604736328125),
  new_x_y(261.6141357421875, 910.5031127929688),
  new_x_y(263.6501770019531, 910.6432495117188),
  new_x_y(265.69793701171875, 910.7942504882812),
  new_x_y(267.78594970703125, 910.9456787109375),
  new_x_y(269.8420104980469,911.140869140625),
  new_x_y(271.8592224121094, 911.3466186523438),
  new_x_y(273.8828430175781, 911.5508422851562),
  new_x_y(275.9330749511719, 911.7582397460938),
  new_x_y(277.9701843261719, 911.9645385742188),
  new_x_y(280.00048828125, 912.1693725585938),
  new_x_y(282.0760803222656, 912.3792114257812),
  new_x_y(284.1090087890625, 912.5840454101562),
  new_x_y(286.1311950683594,912.789794921875),
  new_x_y(288.1921081542969, 912.9985961914062),
  new_x_y(290.2184143066406,913.204345703125),
  new_x_y(292.23944091796875, 913.4135131835938),
  new_x_y(294.2854309082031, 913.6978759765625),
  new_x_y(296.32049560546875,913.963623046875),
  new_x_y(298.34033203125, 914.2282104492188),
  new_x_y(300.35986328125, 914.5670776367188),
  new_x_y(302.39361572265625,914.893310546875),
  new_x_y(304.4005126953125, 915.2149047851562),
  new_x_y(306.41229248046875, 915.5369873046875),
  new_x_y(308.4471435546875, 915.8638305664062),
  new_x_y(310.4346618652344, 916.2388916015625),
  new_x_y(312.4259948730469, 916.6160888671875),
  new_x_y(314.45330810546875, 916.9998168945312),
  new_x_y(316.4488220214844,917.376708984375),
  new_x_y(318.43701171875, 917.7531127929688),
  new_x_y(320.4090270996094, 918.1710815429688),
  new_x_y(322.3974609375,918.60546875),
  new_x_y(324.38427734375,919.038330078125),
  new_x_y(326.32696533203125,919.53515625),
  new_x_y(328.265380859375,920.089599609375),
  new_x_y(330.2064514160156,920.68505859375),
  new_x_y(332.12152099609375,921.335205078125),
  new_x_y(334.0133972167969, 922.1041259765625),
  new_x_y(335.8881530761719, 923.1626586914062),
  new_x_y(337.70257568359375, 924.3040161132812),
  new_x_y(339.39117431640625, 925.3854370117188),
  new_x_y(341.1343688964844,926.63232421875),
  new_x_y(342.74029541015625, 928.0257568359375),
  new_x_y(344.21875, 929.5775756835938),
  new_x_y(345.6282653808594, 931.1237182617188),
  new_x_y(346.9608154296875,932.741943359375),
  new_x_y(348.2108154296875,934.452392578125),
  new_x_y(349.3708801269531, 936.1747436523438),
  new_x_y(350.4872619628906, 938.0270385742188),
  new_x_y(351.3484375, 939.9030151367188),
  new_x_y(352.1280090332031, 941.8198852539062),
  new_x_y(352.60736083984375, 943.7799072265625),
  new_x_y(353.03924560546875, 945.7901611328125),
  new_x_y(353.4901794433594,948.256591796875),
  new_x_y(353.7815612792969, 950.2350463867188),
  new_x_y(354.2011389160156, 952.1985473632812),
  new_x_y(354.7281494140625,954.14306640625),
  new_x_y(355.28167724609375, 956.0647583007812),
  new_x_y(355.9206237792969, 957.9597778320312),
  new_x_y(356.6436767578125, 959.8243408203125),
  new_x_y(357.44940185546875, 961.6546630859375),
  new_x_y(358.3362121582031, 963.4471435546875),
  new_x_y(359.3022766113281, 965.1981811523438),
  new_x_y(360.345703125, 966.9041748046875),
  new_x_y(361.46441650390625, 968.5618286132812),
  new_x_y(362.6561279296875, 970.1678466796875),
  new_x_y(363.91851806640625, 971.7188720703125),
  new_x_y(365.2489929199219,973.2119140625),
  new_x_y(366.6449279785156, 974.6439208984375),
  new_x_y(368.103515625, 976.0120849609375),
  new_x_y(369.621826171875, 977.3136596679688),
  new_x_y(371.19683837890625, 978.5459594726562),
  new_x_y(372.8254089355469, 979.7066040039062),
  new_x_y(374.5042724609375, 980.7932739257812),
  new_x_y(376.23004150390625,981.8037109375),
  new_x_y(377.9992980957031, 982.7359619140625),
  new_x_y(379.8084716796875, 983.5881958007812),
  new_x_y(381.6539306640625, 984.3585815429688),
  new_x_y(383.52581787109375, 985.0628051757812),
  new_x_y(385.3998107910156, 985.7615356445312),
  new_x_y(387.2738037109375,986.460205078125),
  new_x_y(389.1477966308594, 987.1588745117188),
  new_x_y(391.02178955078125, 987.8576049804688),
  new_x_y(392.8957824707031, 988.5562744140625),
  new_x_y(394.769775390625, 989.2549438476562),
  new_x_y(396.6437683105469, 989.9536743164062),
  new_x_y(398.5177307128906,990.65234375),
  new_x_y(400.3917236328125, 991.3510131835938),
  new_x_y(402.2657165527344, 992.0497436523438),
  new_x_y(404.13970947265625, 992.7484130859375),
  new_x_y(406.0137023925781, 993.4470825195312),
  new_x_y(407.8876953125,994.145751953125),
  new_x_y(409.7616882324219,994.844482421875),
  new_x_y(411.63568115234375, 995.5431518554688),
  new_x_y(413.5096435546875, 996.2418212890625),
  new_x_y(415.3836364746094, 996.9405517578125),
  new_x_y(417.25762939453125, 997.6392211914062),
  new_x_y(419.13214111328125, 998.3365478515625),
  new_x_y(421.00885009765625, 999.0278930664062),
  new_x_y(422.8858642578125, 999.7183837890625),
  new_x_y(424.7629089355469, 1000.4088134765625),
  new_x_y(426.63995361328125, 1001.0993041992188),
  new_x_y(428.5169677734375, 1001.789794921875),
  new_x_y(430.3940124511719, 1002.480224609375),
  new_x_y(432.27105712890625, 1003.1707153320312),
  new_x_y(434.1480712890625, 1003.8611450195312),
  new_x_y(436.0251159667969, 1004.5516357421875),
  new_x_y(437.90216064453125, 1005.2420654296875),
  new_x_y(439.7791748046875, 1005.9325561523438),
  new_x_y(441.6562194824219, 1006.6229858398438),
  new_x_y(443.53326416015625,1007.3134765625),
  new_x_y(445.4102783203125, 1008.0039672851562),
  new_x_y(447.2873229980469, 1008.6943969726562),
  new_x_y(449.16436767578125, 1009.3848876953125),
  new_x_y(451.0413818359375, 1010.0753173828125),
  new_x_y(452.9184265136719, 1010.7658081054688),
  new_x_y(454.79547119140625, 1011.4562377929688),
  new_x_y(456.6724853515625, 1012.146728515625),
  new_x_y(458.5495300292969, 1012.837158203125),
  new_x_y(460.42657470703125, 1013.5276489257812),
  new_x_y(462.3035888671875, 1014.2181396484375),
  new_x_y(464.1806335449219, 1014.9085693359375),
  new_x_y(466.05767822265625, 1015.5990600585938),
  new_x_y(467.9347229003906, 1016.2894897460938),
  new_x_y(469.8117370605469,1016.97998046875),
  new_x_y(471.68878173828125,1017.67041015625),
  new_x_y(473.5658264160156, 1018.3609008789062),
  new_x_y(475.4428405761719, 1019.0513916015625),
  new_x_y(477.31988525390625, 1019.7418212890625),
  new_x_y(479.1969299316406, 1020.432373046875),
  new_x_y(481.0739440917969, 1021.122802734375),
  new_x_y(482.95098876953125, 1021.813232421875),
  new_x_y(484.8280334472656, 1022.503662109375),
  new_x_y(486.7050476074219, 1023.1942138671875),
  new_x_y(488.58209228515625, 1023.8846435546875),
  new_x_y(490.4591369628906, 1024.5750732421875),
  new_x_y(492.3361511230469, 1025.2655029296875),
  new_x_y(494.21319580078125,1025.9560546875),
  new_x_y(496.0902404785156,1026.646484375),
  new_x_y(497.96728515625,1027.3369140625),
  new_x_y(499.84429931640625,1028.02734375),
  new_x_y(501.7213439941406, 1028.7178955078125),
  new_x_y(503.598388671875, 1029.4083251953125),
  new_x_y(505.47540283203125, 1030.0987548828125),
  new_x_y(507.3524475097656, 1030.789306640625),
  new_x_y(509.2294921875, 1031.479736328125),
  new_x_y(511.10650634765625, 1032.170166015625),
  new_x_y(512.9835205078125, 1032.860595703125),
  new_x_y(514.860595703125, 1033.5511474609375),
  new_x_y(516.7376098632812, 1034.2415771484375),
  new_x_y(518.6146240234375, 1034.9320068359375),
  new_x_y(520.49169921875, 1035.6224365234375),
  new_x_y(522.3687133789062,1036.31298828125),
  new_x_y(524.2457275390625,1037.00341796875),
  new_x_y(526.122802734375,1037.69384765625),
  new_x_y(527.9998168945312, 1038.3843994140625),
  new_x_y(529.8768310546875, 1039.0748291015625),
  new_x_y(531.75390625, 1039.7652587890625),
  new_x_y(533.6309204101562, 1040.4556884765625),
  new_x_y(535.5079345703125, 1041.146240234375),
  new_x_y(537.385009765625, 1041.836669921875),
  new_x_y(539.2620239257812, 1042.527099609375),
  new_x_y(541.1390380859375, 1043.2176513671875),
  new_x_y(543.01611328125, 1043.9080810546875),
  new_x_y(544.8931274414062, 1044.5985107421875),
  new_x_y(546.7701416015625, 1045.2889404296875),
  new_x_y(548.647216796875,1045.9794921875),
  new_x_y(550.5242309570312,1046.669921875),
  new_x_y(552.4012451171875,1047.3603515625),
  new_x_y(554.2783203125,1048.05078125),
  new_x_y(556.1553344726562, 1048.7413330078125),
  new_x_y(558.0323486328125, 1049.4317626953125),
  new_x_y(559.909423828125, 1050.1221923828125),
  new_x_y(561.7864379882812, 1050.812744140625),
  new_x_y(563.6634521484375, 1051.503173828125),
  new_x_y(565.54052734375, 1052.193603515625),
  new_x_y(567.4175415039062, 1052.884033203125),
  new_x_y(569.2945556640625, 1053.5745849609375),
  new_x_y(571.171630859375, 1054.2650146484375),
  new_x_y(573.0486450195312, 1054.9554443359375),
  new_x_y(574.9256591796875,1055.64599609375),
  new_x_y(576.802734375,1056.33642578125),
  new_x_y(578.6797485351562,1057.02685546875),
  new_x_y(580.5567626953125,1057.71728515625),
  new_x_y(582.4338989257812, 1058.4075927734375),
  new_x_y(584.3129272460938, 1059.0926513671875),
  new_x_y(586.1946411132812, 1059.770263671875),
  new_x_y(588.0791015625, 1060.440185546875),
  new_x_y(589.9661865234375, 1061.1026611328125),
  new_x_y(591.85595703125, 1061.757568359375),
  new_x_y(593.748291015625,1062.40478515625),
  new_x_y(595.6431884765625, 1063.0445556640625),
  new_x_y(597.5406494140625,1063.6767578125),
  new_x_y(599.440673828125,1064.30126953125),
  new_x_y(601.3430786132812, 1064.9183349609375),
  new_x_y(603.248046875, 1065.527587890625),
  new_x_y(605.1553344726562,1066.12939453125),
  new_x_y(607.0650634765625, 1066.7235107421875),
  new_x_y(608.9771728515625, 1067.3099365234375),
  new_x_y(610.8916015625,1067.888671875),
  new_x_y(612.8082885742188, 1068.4598388671875),
  new_x_y(614.727294921875, 1069.0233154296875),
  new_x_y(616.6484985351562,1069.5791015625),
  new_x_y(618.5718994140625, 1070.127197265625),
  new_x_y(620.49755859375, 1070.6676025390625),
  new_x_y(622.42529296875, 1071.2003173828125),
  new_x_y(624.3551635742188, 1071.7252197265625),
  new_x_y(626.287109375, 1072.242431640625),
  new_x_y(628.2211303710938,1072.751953125),
  new_x_y(630.1571655273438, 1073.2537841796875),
  new_x_y(632.0951538085938, 1073.747802734375),
  new_x_y(634.03515625, 1074.234130859375),
  new_x_y(635.97705078125, 1074.712646484375),
  new_x_y(637.9208984375, 1075.183349609375),
  new_x_y(639.8665771484375, 1075.646240234375),
  new_x_y(641.8140869140625, 1076.1014404296875),
  new_x_y(643.7633666992188,1076.548828125),
  new_x_y(645.7144775390625, 1076.9884033203125),
  new_x_y(647.6672973632812, 1077.420166015625),
  new_x_y(649.6217651367188,1077.8447265625),
  new_x_y(651.5765380859375,1078.267578125),
  new_x_y(653.533203125, 1078.6815185546875),
  new_x_y(655.50146484375, 1079.035888671875),
  new_x_y(657.6668090820312,1079.166015625),
  new_x_y(659.6688232421875, 1079.5289306640625),
  new_x_y(661.8072509765625,1079.91650390625),
  new_x_y(663.9493408203125, 1080.1993408203125),
  new_x_y(666.109130859375, 1080.414794921875),
  new_x_y(668.242431640625, 1080.5736083984375),
  new_x_y(670.3635864257812, 1080.6585693359375),
  new_x_y(672.40185546875, 1080.6839599609375),
  new_x_y(674.5316162109375, 1080.6422119140625),
  new_x_y(676.6309204101562,1080.5),
  new_x_y(678.7628784179688, 1080.2989501953125),
  new_x_y(680.8408203125, 1080.035888671875),
  new_x_y(682.8848876953125, 1079.6641845703125),
  new_x_y(684.9441528320312,1079.21435546875),
  new_x_y(686.9503173828125,1078.70947265625),
  new_x_y(688.9417114257812, 1078.0906982421875),
  new_x_y(690.902099609375,1077.41748046875),
  new_x_y(692.8579711914062, 1076.7139892578125),
  new_x_y(694.7534790039062,1075.9326171875),
  new_x_y(696.6484375, 1075.0543212890625),
  new_x_y(698.4599609375,1074.134765625),
  new_x_y(700.28076171875, 1073.1539306640625),
  new_x_y(702.104736328125, 1072.1549072265625),
  new_x_y(703.907470703125,1071.126953125),
  new_x_y(705.6593627929688, 1070.0303955078125),
  new_x_y(707.3565673828125, 1068.843505859375),
  new_x_y(708.9691772460938, 1067.5904541015625),
  new_x_y(710.5309448242188,1066.2861328125),
  new_x_y(712.048095703125, 1064.8817138671875),
  new_x_y(713.4571533203125, 1063.432373046875),
  new_x_y(714.8348999023438, 1061.9320068359375),
  new_x_y(716.2431030273438, 1060.427978515625),
  new_x_y(717.6368408203125, 1058.8948974609375),
  new_x_y(718.9954223632812, 1057.3594970703125),
  new_x_y(720.3859252929688, 1055.7943115234375),
  new_x_y(721.7715454101562, 1054.2342529296875),
  new_x_y(723.1630249023438, 1052.6617431640625),
  new_x_y(724.4800415039062,1050.990234375),
  new_x_y(725.6632080078125, 1049.2928466796875),
  new_x_y(726.6638793945312, 1047.4781494140625),
  new_x_y(727.6619873046875,1045.634765625),
  new_x_y(728.5922241210938, 1043.7821044921875),
  new_x_y(729.541259765625, 1041.9195556640625),
  new_x_y(730.4794311523438,1040.025390625),
  new_x_y(731.3046875,1038.1162109375),
  new_x_y(732.1298828125, 1036.2003173828125),
  new_x_y(732.9694213867188, 1034.256591796875),
  new_x_y(733.7667846679688,1032.314453125),
  new_x_y(734.5419921875, 1030.3682861328125),
  new_x_y(735.232421875, 1028.3651123046875),
  new_x_y(735.8409423828125,1026.36962890625),
  new_x_y(736.3995361328125, 1024.3211669921875),
  new_x_y(736.9556274414062, 1022.2462768554688),
  new_x_y(737.50732421875, 1020.1935424804688),
  new_x_y(738.061767578125, 1018.1292114257812),
  new_x_y(738.5880126953125,1016.0263671875),
  new_x_y(739.048828125,1013.9462890625),
  new_x_y(739.4263916015625, 1011.8434448242188),
  new_x_y(739.8131713867188,1009.7236328125),
  new_x_y(740.2349243164062, 1007.6287841796875),
  new_x_y(740.6785888671875, 1005.5433959960938),
  new_x_y(741.12646484375, 1003.4244995117188),
  new_x_y(741.5186767578125, 1001.322021484375),
  new_x_y(741.8797607421875, 999.3385620117188),
  new_x_y(742.2467651367188, 997.3274536132812),
  new_x_y(742.6082153320312, 995.3466186523438),
  new_x_y(742.9824829101562,993.374755859375),
  new_x_y(743.3729248046875, 991.3908081054688),
  new_x_y(743.7640991210938, 989.3895263671875),
  new_x_y(744.1550903320312, 987.3921508789062),
  new_x_y(744.5455322265625, 985.3910522460938),
  new_x_y(744.9406127929688, 983.3677368164062),
  new_x_y(745.338134765625,981.335205078125),
  new_x_y(745.72998046875, 979.3298950195312),
  new_x_y(746.1295776367188, 977.2844848632812),
  new_x_y(746.5233154296875, 975.2726440429688),
  new_x_y(746.94921875, 973.2760620117188),
  new_x_y(747.3781127929688, 971.2308959960938),
  new_x_y(747.7463989257812,969.223876953125),
  new_x_y(748.0814819335938, 967.1878662109375),
  new_x_y(748.4231567382812, 965.1488647460938),
  new_x_y(748.7644653320312, 963.1107788085938),
  new_x_y(749.1061401367188,961.072265625),
  new_x_y(749.3955078125, 959.0240478515625),
  new_x_y(749.654296875, 956.9144897460938),
  new_x_y(749.90966796875, 954.8754272460938),
  new_x_y(750.1660766601562, 952.8292236328125),
  new_x_y(750.4258422851562, 950.7594604492188),
  new_x_y(750.6841430664062, 948.6983642578125),
  new_x_y(750.9423828125, 946.6423950195312),
  new_x_y(751.1992797851562,944.593505859375),
  new_x_y(751.4561767578125,942.5478515625),
  new_x_y(751.7679443359375,940.518310546875),
  new_x_y(752.0833129882812,938.475341796875),
  new_x_y(752.3961791992188,936.44287109375),
  new_x_y(752.6439819335938, 934.4044189453125),
  new_x_y(752.8971557617188, 932.3667602539062),
  new_x_y(753.154296875, 930.3036499023438),
  new_x_y(753.4074096679688, 928.2691040039062),
  new_x_y(753.6610107421875, 926.2272338867188),
  new_x_y(753.9169921875, 924.1639404296875),
  new_x_y(754.170166015625, 922.1267700195312),
  new_x_y(754.427001953125, 920.0614624023438),
  new_x_y(754.6843872070312,917.990966796875),
  new_x_y(754.9398193359375, 915.9341430664062),
  new_x_y(755.1957397460938, 913.8809814453125),
  new_x_y(755.4555053710938, 911.7857666015625),
  new_x_y(755.7114868164062,909.72607421875),
  new_x_y(755.97021484375, 907.6415405273438),
  new_x_y(756.2266235351562, 905.5753173828125),
  new_x_y(756.4866333007812,903.478271484375),
  new_x_y(756.7470703125,901.384033203125),
  new_x_y(757.00537109375, 899.3070068359375),
  new_x_y(757.267333984375, 897.1970825195312),
  new_x_y(757.525634765625,895.113525390625),
  new_x_y(757.783447265625, 893.0346069335938),
  new_x_y(758.0425415039062, 890.9484252929688),
  new_x_y(758.2999267578125, 888.8775024414062),
  new_x_y(758.5154418945312,886.81201171875),
  new_x_y(758.7112426757812, 884.7130126953125),
  new_x_y(758.923095703125,882.629638671875),
  new_x_y(759.1497192382812,880.5576171875),
  new_x_y(759.3719482421875, 878.4965209960938),
  new_x_y(759.5983276367188, 876.4009399414062),
  new_x_y(759.820068359375,874.344970703125),
  new_x_y(760.0441284179688, 872.2733154296875),
  new_x_y(760.2662963867188, 870.2098999023438),
  new_x_y(760.4927368164062, 868.1192626953125),
  new_x_y(760.716796875, 866.0520629882812),
  new_x_y(760.9423217773438,863.96435546875),
  new_x_y(761.1677856445312,861.871826171875),
  new_x_y(761.3909301757812,859.810302734375),
  new_x_y(761.6163940429688, 857.7262573242188),
  new_x_y(761.8413696289062, 855.6412353515625),
  new_x_y(762.0654296875, 853.5679321289062),
  new_x_y(762.2880859375,851.50341796875),
  new_x_y(762.5121459960938, 849.4232788085938),
  new_x_y(762.734375, 847.3678588867188),
  new_x_y(762.9574584960938, 845.3016357421875),
  new_x_y(763.1831665039062,843.20849609375),
  new_x_y(763.4072265625, 841.1375732421875),
  new_x_y(763.6298828125,839.0712890625),
  new_x_y(763.8572387695312, 836.9671020507812),
  new_x_y(764.082275390625,834.87646484375),
  new_x_y(764.3053588867188,832.807373046875),
  new_x_y(764.5280151367188, 830.7425537109375),
  new_x_y(764.7777099609375, 828.6817626953125),
  new_x_y(765.0321655273438, 826.6013793945312),
  new_x_y(765.2838745117188,824.540771484375),
  new_x_y(765.5407104492188, 822.4385986328125),
  new_x_y(765.7942504882812, 820.3526611328125),
  new_x_y(766.0506591796875, 818.2498168945312),
  new_x_y(766.3094482421875, 816.1253662109375),
  new_x_y(766.564453125, 814.0296020507812),
  new_x_y(766.8189697265625, 811.9459838867188),
  new_x_y(767.0789794921875,809.818603515625),
  new_x_y(767.335693359375, 807.7141723632812),
  new_x_y(767.5804443359375, 805.6196899414062),
  new_x_y(767.8053588867188, 803.5131225585938),
  new_x_y(768.0336303710938, 801.4115600585938),
  new_x_y(768.261962890625, 799.3143310546875),
  new_x_y(768.4946899414062, 797.1687622070312),
  new_x_y(768.725830078125, 795.0407104492188),
  new_x_y(768.9531860351562, 792.9506225585938),
  new_x_y(769.1795654296875,790.857666015625),
  new_x_y(769.4074096679688,788.75390625),
  new_x_y(769.6292724609375, 786.6708374023438),
  new_x_y(769.8209228515625, 784.5796508789062),
  new_x_y(770.0220336914062, 782.4585571289062),
  new_x_y(770.42216796875,780.36279296875),
  new_x_y(770.821875, 778.2628173828125),
  new_x_y(771.12060546875,776.18505859375),
  new_x_y(771.5175048828125,774.116455078125),
  new_x_y(771.9143432617188, 772.0446166992188),
  new_x_y(772.2096557617188, 769.9835205078125),
  new_x_y(772.3975463867188, 767.9135131835938),
  new_x_y(772.5691040039062, 765.8651123046875),
  new_x_y(772.5639770507812, 763.7862548828125),
  new_x_y(772.5587280273438, 761.6884155273438),
  new_x_y(772.449267578125, 759.6234130859375),
  new_x_y(772.211181640625, 757.5516357421875),
  new_x_y(771.9968017578125, 755.4833374023438),
  new_x_y(771.5131713867188,753.44873046875),
  new_x_y(771.0473876953125,751.4130859375),
  new_x_y(770.4400390625, 749.3793334960938),
  new_x_y(769.5944458007812, 747.3814086914062),
  new_x_y(768.8312377929688,745.451171875),
  new_x_y(768.0853881835938,743.5703125),
  new_x_y(767.2445068359375, 741.7239379882812),
  new_x_y(766.2857055664062, 739.9307861328125),
  new_x_y(765.1336059570312, 738.2741088867188),
  new_x_y(763.9116821289062,736.6513671875),
  new_x_y(762.6016235351562, 735.1362915039062),
  new_x_y(761.2134399414062,733.685546875),
  new_x_y(759.7565307617188,732.30029296875),
  new_x_y(758.1156005859375, 730.8775024414062),
  new_x_y(756.4514770507812, 729.4776611328125),
  new_x_y(754.8825073242188, 728.1710205078125),
  new_x_y(753.2809448242188, 726.9573364257812),
  new_x_y(751.64453125, 725.7698364257812),
  new_x_y(749.9868774414062,724.6240234375),
  new_x_y(748.292236328125, 723.4955444335938),
  new_x_y(746.5691528320312, 722.4483642578125),
  new_x_y(744.8391723632812, 721.3909301757812),
  new_x_y(743.1275634765625,720.34375),
  new_x_y(741.358642578125, 719.3234252929688),
  new_x_y(739.55419921875, 718.3248291015625),
  new_x_y(737.775390625, 717.3352661132812),
  new_x_y(735.9932861328125, 716.3433227539062),
  new_x_y(734.1543579101562,715.3193359375),
  new_x_y(732.3410034179688, 714.3501586914062),
  new_x_y(730.5183715820312, 713.4105834960938),
  new_x_y(728.697509765625, 712.4268798828125),
  new_x_y(726.8885498046875, 711.4146118164062),
  new_x_y(725.1082153320312,710.423095703125),
  new_x_y(723.308349609375, 709.4202270507812),
  new_x_y(721.4984741210938, 708.4127807617188),
  new_x_y(719.69873046875, 707.4102783203125),
  new_x_y(717.8887939453125,706.402587890625),
  new_x_y(716.0477905273438,705.378662109375),
  new_x_y(714.2102661132812, 704.3553466796875),
  new_x_y(712.37841796875,703.3359375),
  new_x_y(710.5161743164062,702.298583984375),
  new_x_y(708.666015625, 701.2684936523438),
  new_x_y(706.822265625, 700.2416381835938),
  new_x_y(704.946533203125,699.197021484375),
  new_x_y(703.1136474609375,698.177001953125),
  new_x_y(701.2525024414062, 697.1406860351562),
  new_x_y(699.3790283203125, 696.0982055664062),
  new_x_y(697.5098266601562,695.05810546875),
  new_x_y(695.65625, 694.0261840820312),
  new_x_y(693.7705078125, 692.9769897460938),
  new_x_y(691.901611328125, 691.9364013671875),
  new_x_y(690.0443115234375, 690.9027099609375),
  new_x_y(688.2884521484375, 689.9255981445312),
  new_x_y(686.3914794921875, 688.8699951171875),
  new_x_y(684.5103759765625, 687.8223876953125),
  new_x_y(682.5811767578125, 686.7472534179688),
  new_x_y(680.6767578125, 685.6867065429688),
  new_x_y(678.7884521484375, 684.6353759765625),
  new_x_y(677.0401611328125,683.661865234375),
  new_x_y(675.130615234375, 682.5994262695312),
  new_x_y(673.2427368164062, 681.5475463867188),
  new_x_y(671.3389892578125,680.488037109375),
  new_x_y(669.4193115234375, 679.4188232421875),
  new_x_y(667.5164184570312, 678.3592529296875),
  new_x_y(665.6065673828125, 677.2960205078125),
  new_x_y(663.8457641601562, 676.3156127929688),
  new_x_y(662.094970703125, 675.3401489257812),
  new_x_y(660.34326171875, 674.3646240234375),
  new_x_y(658.416259765625, 673.2919311523438),
  new_x_y(656.5078735351562, 672.2279663085938),
  new_x_y(654.7241821289062, 671.2349243164062),
  new_x_y(652.7996215820312, 670.1641845703125),
  new_x_y(650.9098510742188, 669.1109008789062),
  new_x_y(648.9963989257812,668.045166015625),
  new_x_y(647.1124877929688, 666.9965209960938),
  new_x_y(645.2067260742188, 665.9359130859375),
  new_x_y(643.3223266601562, 664.8859252929688),
  new_x_y(641.4432373046875, 663.8392333984375),
  new_x_y(639.5513916015625, 662.7859497070312),
  new_x_y(637.67626953125, 661.7420043945312),
  new_x_y(635.7838745117188, 660.6829833984375),
  new_x_y(633.8876342773438, 659.5838012695312),
  new_x_y(632.022705078125, 658.5112915039062),
  new_x_y(630.1793823242188, 657.4005126953125),
  new_x_y(628.3280639648438,656.25537109375),
  new_x_y(626.5057373046875, 655.1375732421875),
  new_x_y(624.6355590820312, 654.0831298828125),
  new_x_y(622.7648315429688, 653.0079956054688),
  new_x_y(620.9070434570312, 651.9107055664062),
  new_x_y(619.0673828125, 650.8185424804688),
  new_x_y(617.2235107421875, 649.7243041992188),
  new_x_y(615.3805541992188, 648.6307983398438),
  new_x_y(613.5301513671875, 647.5328369140625),
  new_x_y(611.654052734375, 646.4194946289062),
  new_x_y(609.7936401367188, 645.3159790039062),
  new_x_y(607.9262084960938, 644.2078247070312),
  new_x_y(606.0618896484375,643.1015625),
  new_x_y(604.3362426757812, 642.0778198242188),
  new_x_y(602.6425170898438,640.5009765625),
  new_x_y(600.9219360351562, 639.4813842773438),
  new_x_y(599.2013549804688, 638.4617919921875),
  new_x_y(597.4807739257812, 637.4421997070312),
  new_x_y(595.7601928710938,636.422607421875),
  new_x_y(594.0396118164062, 635.4029541015625),
  new_x_y(592.3190307617188, 634.3833618164062),
  new_x_y(590.598388671875,633.36376953125),
  new_x_y(588.8778076171875, 632.3441772460938),
  new_x_y(587.1572265625, 631.3245849609375),
  new_x_y(585.4366455078125, 630.3049926757812),
  new_x_y(583.716064453125,629.285400390625),
  new_x_y(581.9954833984375, 628.2658081054688),
  new_x_y(580.27490234375, 627.2462158203125),
  new_x_y(578.5543212890625,626.2265625),
  new_x_y(576.833740234375, 625.2069702148438),
  new_x_y(575.1131591796875, 624.1873779296875),
  new_x_y(573.392578125, 623.1677856445312),
  new_x_y(571.6719970703125,622.148193359375),
  new_x_y(569.9513549804688, 621.1286010742188),
  new_x_y(568.2307739257812, 620.1090087890625),
  new_x_y(566.5101928710938, 619.0894165039062),
  new_x_y(564.7896118164062,618.06982421875),
  new_x_y(563.0690307617188, 617.0501708984375),
  new_x_y(561.3484497070312, 616.0305786132812),
  new_x_y(559.6278686523438,615.010986328125),
  new_x_y(557.9072875976562, 613.9913940429688),
  new_x_y(556.1867065429688, 612.9718017578125),
  new_x_y(554.4661254882812, 611.9522094726562),
  new_x_y(552.7454833984375,610.9326171875),
  new_x_y(551.02490234375, 609.9130249023438),
  new_x_y(549.3043212890625, 608.8934326171875),
  new_x_y(547.583740234375, 607.8738403320312),
  new_x_y(545.8631591796875, 606.8541870117188),
  new_x_y(544.142578125, 605.8345947265625),
  new_x_y(542.4219970703125, 604.8150024414062),
  new_x_y(540.701416015625,603.79541015625),
  new_x_y(538.9808349609375, 602.7758178710938),
  new_x_y(537.26025390625, 601.7562255859375),
  new_x_y(535.5396728515625, 600.7366333007812),
  new_x_y(533.819091796875,599.717041015625),
  new_x_y(532.0984497070312, 598.6974487304688),
  new_x_y(530.3778686523438, 597.6778564453125),
  new_x_y(528.6572875976562,596.658203125),
  new_x_y(526.9367065429688, 595.6386108398438),
  new_x_y(525.2161254882812, 594.6190185546875),
  new_x_y(523.4955444335938, 593.5994262695312),
  new_x_y(521.7749633789062,592.579833984375),
  new_x_y(520.0559692382812,591.5576171875),
  new_x_y(518.3410034179688,590.528564453125),
  new_x_y(516.6301879882812,589.49267578125),
  new_x_y(514.9235229492188, 588.4498901367188),
  new_x_y(513.2210693359375,587.400390625),
  new_x_y(511.52276611328125,586.343994140625),
  new_x_y(509.82879638671875, 585.2808837890625),
  new_x_y(508.1390075683594,584.2109375),
  new_x_y(506.4535217285156,583.13427734375),
  new_x_y(504.77239990234375, 582.0509033203125),
  new_x_y(503.0955810546875, 580.9608154296875),
  new_x_y(501.42315673828125, 579.8639526367188),
  new_x_y(499.755126953125,578.760498046875),
  new_x_y(498.091552734375, 577.6503295898438),
  new_x_y(496.4324035644531, 576.5335693359375),
  new_x_y(494.7777404785156, 575.4100952148438),
  new_x_y(493.1275634765625,574.280029296875),
  new_x_y(491.4819641113281, 573.1434326171875),
  new_x_y(489.84088134765625,572.000244140625),
  new_x_y(488.20440673828125, 570.8504638671875),
  new_x_y(486.5725402832031, 569.6942138671875),
  new_x_y(484.9453125, 568.5313720703125),
  new_x_y(483.32275390625,567.362060546875),
  new_x_y(481.70489501953125,566.186279296875),
  new_x_y(480.09173583984375, 565.0040283203125),
  new_x_y(478.4833068847656, 563.8153076171875),
  new_x_y(476.8796691894531, 562.6202392578125),
  new_x_y(475.28082275390625,561.418701171875),
  new_x_y(473.686767578125, 560.2108154296875),
  new_x_y(472.09759521484375, 558.9965209960938),
  new_x_y(470.5132751464844,557.77587890625),
  new_x_y(468.933837890625, 556.5489501953125),
  new_x_y(467.3593444824219,555.315673828125),
  new_x_y(465.7897644042969,554.076171875),
  new_x_y(464.2251892089844,552.830322265625),
  new_x_y(462.66558837890625, 551.5782470703125),
  new_x_y(461.11102294921875, 550.3199462890625),
  new_x_y(459.5611267089844,549.055908203125),
  new_x_y(458.01220703125, 547.7906494140625),
  new_x_y(456.46331787109375,546.525390625),
  new_x_y(454.9143981933594, 545.2601318359375),
  new_x_y(453.3655090332031, 543.9948120117188),
  new_x_y(451.8166198730469, 542.7295532226562),
  new_x_y(450.2677001953125, 541.4642944335938),
  new_x_y(448.71881103515625, 540.1990356445312),
  new_x_y(447.1698913574219, 538.9337768554688),
  new_x_y(445.6210021972656, 537.6685180664062),
  new_x_y(444.0721130371094, 536.4032592773438),
  new_x_y(442.523193359375,535.137939453125),
  new_x_y(440.97430419921875, 533.8726806640625),
  new_x_y(439.4253845214844,532.607421875),
  new_x_y(437.87677001953125,531.341796875),
  new_x_y(436.33203125, 530.0714721679688),
  new_x_y(434.7923889160156,528.794921875),
  new_x_y(433.25787353515625, 527.5122680664062),
  new_x_y(431.728515625, 526.2235107421875),
  new_x_y(430.2043151855469, 524.9285888671875),
  new_x_y(428.685302734375, 523.6275634765625),
  new_x_y(427.1714782714844, 522.3204956054688),
  new_x_y(425.6629333496094, 521.0073852539062),
  new_x_y(424.1596374511719,519.688232421875),
  new_x_y(422.6616516113281, 518.3631591796875),
  new_x_y(421.1689453125,517.031982421875),
  new_x_y(419.68157958984375, 515.6949462890625),
  new_x_y(418.1995849609375, 514.3519287109375),
  new_x_y(416.7229919433594, 513.0029907226562),
  new_x_y(415.25177001953125, 511.6481628417969),
  new_x_y(413.7860107421875, 510.2874755859375),
  new_x_y(412.3236999511719, 508.92303466796875),
  new_x_y(410.8614501953125, 507.5585632324219),
  new_x_y(409.399169921875, 506.1941223144531),
  new_x_y(407.9368896484375, 504.82965087890625),
  new_x_y(406.4746398925781, 503.4651794433594),
  new_x_y(405.0123596191406, 502.1007080078125),
  new_x_y(403.55010986328125, 500.7362365722656),
  new_x_y(402.08782958984375, 499.37176513671875),
  new_x_y(400.62554931640625,498.00732421875),
  new_x_y(399.1632995605469, 496.6428527832031),
  new_x_y(397.7010192871094, 495.27838134765625),
  new_x_y(396.2387390136719, 493.9139099121094),
  new_x_y(394.7764892578125, 492.5494384765625),
  new_x_y(393.314208984375, 491.18499755859375),
  new_x_y(391.8519287109375, 489.8205261230469),
  new_x_y(390.3896789550781,488.4560546875),
  new_x_y(388.9273986816406, 487.0915832519531),
  new_x_y(387.4651184082031, 485.72711181640625),
  new_x_y(386.00286865234375, 484.3626403808594),
  new_x_y(384.54058837890625, 482.9981689453125),
  new_x_y(383.07830810546875, 481.63372802734375),
  new_x_y(381.6160583496094, 480.2692565917969),
  new_x_y(380.1537780761719,478.90478515625),
  new_x_y(378.6915283203125, 477.5403137207031),
  new_x_y(377.229248046875, 476.17584228515625),
  new_x_y(375.7669677734375, 474.8114013671875),
  new_x_y(374.3047180175781, 473.4469299316406),
  new_x_y(372.8424377441406, 472.08245849609375),
  new_x_y(371.3801574707031, 470.7179870605469),
  new_x_y(369.91790771484375,469.353515625),
  new_x_y(368.45562744140625, 467.9890441894531),
  new_x_y(366.99334716796875, 466.6246032714844),
  new_x_y(365.5310974121094, 465.2601318359375),
  new_x_y(364.0688171386719, 463.8956604003906),
  new_x_y(362.6065368652344, 462.53118896484375),
  new_x_y(361.144287109375, 461.1667175292969),
  new_x_y(359.6820068359375,459.80224609375),
  new_x_y(358.2197265625, 458.43780517578125),
  new_x_y(356.7574768066406, 457.0733337402344),
  new_x_y(355.2951965332031, 455.7088623046875),
  new_x_y(353.83294677734375, 454.3443908691406),
  new_x_y(352.37066650390625, 452.97991943359375),
  new_x_y(350.90838623046875,451.615478515625),
  new_x_y(349.44610595703125, 450.2510070800781),
  new_x_y(347.9838562011719, 448.88653564453125),
  new_x_y(346.5215759277344, 447.5220642089844),
  new_x_y(345.059326171875, 446.1575927734375),
  new_x_y(343.5970458984375, 444.7931213378906),
  new_x_y(342.13543701171875,443.427978515625),
  new_x_y(340.67852783203125, 442.05780029296875),
  new_x_y(339.22711181640625, 440.6817932128906),
  new_x_y(337.78118896484375, 439.3000183105469),
  new_x_y(336.33929443359375, 437.91400146484375),
  new_x_y(334.8976135253906, 436.5278015136719),
  new_x_y(333.4559326171875,435.1416015625),
  new_x_y(332.0142517089844, 433.7554016113281),
  new_x_y(330.57257080078125, 432.36920166015625),
  new_x_y(329.1308898925781, 430.9830017089844),
  new_x_y(327.689208984375, 429.5968017578125),
  new_x_y(326.2475280761719, 428.2106018066406),
  new_x_y(324.80584716796875, 426.82440185546875),
  new_x_y(323.3641662597656, 425.4382019042969),
  new_x_y(321.9224853515625,424.052001953125),
  new_x_y(320.4808044433594, 422.6658020019531),
  new_x_y(319.03912353515625, 421.27960205078125),
  new_x_y(317.5974426269531, 419.89337158203125),
  new_x_y(316.15576171875, 418.5071716308594),
  new_x_y(314.7140808105469, 417.1209716796875),
  new_x_y(313.27239990234375, 415.7347717285156),
  new_x_y(311.8307189941406, 414.34857177734375),
  new_x_y(310.3890380859375, 412.9623718261719),
  new_x_y(308.9473571777344,411.576171875),
  new_x_y(307.50567626953125, 410.1899719238281),
  new_x_y(306.0639953613281, 408.80377197265625),
  new_x_y(304.622314453125, 407.4175720214844),
  new_x_y(303.1806335449219, 406.0313720703125),
  new_x_y(301.73895263671875, 404.6451416015625),
  new_x_y(300.2972717285156, 403.25897216796875),
  new_x_y(298.8555908203125, 401.87274169921875),
  new_x_y(297.4139099121094, 400.4865417480469),
  new_x_y(295.97222900390625,399.100341796875),
  new_x_y(294.5305480957031, 397.7141418457031),
  new_x_y(293.0888671875, 396.32794189453125),
  new_x_y(291.6471862792969, 394.9417419433594),
  new_x_y(290.20550537109375, 393.5555419921875),
  new_x_y(288.7638244628906, 392.1693420410156),
  new_x_y(287.3221435546875, 390.78314208984375),
  new_x_y(285.8804626464844, 389.3969421386719),
  new_x_y(284.43878173828125,388.0107421875),
  new_x_y(282.99713134765625,386.62451171875),
  new_x_y(281.555419921875, 385.2383117675781),
  new_x_y(280.11376953125, 383.85211181640625),
  new_x_y(278.67205810546875, 382.4659118652344),
  new_x_y(277.23040771484375, 381.0797119140625),
  new_x_y(275.7886962890625, 379.6935119628906),
  new_x_y(274.3470458984375, 378.30731201171875),
  new_x_y(272.90533447265625, 376.9211120605469),
  new_x_y(271.46368408203125,375.534912109375),
  new_x_y(270.02197265625, 374.1487121582031),
  new_x_y(268.580322265625, 372.76251220703125),
  new_x_y(267.1395263671875, 371.37530517578125),
  new_x_y(265.70379638671875, 369.9829406738281),
  new_x_y(264.2736511230469, 368.5848388671875),
  new_x_y(262.84912109375, 367.1810302734375),
  new_x_y(261.4302062988281, 365.7715148925781),
  new_x_y(260.0169982910156, 364.3563537597656),
  new_x_y(258.6064453125,362.9384765625),
  new_x_y(257.1959228515625, 361.52056884765625),
  new_x_y(255.785400390625, 360.1026916503906),
  new_x_y(254.3748779296875, 358.6847839355469),
  new_x_y(252.96435546875, 357.26690673828125),
  new_x_y(251.5538330078125, 355.8490295410156),
  new_x_y(250.14329528808594, 354.4311218261719),
  new_x_y(248.73277282714844, 353.01324462890625),
  new_x_y(247.32225036621094, 351.5953369140625),
  new_x_y(245.91171264648438, 350.1774597167969),
  new_x_y(244.50119018554688, 348.7595520019531),
  new_x_y(243.09066772460938, 347.3416748046875),
  new_x_y(241.68014526367188, 345.92376708984375),
  new_x_y(240.2696075439453, 344.5058898925781),
  new_x_y(238.8590850830078, 343.0880126953125),
  new_x_y(237.4485626220703, 341.67010498046875),
  new_x_y(236.03802490234375, 340.2522277832031),
  new_x_y(234.62750244140625, 338.8343200683594),
  new_x_y(233.21697998046875, 337.41644287109375),
  new_x_y(231.80645751953125,335.99853515625),
  new_x_y(230.3959197998047, 334.5806579589844),
  new_x_y(228.9853973388672, 333.1627502441406),
  new_x_y(227.5748748779297,331.744873046875),
  new_x_y(226.16433715820312, 330.32696533203125),
  new_x_y(224.75381469726562, 328.9090881347656),
  new_x_y(223.34329223632812,327.4912109375),
  new_x_y(221.93276977539062, 326.07330322265625),
  new_x_y(220.52224731445312, 324.6554260253906),
  new_x_y(219.11170959472656, 323.2375183105469),
  new_x_y(217.70118713378906, 321.81964111328125),
  new_x_y(216.2906494140625, 320.4017333984375),
  new_x_y(214.880126953125, 318.9838562011719),
  new_x_y(213.4696044921875, 317.56597900390625),
  new_x_y(212.05908203125, 316.1480712890625),
  new_x_y(210.6485595703125, 314.7301940917969),
  new_x_y(209.23802185058594, 313.3122863769531),
  new_x_y(207.82749938964844, 311.8944091796875),
  new_x_y(206.41697692871094, 310.47650146484375),
  new_x_y(205.00643920898438, 309.0586242675781),
  new_x_y(203.59591674804688, 307.6407165527344),
  new_x_y(202.18539428710938, 306.22283935546875),
  new_x_y(200.77487182617188,304.804931640625),
  new_x_y(199.3643341064453, 303.3870544433594),
  new_x_y(197.9538116455078, 301.96917724609375),
  new_x_y(196.5432891845703,300.55126953125),
  new_x_y(195.13182067871094, 299.13433837890625),
  new_x_y(193.71519470214844, 297.7225036621094),
  new_x_y(192.29295349121094, 296.3163757324219),
  new_x_y(190.8650665283203, 294.91595458984375),
  new_x_y(189.43162536621094,293.521240234375),
  new_x_y(187.9925994873047, 292.1322937011719),
  new_x_y(186.5480499267578, 290.74908447265625),
  new_x_y(185.0979461669922, 289.3716735839844),
  new_x_y(183.6423797607422, 288.0000915527344),
  new_x_y(182.18133544921875, 286.6343078613281),
  new_x_y(180.7180938720703, 285.2708740234375),
  new_x_y(179.2548370361328,283.907470703125),
  new_x_y(177.79159545898438, 282.5440673828125),
  new_x_y(176.32833862304688, 281.1806335449219),
  new_x_y(174.86508178710938, 279.8172302246094),
  new_x_y(173.40184020996094, 278.4538269042969),
  new_x_y(171.93858337402344, 277.09039306640625),
  new_x_y(170.47532653808594, 275.72698974609375),
  new_x_y(169.0120849609375, 274.36358642578125),
  new_x_y(167.548828125, 273.0001525878906),
  new_x_y(166.0855712890625, 271.6367492675781),
  new_x_y(164.62232971191406, 270.2733459472656),
  new_x_y(163.15907287597656,268.909912109375),
  new_x_y(161.69583129882812, 267.5465087890625),
  new_x_y(160.23257446289062,266.18310546875),
  new_x_y(158.76931762695312, 264.8196716308594),
  new_x_y(157.3060760498047, 263.4562683105469),
  new_x_y(155.8428192138672, 262.0928649902344),
  new_x_y(154.37957763671875, 260.72943115234375),
  new_x_y(152.91632080078125, 259.36602783203125),
  new_x_y(151.45306396484375, 258.00262451171875),
  new_x_y(149.98980712890625, 256.63922119140625),
  new_x_y(148.5265655517578, 255.27578735351562),
  new_x_y(147.0633087158203, 253.91238403320312),
  new_x_y(145.60006713867188, 252.54896545410156),
  new_x_y(144.13681030273438,251.185546875),
  new_x_y(142.67355346679688, 249.8221435546875),
  new_x_y(141.21031188964844, 248.45872497558594),
  new_x_y(139.74705505371094, 247.09530639648438),
  new_x_y(138.2838134765625, 245.73190307617188),
  new_x_y(136.820556640625, 244.3684844970703),
  new_x_y(135.3572998046875, 243.00506591796875),
  new_x_y(133.89404296875, 241.64166259765625),
  new_x_y(132.43080139160156, 240.2782440185547),
  new_x_y(130.96754455566406, 238.91482543945312),
  new_x_y(129.50430297851562, 237.55142211914062),
  new_x_y(128.04104614257812, 236.18800354003906),
  new_x_y(126.57778930664062, 234.8245849609375),
  new_x_y(125.11454772949219,233.461181640625),
  new_x_y(123.65129089355469, 232.09776306152344),
  new_x_y(122.18804168701172, 230.73434448242188),
  new_x_y(120.72479248046875, 229.37094116210938),
  new_x_y(119.26153564453125, 228.0075225830078),
  new_x_y(117.79828643798828, 226.64410400390625),
  new_x_y(116.33503723144531, 225.28070068359375),
  new_x_y(114.87178802490234, 223.9172821044922),
  new_x_y(113.40853881835938, 222.55386352539062),
  new_x_y(111.94528198242188, 221.19046020507812),
  new_x_y(110.4820327758789, 219.82705688476562),
  new_x_y(109.01878356933594,218.463623046875),
  new_x_y(107.55553436279297, 217.1002197265625),
  new_x_y(106.09227752685547,215.73681640625),
  new_x_y(104.6290283203125, 214.37338256835938),
  new_x_y(103.16577911376953, 213.00997924804688),
  new_x_y(101.70252227783203, 211.64657592773438),
  new_x_y(100.23927307128906, 210.28314208984375),
  new_x_y(98.7760238647461, 208.91973876953125),
  new_x_y(97.31277465820312, 207.55633544921875),
  new_x_y(95.84951782226562, 206.19290161132812),
  new_x_y(94.38626861572266, 204.82949829101562),
  new_x_y(92.92301940917969, 203.46609497070312),
  new_x_y(91.45977020263672, 202.1026611328125),
  new_x_y(89.99651336669922,200.7392578125),
  new_x_y(88.53326416015625, 199.3758544921875),
  new_x_y(87.07001495361328, 198.01243591308594),
  new_x_y(85.60676574707031, 196.64901733398438),
  new_x_y(84.14350891113281, 195.28561401367188),
  new_x_y(82.68025970458984, 193.9221954345703),
  new_x_y(81.21701049804688, 192.55877685546875),
  new_x_y(79.7537612915039, 191.19537353515625),
  new_x_y(78.2905044555664, 189.8319549560547),
  new_x_y(76.82725524902344, 188.46853637695312),
  new_x_y(75.36400604248047, 187.10513305664062),
  new_x_y(73.90074920654297, 185.74171447753906),
  new_x_y(72.4375, 184.3782958984375),
  new_x_y(70.97425079345703,183.014892578125),
  new_x_y(69.51100158691406, 181.65147399902344),
  new_x_y(68.04774475097656, 180.28805541992188),
  new_x_y(66.5844955444336, 178.92465209960938),
  new_x_y(65.12124633789062, 177.5612335205078),
  new_x_y(63.657997131347656, 176.19781494140625),
  new_x_y(62.194740295410156, 174.83441162109375),
  new_x_y(60.73149108886719, 173.4709930419922),
  new_x_y(59.26824188232422, 172.10757446289062),
  new_x_y(57.80499267578125, 170.74417114257812),
  new_x_y(56.34173583984375, 169.38075256347656),
  new_x_y(54.87848663330078,168.017333984375),
  new_x_y(53.41523742675781, 166.6539306640625),
  new_x_y(51.95198059082031, 165.29051208496094),
  new_x_y(50.488739013671875, 163.92709350585938),
  new_x_y(49.025482177734375, 162.56369018554688),
  new_x_y(47.562225341796875, 161.2002716064453),
  new_x_y(46.09898376464844, 159.83685302734375),
  new_x_y(44.63572692871094, 158.47344970703125),
  new_x_y(43.17041015625, 157.11224365234375),
  new_x_y(41.700340270996094, 155.75621032714844),
  new_x_y(40.22953796386719, 154.40093994140625),
  new_x_y(38.758731842041016, 153.04568481445312),
  new_x_y(37.287925720214844,151.6904296875),
  new_x_y(35.81712341308594, 150.3351593017578),
  new_x_y(34.346317291259766, 148.9799041748047),
  new_x_y(32.87551498413086, 147.6246337890625),
  new_x_y(31.404708862304688, 146.26937866210938),
  new_x_y(29.933902740478516, 144.91412353515625),
  new_x_y(28.46310043334961, 143.55885314941406),
  new_x_y(26.992294311523438, 142.20359802246094),
  new_x_y(25.5214900970459, 140.84832763671875),
  new_x_y(24.05068588256836, 139.49307250976562),
  new_x_y(22.579879760742188, 138.1378173828125),
  new_x_y(21.10907554626465, 136.7825469970703),
  new_x_y(19.63827133178711, 135.4272918701172),
  new_x_y(18.16746711730957,134.072021484375),
  new_x_y(16.6966609954834, 132.71676635742188),
  new_x_y(15.22585678100586, 131.36151123046875),
  new_x_y(13.75505256652832, 130.00624084472656),
  new_x_y(12.284248352050781, 128.65098571777344),
  new_x_y(10.81344223022461, 127.29571533203125),
  new_x_y(9.342639923095703, 125.94046020507812),
  new_x_y(7.871833801269531, 124.58518981933594),
  new_x_y(6.401027679443359, 123.22993469238281),
  new_x_y(4.930999755859375, 121.87382507324219),
  new_x_y(3.465850830078125, 120.51246643066406),
  new_x_y(2.00616455078125, 119.14524841308594),
  new_x_y(0.55194091796875, 117.9),
  new_x_y(-0.89678955078125, 116.9),
  new_x_y(-2.3399658203125, 115.8),
  new_x_y(-3.97967929840087,112.0204833984375),
  new_x_y(-4.9, 110.3),
  new_x_y(-6.0046272277832,106.52698516845703),
  new_x_y(-6.96678657531738,103.77728271484375),
  new_x_y(-7.31775169372558,100.9249038696289),
  new_x_y(-8.0, 97.99624633789062),
  new_x_y(-8.03402919769287,96.01879119873047),
  new_x_y(-8.08787841796875, 97.02069091796875),
  new_x_y(-8.8743272781372, 95.02230072021484),
  new_x_y(-8.86077613830566, 93.02391052246094),
  new_x_y(-8.60400104522705, 91.02471923828125),
  new_x_y(-8.54722595214843, 89.02552795410156),
  new_x_y(-8.4904499053955, 87.02632904052734),
  new_x_y(-8.43367481231689, 85.02713775634766),
  new_x_y(-8.37689971923828, 83.02793884277344),
  new_x_y(-8.32369995117187, 81.02864837646484),
  new_x_y(-8.27975463867187, 79.02913665771484),
  new_x_y(-8.2451171875, 77.02943420410156),
  new_x_y(-8.21978759765625, 75.02960205078125),
  new_x_y(-8.20376586914062,73.0296630859375),
  new_x_y(-8.19705200195312, 71.02967834472656),
  new_x_y(-8.19964599609375, 69.02967834472656),
  new_x_y(-8.21157836914062, 67.02971649169922),
  new_x_y(-8.2327880859375, 65.02983093261719),
  new_x_y(-8.2633056640625, 63.030067443847656),
  new_x_y(-8.30316162109375, 61.03046417236328),
  new_x_y(-8.352294921875, 59.031070709228516),
  new_x_y(-8.41073608398437, 57.03192901611328),
  new_x_y(-8.478515625, 55.033077239990234),
  new_x_y(-8.55557250976562, 53.03456497192383),
  new_x_y(-8.64193725585937, 51.03643035888672),
  new_x_y(-8.73757934570312, 49.03872299194336),
  new_x_y(-8.84255981445312, 47.041481018066406),
  new_x_y(-8.95681762695312, 45.04474639892578),
  new_x_y(-9.08035278320312, 43.04856872558594),
  new_x_y(-9.21319580078125, 41.05298614501953),
  new_x_y(-9.35531616210937, 39.05804443359375),
  new_x_y(-9.50674438476562, 37.06378936767578),
  new_x_y(-9.66741943359375, 35.070255279541016),
  new_x_y(-9.83740234375, 33.07749557495117),
  new_x_y(-10.0164966583251, 31.08553123474121),
  new_x_y(-10.1985836029052, 29.09383773803711),
  new_x_y(-10.3806705474853, 27.102144241333008),
  new_x_y(-10.5627574920654, 25.110450744628906),
  new_x_y(-10.7448444366455, 23.118755340576172),
  new_x_y(-10.9269313812255, 21.127063751220703),
  new_x_y(-11.1197814941406, 19.136409759521484),
  new_x_y(-11.3561401367187, 17.150470733642578),
  new_x_y(-11.6381530761718, 15.170498847961426),
  new_x_y(-11.9656753540039, 13.197543144226074),
  new_x_y(-12.3385314941406, 11.232650756835938),
  new_x_y(-12.7565231323242, 9.276863098144531),
  new_x_y(-13.2194290161132, 7.331214904785156),
  new_x_y(-13.7269973754882, 5.396739959716797),
  new_x_y(-14.2789688110351, 3.4744625091552734),
  new_x_y(-14.8750457763671, 1.5654010772705078),
  new_x_y(-15.5149154663085,-0.329431533813476),
  new_x_y(-16.1982345581054,-2.20903205871582),
  new_x_y(-16.9246444702148,-4.07240295410156),
  new_x_y(-17.6937561035156,-5.91856002807617),
  new_x_y(-18.5051651000976,-7.74652099609375),
  new_x_y(-19.3584442138671,-9.55531692504882),
  new_x_y(-20.2531280517578,-11.3439903259277),
  new_x_y(-21.1887588500976,-13.1115913391113),
  new_x_y(-22.1648330688476,-14.8571853637695),
  new_x_y(-23.1808395385742,-16.579849243164),
  new_x_y(-24.236228942871,-18.2786636352539),
  new_x_y(-25.3304443359375,-19.9527359008789),
  new_x_y(-26.4629135131835,-21.6011695861816),
  new_x_y(-27.6330261230468,-23.2230987548828),
  new_x_y(-28.8401718139648,-24.8176612854003),
  new_x_y(-30.0837020874023,-26.3840103149414),
  new_x_y(-31.3610324859619,-27.9229488372802),
  new_x_y(-32.6462783813476,-29.4553146362304),
  new_x_y(-33.9315223693847,-30.9876823425292),
  new_x_y(-35.2167663574218,-32.5200462341308),
  new_x_y(-36.5020141601562,-34.0524101257324),
  new_x_y(-37.7872581481933,-35.5847778320312),
  new_x_y(-39.0725021362304,-37.1171417236328),
  new_x_y(-40.3596954345703,-38.6478767395019),
  new_x_y(-41.666259765625,-40.1620750427246),
  new_x_y(-42.9961013793945,-41.6558723449707),
  new_x_y(-44.348892211914,-43.1289253234863),
  new_x_y(-45.7243194580078,-44.5808677673339),
  new_x_y(-47.1220397949218,-46.0113487243652),
  new_x_y(-48.5417251586914,-47.4200401306152),
  new_x_y(-49.983039855957,-48.80659866333),
  new_x_y(-51.4456329345703,-50.1706886291503),
  new_x_y(-52.9291610717773,-51.5119819641113),
  new_x_y(-54.4332580566406,-52.8301658630371),
  new_x_y(-55.9575729370117,-54.1249198913574),
  new_x_y(-57.5017318725585,-55.3959312438964),
  new_x_y(-59.0647621154785,-56.643684387207),
  new_x_y(-60.5854568481445,-57.9421768188476),
  new_x_y(-62.0190505981445,-59.3362426757812),
  new_x_y(-63.3595466613769,-60.8200454711914),
  new_x_y(-64.6013412475586,-62.3873901367187),
  new_x_y(-65.7392349243164,-64.0317077636718),
  new_x_y(-66.4,-65.7461395263671),
  new_x_y(-66.8,-67.5235061645507),
  new_x_y(-67.7,-70.3563766479492),
  new_x_y(-68.4,-73.2370910644531),
  new_x_y(-68.8,-76.1577758789062),
  new_x_y(-69.2,-78.1104049682617),
  new_x_y(-69.4,-80.0868148803711),
  new_x_y(-69.9,-83.0774002075195),
  new_x_y(-70.25,-86.0694808959961),
  new_x_y(-70.55,-88.0615615844726),
  new_x_y(-70.85,-90.0536422729492),
  new_x_y(-71.3,-92.0457229614257),
  new_x_y(-72.0,-95.0378036499023),
  new_x_y(-72.2,-97.0061264038086),
  new_x_y(-72.6,-98.9982070922851),
  new_x_y(-72.9,-100.990287780761),
  new_x_y(-73.1,-102.982368469238),
  new_x_y(-73.4,-104.974449157714),
  new_x_y(-73.8,-106.966529846191),
  new_x_y(-74,-108.958610534667),
  new_x_y(-74.2,-110.950691223144),
  new_x_y(-74.4,-112.942771911621),
  new_x_y(-74.6,-114.934852600097),
  new_x_y(-74.8,-116.926933288574),
  new_x_y(-74.9,-118.91901397705),
  new_x_y(-75.1,-120.911094665527),
  new_x_y(-75.3,-122.903175354003),
  new_x_y(-75.5,-124.89525604248),
  new_x_y(-76.7,-126.887336730957),
  new_x_y(-76.8,-128.879440307617),
  new_x_y(-77,-130.872024536132),
  new_x_y(-77.25,-132.865295410156),
  new_x_y(-77.4,-134.858932495117),
  new_x_y(-77.6,-136.852584838867),
  new_x_y(-77.8,-138.846221923828),
  new_x_y(-77.9,-140.839874267578),
  new_x_y(-78.1,-142.833526611328),
  new_x_y(-78.2,-144.827178955078),
  new_x_y(-78.34,-146.820831298828),
  new_x_y(-78.5,-148.814483642578),
  new_x_y(-78.7,-150.808135986328),
  new_x_y(-78.8,-152.801773071289),
  new_x_y(-78.9,-154.795425415039),
  new_x_y(-79,-156.789077758789),
  new_x_y(-79.15,-158.782730102539),
  new_x_y(-79.25,-160.776382446289),
  new_x_y(-79.4,-162.77001953125),
  new_x_y(-79.5,-164.763671875),
  new_x_y(-79.6,-166.75732421875),
  new_x_y(-79.75,-168.7509765625),
  new_x_y(-79.9,-170.74462890625),
  new_x_y(-80,-172.73828125),
  new_x_y(-80.1,-174.73193359375),
  new_x_y(-80.3,-176.7255859375),
  new_x_y(-80.4,-178.71922302246),
  new_x_y(-80.5,-180.71287536621),
  new_x_y(-80.6,-182.70652770996),
  new_x_y(-80.7,-184.70018005371),
  new_x_y(-80.85, -186.693817138671),
  new_x_y(-81,-188.687469482421),
  new_x_y(-81.2,-190.681121826171),
  new_x_y(-81.3,-192.674774169921),
  new_x_y(-81.4,-194.668426513671),
  new_x_y(-81.5,-196.662078857421),
  new_x_y(-81.7,-198.655731201171),
  new_x_y(-81.8,-200.649383544921),
  new_x_y(-82,-202.643035888671),
  new_x_y(-82.2,-204.636672973632),
  new_x_y(-82.3,-206.630325317382),
  new_x_y(-82.5,-208.623977661132),
  new_x_y(-82.6,-210.617614746093),
  new_x_y(-82.7,-212.611267089843),
  new_x_y(-82.9,-214.604919433593),
  new_x_y(-83,-216.598770141601),
  new_x_y(-83.1,-218.593215942382),
  new_x_y(-83.2,-220.588256835937),
  new_x_y(-83.3,-222.583831787109),
  new_x_y(-83.4,-224.579925537109),
  new_x_y(-83.5,-226.576507568359),
  new_x_y(-83.6,-228.573532104492),
  new_x_y(-83.7,-230.570983886718),
  new_x_y(-83.85,-232.568817138671),
  new_x_y(-84,-234.567016601562),
  new_x_y(-84.05,-236.565536499023),
  new_x_y(-84.1,-238.564132690429),
  new_x_y(-84.2,-240.562728881835),
  new_x_y(-84.3,-242.561325073242),
  new_x_y(-84.4,-244.559921264648),
  new_x_y(-84.5,-246.558517456054),
  new_x_y(-84.6,-248.55711364746),
  new_x_y(-84.7,-250.555694580078),
  new_x_y(-84.8,-252.554290771484),
  new_x_y(-84.9,-254.55288696289),
  new_x_y(-85,-256.551483154296),
  new_x_y(-85,-258.550079345703),
  new_x_y(-85.1,-260.548675537109),
  new_x_y(-85.2,-262.547271728515),
  new_x_y(-85.3,-264.545867919921),
  new_x_y(-85.4,-266.544464111328),
  new_x_y(-85.5,-268.543060302734),
  new_x_y(-85.65,-270.54165649414),
  new_x_y(-85.75,-272.540252685546),
  new_x_y(-85.9,-274.538848876953),
  new_x_y(-86,-276.537445068359),
  new_x_y(-86.1,-278.536041259765),
  new_x_y(-86.2,-280.534637451171),
  new_x_y(-86.3,-282.533233642578),
  new_x_y(-86.4,-284.531829833984),
  new_x_y(-86.5,-286.53042602539),
  new_x_y(-86.6,-288.528991699218),
  new_x_y(-86.7,-290.527587890625),
  new_x_y(-86.8,-292.526184082031),
  new_x_y(-86.9,-294.524780273437),
  new_x_y(-87,-296.523376464843),
  new_x_y(-87.05,-298.52197265625),
  new_x_y(-87.1,-300.520568847656),
  new_x_y(-87.2,-302.519165039062),
  new_x_y(-87.3,-304.517761230468),
  new_x_y(-87.4,-306.516357421875),
  new_x_y(-87.4,-308.514953613281),
  new_x_y(-87.5,-310.513549804687),
  new_x_y(-87.5,-312.512145996093),
  new_x_y(-87.6,-314.5107421875),
  new_x_y(-87.7,-316.509338378906),
  new_x_y(-87.8,-318.507934570312),
  new_x_y(-87.9,-320.506530761718),
  new_x_y(-88,-322.505126953125),
  new_x_y(-88,-324.503723144531),
  new_x_y(-88.1,-326.502319335937),
  new_x_y(-88.2,-328.500915527343),
  new_x_y(-88.3,-330.49951171875),
  new_x_y(-88.4,-332.498107910156),
  new_x_y(-88.5,-334.496704101562),
  new_x_y(-88.6,-336.495300292968),
  new_x_y(-88.7,-338.493896484375),
  new_x_y(-88.8,-340.492492675781),
  new_x_y(-88.9,-342.491088867187),
  new_x_y(-89,-344.489685058593),
  new_x_y(-89.1,-346.48828125),
  new_x_y(-89.2,-348.486877441406),
  new_x_y(-89.3,-350.485473632812),
  new_x_y(-89.4,-352.48403930664),
  new_x_y(-89.5,-354.482635498046),
  new_x_y(-89.55,-356.481231689453),
  new_x_y(-89.6,-358.479827880859),
  new_x_y(-89.7,-360.478424072265),
  new_x_y(-89.75,-362.477020263671),
  new_x_y(-89.8,-364.475616455078),
  new_x_y(-89.85,-366.474212646484),
  new_x_y(-89.9,-368.47280883789),
  new_x_y(-90,-370.471405029296),
  new_x_y(-90.1,-372.470001220703),
  new_x_y(-90.1,-374.468597412109),
  new_x_y(-90.2,-376.467193603515),
  new_x_y(-90.2,-378.465789794921),
  new_x_y(-90.3,-380.464385986328),
  new_x_y(-90.3,-382.462982177734),
  new_x_y(-90.4,-384.461547851562),
  new_x_y(-90.5,-386.460144042968),
  new_x_y(-90.6,-388.458740234375),
  new_x_y(-90.6,-390.457336425781),
  new_x_y(-90.7,-392.455932617187),
  new_x_y(-90.8,-394.454528808593),
  new_x_y(-90.9,-396.453125),
  new_x_y(-91,-398.451721191406),
  new_x_y(-91.1,-400.450317382812),
  new_x_y(-91.1,-402.448913574218),
  new_x_y(-91.2,-404.447509765625),
  new_x_y(-91.2,-406.446105957031),
  new_x_y(-91.3,-408.444702148437),
  new_x_y(-91.4,-410.443298339843),
  new_x_y(-91.5,-412.44189453125),
  new_x_y(-91.6,-414.440490722656),
  new_x_y(-91.7,-416.439086914062),
  new_x_y(-91.8,-418.437683105468),
  new_x_y(-91.9,-420.436279296875),
  new_x_y(-92,-422.434875488281),
  new_x_y(-92,-424.433471679687),
  new_x_y(-92.1,-426.432067871093),
  new_x_y(-92.2,-428.4306640625),
  new_x_y(-92.3,-430.429260253906),
  new_x_y(-92.35,-432.427856445312),
  new_x_y(-92.5,-434.426452636718),
  new_x_y(-92.6,-436.425048828125),
  new_x_y(-92.7,-438.423645019531),
  new_x_y(-92.8,-440.422241210937),
  new_x_y(-92.9,-442.420837402343),
  new_x_y(-92.9,-444.41943359375),
  new_x_y(-93,-446.418029785156),
  new_x_y(-93.1,-448.416625976562),
  new_x_y(-93.2,-450.415222167968),
  new_x_y(-93.3,-452.413818359375),
  new_x_y(-93.4,-454.412414550781),
  new_x_y(-93.5,-456.411010742187),
  new_x_y(-93.5,-458.409606933593),
  new_x_y(-93.6,-460.408203125),
  new_x_y(-93.65,-462.406799316406),
  new_x_y(-93.65,-464.405364990234),
  new_x_y(-93.7,-466.40396118164),
  new_x_y(-93.7,-468.402557373046),
  new_x_y(-93.8,-470.401153564453),
  new_x_y(-93.85,-472.399749755859),
  new_x_y(-93.9,-474.398345947265),
  new_x_y(-93.95,-476.396942138671),
  new_x_y(-94,-478.395538330078),
  new_x_y(-94,-480.394134521484),
  new_x_y(-94.1,-482.39273071289),
  new_x_y(-94.2,-484.391326904296),
  new_x_y(-94.3,-486.389923095703),
  new_x_y(-94.4,-488.388519287109),
  new_x_y(-94.45,-490.387084960937),
  new_x_y(-94.5,-492.385711669921),
  new_x_y(-94.55,-494.384307861328),
  new_x_y(-94.55,-496.382904052734),
  new_x_y(-94.6,-498.38150024414),
  new_x_y(-94.7,-500.380096435546),
  new_x_y(-94.8,-502.378692626953),
  new_x_y(-94.9,-504.377258300781),
  new_x_y(-95,-506.375854492187),
  new_x_y(-95,-508.374450683593),
  new_x_y(-95.1,-510.373046875),
  new_x_y(-95.1,-512.37158203125),
  new_x_y(-95.2,-514.369873046875),
  new_x_y(-95.3,-516.367797851562),
  new_x_y(-95.35,-518.365417480468),
  new_x_y(-95.4,-520.362976074218),
  new_x_y(-95.5,-522.360534667968),
  new_x_y(-95.55,-524.358093261718),
  new_x_y(-95.6,-526.355651855468),
  new_x_y(-95.6,-528.353271484375),
  new_x_y(-95.65,-530.350830078125),
  new_x_y(-95.7,-532.348388671875),
  new_x_y(-95.75,-534.345947265625),
  new_x_y(-95.8,-536.343505859375),
  new_x_y(-95.85,-538.341064453125),
  new_x_y(-95.9,-540.338684082031),
  new_x_y(-96,-542.336242675781),
  new_x_y(-96,-544.333801269531),
  new_x_y(-96.05,-546.331359863281),
  new_x_y(-96.1,-548.328918457031),
  new_x_y(-96.2,-550.326477050781),
  new_x_y(-96.2,-552.324035644531),
  new_x_y(-96.2,-554.321655273437),
  new_x_y(-96.2,-556.319213867187),
  new_x_y(-96.2,-558.316772460937),
  new_x_y(-96.2,-560.314331054687),
  new_x_y(-96.3,-562.311889648437),
  new_x_y(-96.35,-564.309448242187),
  new_x_y(-96.4,-566.307006835937),
  new_x_y(-96.4,-568.304626464843),
  new_x_y(-96.4243240356445,-570.302185058593),
  new_x_y(-96.5229263305664,-572.299743652343),
  new_x_y(-96.6215286254882,-574.297302246093),
  new_x_y(-96.7201309204101,-576.294860839843),
  new_x_y(-96.818733215332,-578.292419433593),
  new_x_y(-96.9173355102539,-580.2900390625),
  new_x_y(-97.0159378051757,-582.28759765625),
  new_x_y(-97.1145401000976,-584.28515625),
  new_x_y(-97.2131423950195,-586.28271484375),
  new_x_y(-97.3117446899414,-588.2802734375),
  new_x_y(-97.4103393554687,-590.27783203125),
  new_x_y(-97.5089416503906,-592.275390625),
  new_x_y(-97.6075439453125,-594.273010253906),
  new_x_y(-97.7061462402343,-596.270568847656),
  new_x_y(-97.8047485351562,-598.268127441406),
  new_x_y(-97.9033508300781,-600.265686035156),
  new_x_y(-98.001953125,-602.263244628906),
  new_x_y(-98.1005554199218,-604.260803222656),
  new_x_y(-98.1991577148437,-606.258422851562),
  new_x_y(-98.2977600097656,-608.255981445312),
  new_x_y(-98.3963623046875,-610.253540039062),
  new_x_y(-98.4949645996093,-612.251098632812),
  new_x_y(-98.5935668945312,-614.248657226562),
  new_x_y(-98.6921691894531,-616.246215820312),
  new_x_y(-98.790771484375,-618.243774414062),
  new_x_y(-98.8893737792968,-620.241394042968),
  new_x_y(-98.9879760742187,-622.238952636718),
  new_x_y(-99.0865783691406,-624.236511230468),
  new_x_y(-99.1851806640625,-626.234069824218),
  new_x_y(-99.2837829589843,-628.231628417968),
  new_x_y(-99.3823852539062,-630.229187011718),
  new_x_y(-99.4809875488281,-632.226806640625),
  new_x_y(-99.57958984375,-634.224365234375),
  new_x_y(-99.6781921386718,-636.221923828125),
  new_x_y(-99.7767944335937,-638.219482421875),
  new_x_y(-99.8753967285156,-640.217041015625),
  new_x_y(-99.9739990234375,-642.214599609375),
  new_x_y(-100.072601318359,-644.212158203125),
  new_x_y(-100.171203613281,-646.209777832031),
  new_x_y(-100.269805908203,-648.207336425781),
  new_x_y(-100.368408203125,-650.204895019531),
  new_x_y(-100.467010498046,-652.202453613281),
  new_x_y(-100.565612792968,-654.200012207031),
  new_x_y(-100.66421508789,-656.197631835937),
  new_x_y(-100.762817382812,-658.195190429687),
  new_x_y(-100.861419677734,-660.192749023437),
  new_x_y(-100.960021972656,-662.190307617187),
  new_x_y(-101.058624267578,-664.187866210937),
  new_x_y(-101.1572265625,-666.185424804687),
  new_x_y(-101.255828857421,-668.182983398437),
  new_x_y(-101.354431152343,-670.180541992187),
  new_x_y(-101.453033447265,-672.178161621093),
  new_x_y(-101.551628112792,-674.175720214843),
  new_x_y(-101.650230407714,-676.173278808593),
  new_x_y(-101.748832702636,-678.170837402343),
  new_x_y(-101.847434997558,-680.168395996093),
  new_x_y(-101.94603729248,-682.166015625),
  new_x_y(-102.044639587402,-684.16357421875),
  new_x_y(-102.143241882324,-686.1611328125),
  new_x_y(-102.241844177246,-688.15869140625),
  new_x_y(-102.340446472167,-690.15625),
  new_x_y(-102.439048767089,-692.15380859375),
  new_x_y(-102.537651062011,-694.1513671875),
  new_x_y(-102.636253356933,-696.14892578125),
  new_x_y(-102.734855651855,-698.146484375),
  new_x_y(-102.833457946777,-700.144104003906),
  new_x_y(-102.932060241699,-702.141662597656),
  new_x_y(-103.030662536621,-704.139221191406),
  new_x_y(-103.129264831542,-706.136779785156),
  new_x_y(-103.227867126464,-708.134399414062),
  new_x_y(-103.326469421386,-710.131958007812),
  new_x_y(-103.425071716308,-712.129516601562),
  new_x_y(-103.52367401123,-714.127075195312),
  new_x_y(-103.622276306152,-716.124633789062),
  new_x_y(-103.720878601074,-718.122192382812),
  new_x_y(-103.819480895996,-720.119750976562),
  new_x_y(-103.918083190917,-722.117309570312),
  new_x_y(-104.016685485839,-724.114868164062),
  new_x_y(-104.11528778076172, -726.1124877929688),
  new_x_y(-104.1638900756836, -728.1100463867188),
  new_x_y(-104.21249237060549, -730.1076049804688),
  new_x_y(-104.26109466552734, -732.1051635742188),
  new_x_y(-104.30969696044922, -734.1027221679688),
  new_x_y(-104.3582992553711, -736.100341796875),
  new_x_y(-104.40690155029296, -738.097900390625),
  new_x_y(-104.45550384521485, -740.095458984375),
  new_x_y(-104.50410614013671, -742.093017578125),
  new_x_y(-104.55270843505859, -744.090576171875),
  new_x_y(-104.60131072998048, -746.088134765625),
  new_x_y(-104.6499053955078, -748.085693359375),
  new_x_y(-104.69850769042968, -750.083251953125),
  new_x_y(-104.74710998535156, -752.0808715820312),
  new_x_y(-104.79571228027343, -754.0784301757812),
  new_x_y(-104.84431457519533, -756.0759887695312),
  new_x_y(-104.8929168701172, -758.0735473632812),
  new_x_y(-104.94151916503907, -760.0711059570312),
  new_x_y(-104.99012145996093, -762.0687255859375),
  new_x_y(-105.0387237548828, -764.0662841796875),
  new_x_y(-105.08732604980467, -766.0638427734375),
  new_x_y(-105.13592834472657, -768.0614013671875),
  new_x_y(-105.18453063964844, -770.0589599609375),
  new_x_y(-105.23313293457032, -772.0565185546875),
  new_x_y(-105.2817352294922, -774.0540771484375),
  new_x_y(-105.33033752441406, -776.0516357421875),
  new_x_y(-105.37893981933594, -778.0491943359375),
  new_x_y(-105.4275421142578, -780.0468139648438),
  new_x_y(-105.47614440917967, -782.0443725585938),
  new_x_y(-105.52474670410156, -784.0419311523438),
  new_x_y(-105.57334899902344, -786.03955078125),
  new_x_y(-105.62195129394533, -788.037109375),
  new_x_y(-105.67055358886721, -790.03466796875),
  new_x_y(-105.71915588378906, -792.0322265625),
  new_x_y(-105.76775817871093, -794.02978515625),
  new_x_y(-105.8163604736328, -796.02734375),
  new_x_y(-105.86496276855468, -798.02490234375),
  new_x_y(-105.91356506347657, -800.0224609375),
  new_x_y(-105.96216735839843, -802.02001953125),
  new_x_y(-106.01076965332032, -804.017578125),
  new_x_y(-106.0593719482422, -806.0151977539062),
  new_x_y(-106.10797424316407, -808.0127563476562),
  new_x_y(-106.15657653808594, -810.0103149414062),
  new_x_y(-106.20517883300779, -812.0079345703125),
  new_x_y(-106.25378112792967, -814.0054931640625),
  new_x_y(-106.30238342285156, -816.0030517578125),
  new_x_y(-106.35098571777344, -818.0006103515625),
  new_x_y(-106.39958801269533, -819.9981689453125),
  new_x_y(-106.4481903076172, -821.9957275390625),
  new_x_y(-106.49679260253906, -823.9932861328125),
  new_x_y(-106.54539489746094, -825.9908447265625),
  new_x_y(-106.6439971923828, -827.9884033203125),
  new_x_y(-106.74259948730467, -829.9859619140625),
  new_x_y(-106.84120178222656, -831.9835815429688),
  new_x_y(-106.93980407714844, -833.9811401367188),
  new_x_y(-107.03840637207033, -835.9786987304688),
  new_x_y(-107.13700103759766, -837.976318359375),
  new_x_y(-107.23560333251952, -839.973876953125),
  new_x_y(-107.33421325683594, -841.971435546875),
  new_x_y(-107.43280792236328, -843.968994140625),
  new_x_y(-107.53141021728516, -845.966552734375),
  new_x_y(-107.63001251220705, -847.964111328125),
  new_x_y(-107.7286148071289, -849.961669921875),
  new_x_y(-107.82721710205078, -851.959228515625),
  new_x_y(-107.92581939697266, -853.956787109375),
  new_x_y(-108.02442169189452, -855.954345703125),
  new_x_y(-108.1230239868164, -857.9519653320312),
  new_x_y(-108.22162628173828, -859.9495239257812),
  new_x_y(-108.32022857666016, -861.9470825195312),
  new_x_y(-108.41883087158205, -863.9447021484375),
  new_x_y(-108.5174331665039, -865.9422607421875),
  new_x_y(-108.61603546142578, -867.9398193359375),
  new_x_y(-108.71463775634766, -869.9373779296875),
  new_x_y(-108.81324005126952, -871.9349365234375),
  new_x_y(-108.9118423461914, -873.9324951171875),
  new_x_y(-109.01044464111328, -875.9300537109375),
  new_x_y(-109.10904693603516, -877.9276123046875),
  new_x_y(-109.20764923095705, -879.9251708984375),
  new_x_y(-109.3062515258789, -881.9227294921875),
  new_x_y(-109.40485382080078, -883.9203491210938),
  new_x_y(-109.50345611572266, -885.9179077148438),
  new_x_y(-109.60205841064452, -887.9154663085938),
  new_x_y(-109.7006607055664, -889.9130859375),
  new_x_y(-109.79926300048828, -891.91064453125),
  new_x_y(-109.89786529541016, -893.908203125),
  new_x_y(-109.99646759033205, -895.90576171875),
  new_x_y(-110.0950698852539, -897.9033203125),
  new_x_y(-110.19367218017578, -899.90087890625),
  new_x_y(-110.29227447509766, -901.8984375),
  new_x_y(-110.390869140625, -903.89599609375),
  new_x_y(-110.48947143554688, -905.8935546875),
  new_x_y(-110.58807373046876, -907.89111328125),
  new_x_y(-110.68667602539062, -909.8887329101562),
  new_x_y(-110.7852783203125, -911.8862915039062),
  new_x_y(-110.88388061523438, -913.8838500976562),
  new_x_y(-110.98248291015624, -915.8814697265624),
  new_x_y(-111.08108520507812, -917.8790283203124),
  new_x_y(-111.1796875, -919.8765869140624),
  new_x_y(-111.27828979492188, -921.8741455078124),
  new_x_y(-111.37689208984376, -923.8717041015624),
  new_x_y(-111.47549438476562, -925.8692626953124),
  new_x_y(-111.5740966796875, -927.8668212890624),
  new_x_y(-111.67269897460938, -929.8643798828124),
  new_x_y(-111.77130126953124, -931.8619384765624),
  new_x_y(-111.86990356445312, -933.8594970703124),
  new_x_y(-111.968505859375, -935.8571166992188),
  new_x_y(-112.06756591796876, -937.8546752929688),
  new_x_y(-112.17355346679688, -939.8518676757812),
  new_x_y(-112.2884521484375, -941.8485717773438),
  new_x_y(-112.4122314453125, -943.8447265625),
  new_x_y(-112.54489135742188, -945.84033203125),
  new_x_y(-112.68646240234376, -947.8353271484376),
  new_x_y(-112.8369140625, -949.8296508789062),
  new_x_y(-112.99624633789062, -951.8233032226562),
  new_x_y(-113.16445922851562, -953.8162231445312),
  new_x_y(-113.3515537600983, -955.8665279809941),
  new_x_y(-113.53996902717849, -957.9167117971767),
  new_x_y(-113.73102552986727, -959.9666510205336),
  new_x_y(-113.9260432892828, -962.0162169747531),
  new_x_y(-114.12634158750711, -964.0652733298231),
  new_x_y(-114.33323868289689, -966.1136735545402),
  new_x_y(-114.54805149255013, -968.1612583724475),
  new_x_y(-114.77209523374661, -970.2078532223375),
  new_x_y(-115.006683016202, -972.2532657246397),
  new_x_y(-115.25312537700373, -974.297283155235),
  new_x_y(-115.51272975013325, -976.3396699284953),
  new_x_y(-115.78679986252514, -978.3801650916428),
  new_x_y(-116.07663504867058, -980.4184798328554),
  new_x_y(-116.38352947584305, -982.4542950059051),
  new_x_y(-116.70877127210922, -984.4872586745246),
  new_x_y(-117.05364154939126, -986.5169836801274),
  new_x_y(-117.41941331396944, -988.5430452369803),
  new_x_y(-117.80735025695967, -990.5649785594276),
  new_x_y(-118.21870541747198, -992.5822765263035),
  new_x_y(-118.65471971135594, -994.5943873882336),
  new_x_y(-119.11662031867073, -996.6007125241229),
  new_x_y(-119.605618923285, -998.6006042537522),
  new_x_y(-120.12290979831764, -1000.5933637140547),
  new_x_y(-120.66966773147875, -1002.578238807317),
  new_x_y(-121.24704578476556, -1004.5544222302485),
  new_x_y(-121.85617288341206, -1006.5210495935763),
  new_x_y(-122.49815122949076, -1008.4771976425546),
  new_x_y(-123.17405353612175, -1010.4218825895213),
  new_x_y(-123.88492007886275, -1012.3540585703897),
  new_x_y(-124.63175556153985, -1014.2726162377194),
  new_x_y(-125.41552579453258, -1016.1763815037664),
  new_x_y(-126.23715418435646, -1018.064114447671),
  new_x_y(-127.0975180342922, -1019.9345084016783),
  new_x_y(-127.99744465679828, -1021.7861892320115),
  new_x_y(-129.29904174804688, -1024.0030168456112),
  new_x_y(-130.23733520507812, -1025.3253234392039),
  new_x_y(-131.21519470214844, -1026.6535923650738),
  new_x_y(-132.2321319580078, -1027.9847638155609),
  new_x_y(-133.28762817382812, -1029.3159715472532),
  new_x_y(-134.38116455078125, -1030.6445645242186),
  new_x_y(-135.51214599609375, -1031.9679987239151),
  new_x_y(-136.68003845214844, -1033.283986323702),
  new_x_y(-137.8842315673828, -1034.590318591403),
  new_x_y(-139.12411499023438, -1035.8849434285803),
  new_x_y(-140.3990478515625, -1037.1659199800672),
  new_x_y(-141.70838928222656, -1038.431439475185),
  new_x_y(-143.05148315429688, -1039.679798522091),
  new_x_y(-144.42764282226562, -1040.9093769333458),
  new_x_y(-145.83311462402344, -1042.1160772946891),
  new_x_y(-147.24366760253906, -1043.2797508701397),
  new_x_y(-148.6542205810547, -1044.398189605361),
  new_x_y(-150.0647735595703, -1045.4734179410927),
  new_x_y(-151.9115447998047, -1046.818879204404),
  new_x_y(-153.56297302246094, -1047.9649649606927),
  new_x_y(-155.27511596679688, -1049.0989259660173),
  new_x_y(-157.0152130126953, -1050.1971999910343),
  new_x_y(-158.78709411621094, -1051.261679878713),
  new_x_y(-160.56326293945312, -1052.2763142840188),
  new_x_y(-162.36941528320312, -1053.256244237683),
  new_x_y(-164.17236328125, -1054.1841280003594),
  new_x_y(-166.06207275390625, -1055.1045175025336),
  new_x_y(-167.92999267578125, -1055.963504145741),
  new_x_y(-169.81085205078125, -1056.7789530599423),
  new_x_y(-171.71499633789062, -1057.555335983251),
  new_x_y(-173.6272430419922, -1058.2865596520683),
  new_x_y(-175.54446411132812, -1058.9721381371337),
  new_x_y(-177.5172576904297, -1059.6290460067014),
  new_x_y(-179.49436950683594, -1060.2390685602497),
  new_x_y(-181.5004119873047, -1060.80958016515),
  new_x_y(-183.51683044433597, -1061.3347975878194),
  new_x_y(-185.5426788330078, -1061.8146020439071),
  new_x_y(-187.5782928466797, -1062.2491491193605),
  new_x_y(-189.625, -1062.6386692708334),
  new_x_y(-191.70413208007807, -1062.9863178358407),
  new_x_y(-193.7519073486328, -1063.2819196173116),
  new_x_y(-195.80239868164065, -1063.5318193259066),
  new_x_y(-197.89547729492188, -1063.7397222603213),
  new_x_y(-199.98516845703125, -1063.9000472976386),
  new_x_y(-202.0535888671875, -1064.0124941221452),
  new_x_y(-204.19088745117188, -1064.0805283660864),
  new_x_y(-206.28028869628903, -1064.0998263672855),
  new_x_y(-208.3740997314453, -1064.0723702297396),
  new_x_y(-210.478515625, -1063.9975325926928),
  new_x_y(-212.55540466308597, -1063.8771264852148),
  new_x_y(-214.64825439453125, -1063.708837278481),
  new_x_y(-216.74729919433597, -1063.4924460365803),
  new_x_y(-218.8514862060547, -1063.2273400866045),
  new_x_y(-220.93853759765625, -1062.9163286544263),
  new_x_y(-223.02557373046875, -1062.5569658086474),
  new_x_y(-225.13626098632807, -1062.1437710248788),
  new_x_y(-227.19061279296875, -1061.6929057110094),
  new_x_y(-229.30372619628903, -1061.1782614004462),
  new_x_y(-231.394821166992,-1060.39245605468),
  new_x_y(-233.479858398437,-1059.93676757812),
  new_x_y(-235.452316284179,-1059.46057128906),
  new_x_y(-237.548873901367,-1058.95886230468),
  new_x_y(-239.592651367187,-1058.361328125),
  new_x_y(-241.650329589843,-1057.78479003906),
  new_x_y(-243.68374633789,-1057.12170410156),
  new_x_y(-245.70344543457,-1056.46740722656),
  new_x_y(-247.603805541992,-1055.828125),
  new_x_y(-249.591751098632,-1055.07885742187),
  new_x_y(-251.556182861328,-1054.29602050781),
  new_x_y(-253.527450561523,-1053.48071289062),
  new_x_y(-255.447509765625,-1052.60034179687),
  new_x_y(-257.362274169921,-1051.70666503906),
  new_x_y(-259.260040283203,-1050.7177734375),
  new_x_y(-261.134887695312,-1049.72375488281),
  new_x_y(-262.943969726562,-1048.6640625),
  new_x_y(-264.724792480468,-1047.52429199218),
  new_x_y(-266.505065917968,-1046.37524414062),
  new_x_y(-268.223602294921,-1045.14611816406),
  new_x_y(-269.97378540039,-1043.91845703125),
  new_x_y(-271.704284667968,-1042.70471191406),
  new_x_y(-273.460418701171,-1041.47326660156),
  new_x_y(-275.233581542968,-1040.23010253906),
  new_x_y(-276.994445800781,-1038.99499511718),
  new_x_y(-278.763641357421,-1037.75463867187),
  new_x_y(-280.389617919921,-1036.572265625),
  new_x_y(-282.118591308593,-1035.27490234375),
  new_x_y(-283.785339355468,-1033.896484375),
  new_x_y(-285.290985107421,-1032.57507324218),
  new_x_y(-286.876800537109,-1031.08203125),
  new_x_y(-288.355346679687,-1029.71142578125),
  new_x_y(-289.817291259765,-1028.26049804687),
  new_x_y(-291.263610839843,-1026.84057617187),
  new_x_y(-292.681488037109,-1025.37573242187),
  new_x_y(-294.08901977539,-1023.86694335937),
  new_x_y(-295.489624023437,-1022.3735961914),
  new_x_y(-296.891540527343,-1020.87878417968),
  new_x_y(-298.304321289062,-1019.37225341796),
  new_x_y(-299.731292724609,-1017.85125732421),
  new_x_y(-301.1484375,-1016.34045410156),
  new_x_y(-302.563110351562,-1014.83203125),
  new_x_y(-304.00830078125,-1013.29119873046),
  new_x_y(-305.39859008789,-1011.75604248046),
  new_x_y(-306.8076171875,-1010.21203613281),
  new_x_y(-308.1435546875,-1008.61224365234),
  new_x_y(-309.465057373046,-1007.03491210937),
  new_x_y(-310.75991821289,-1005.41522216796),
  new_x_y(-312.044830322265,-1003.7866821289),
  new_x_y(-313.356872558593,-1002.06475830078),
  new_x_y(-314.643157958984,-1000.318359375),
  new_x_y(-315.846252441406,-998.495361328125),
  new_x_y(-317.005676269531,-996.772155761718),
  new_x_y(-318.16616821289,-995.048583984375),
  new_x_y(-319.290100097656,-993.3046875),
  new_x_y(-320.421569824218,-991.5107421875),
  new_x_y(-321.517059326171,-989.779174804687),
  new_x_y(-322.620727539062,-988.033630371093),
  new_x_y(-323.74072265625,-986.262329101562),
  new_x_y(-324.852874755859,-984.503662109375),
  new_x_y(-325.962677001953,-982.748168945312),
  new_x_y(-327.082977294921,-980.977233886718),
  new_x_y(-328.205261230468,-979.202819824218),
  new_x_y(-329.316528320312,-977.445434570312),
  new_x_y(-330.402404785156,-975.632019042968),
  new_x_y(-331.46240234375,-973.832458496093),
  new_x_y(-332.480346679687,-972.024536132812),
  new_x_y(-333.418365478515,-970.172729492187),
  new_x_y(-334.365997314453,-968.34130859375),
  new_x_y(-335.221740722656,-966.456909179687),
  new_x_y(-335.97280883789,-964.534912109375),
  new_x_y(-336.662811279296,-962.573425292968),
  new_x_y(-337.187377929687,-960.572387695312),
  new_x_y(-337.756744384765,-958.539611816406),
  new_x_y(-338.331604003906,-956.540771484375),
  new_x_y(-338.96401977539,-954.568420410156),
  new_x_y(-339.584594726562,-952.584655761718),
  new_x_y(-340.218627929687,-950.572875976562),
  new_x_y(-340.914184570312,-948.612976074218),
  new_x_y(-341.589447021484,-946.657958984375),
  new_x_y(-342.290954589843,-944.642761230468),
  new_x_y(-343.044128417968,-942.705078125),
  new_x_y(-343.781463623046,-940.760192871093),
  new_x_y(-344.519866943359,-938.810546875),
  new_x_y(-345.264343261718,-936.846252441406),
  new_x_y(-345.937103271484,-934.87841796875),
  new_x_y(-346.619567871093,-932.898498535156),
  new_x_y(-347.32763671875,-930.937866210937),
  new_x_y(-348.032897949218,-928.979797363281),
  new_x_y(-348.74560546875,-927.00146484375),
  new_x_y(-349.450592041015,-925.042541503906),
  new_x_y(-350.163848876953,-923.061828613281),
  new_x_y(-350.859405517578,-921.019409179687),
  new_x_y(-351.546478271484,-919.013000488281),
  new_x_y(-352.117309570312,-917.012023925781),
  new_x_y(-352.711547851562,-914.997497558593),
  new_x_y(-353.228515625,-912.981201171875),
  new_x_y(-353.764007568359,-910.939697265625),
  new_x_y(-354.243896484375,-908.886413574218),
  new_x_y(-354.721160888671,-906.810607910156),
  new_x_y(-355.19287109375,-904.762939453125),
  new_x_y(-355.6669921875,-902.706359863281),
  new_x_y(-356.14663696289,-900.621398925781),
  new_x_y(-356.597381591796,-898.548156738281),
  new_x_y(-356.99951171875,-896.483154296875),
  new_x_y(-357.419769287109,-894.369689941406),
  new_x_y(-357.817504882812,-892.29833984375),
  new_x_y(-358.1552734375,-890.197875976562),
  new_x_y(-358.516448974609,-888.047180175781),
  new_x_y(-358.831665039062,-885.93896484375),
  new_x_y(-359.151763916015,-883.851928710937),
  new_x_y(-359.44351196289,-881.719604492187),
  new_x_y(-359.697265625,-879.625427246093),
  new_x_y(-359.956665039062,-877.520812988281),
  new_x_y(-360.056457519531,-875.356079101562),
  new_x_y(-360.308074951171,-873.371948242187),
  new_x_y(-360.5517578125,-871.386840820312),
  new_x_y(-360.787506103515,-869.400817871093),
  new_x_y(-361.01528930664,-867.413818359375),
  new_x_y(-361.235107421875,-865.425964355468),
  new_x_y(-361.447021484375,-863.437194824218),
  new_x_y(-361.650939941406,-861.447631835937),
  new_x_y(-361.846923828125,-859.457275390625),
  new_x_y(-362.034912109375,-857.466125488281),
  new_x_y(-362.214965820312,-855.474243164062),
  new_x_y(-362.387023925781,-853.481628417968),
  new_x_y(-362.551116943359,-851.488403320312),
  new_x_y(-362.707244873046,-849.494506835937),
  new_x_y(-362.855407714843,-847.5),
  new_x_y(-362.996398925781,-845.504943847656),
  new_x_y(-363.136291503906,-843.509887695312),
  new_x_y(-363.276153564453,-841.514770507812),
  new_x_y(-363.416015625,-839.519653320312),
  new_x_y(-363.555877685546,-837.524536132812),
  new_x_y(-363.695770263671,-835.529479980468),
  new_x_y(-363.835632324218,-833.534362792968),
  new_x_y(-363.975494384765,-831.539245605468),
  new_x_y(-364.115356445312,-829.544128417968),
  new_x_y(-364.255249023437,-827.549072265625),
  new_x_y(-364.395111083984,-825.553955078125),
  new_x_y(-364.534973144531,-823.558837890625),
  new_x_y(-364.674835205078,-821.563720703125),
  new_x_y(-364.814727783203,-819.568603515625),
  new_x_y(-364.95458984375,-817.573547363281),
  new_x_y(-365.094451904296,-815.578430175781),
  new_x_y(-365.234313964843,-813.583312988281),
  new_x_y(-365.374206542968,-811.588195800781),
  new_x_y(-365.514068603515,-809.593139648437),
  new_x_y(-365.653930664062,-807.598022460937),
  new_x_y(-365.793792724609,-805.602905273437),
  new_x_y(-365.933685302734,-803.607788085937),
  new_x_y(-366.073547363281,-801.612670898437),
  new_x_y(-366.213409423828,-799.617614746093),
  new_x_y(-366.353271484375,-797.622497558593),
  new_x_y(-366.4931640625,-795.627380371093),
  new_x_y(-366.633026123046,-793.632263183593),
  new_x_y(-366.772888183593,-791.63720703125),
  new_x_y(-366.91275024414,-789.64208984375),
  new_x_y(-367.052642822265,-787.64697265625),
  new_x_y(-367.192504882812,-785.65185546875),
  new_x_y(-367.332366943359,-783.656799316406),
  new_x_y(-367.472229003906,-781.661682128906),
  new_x_y(-367.612121582031,-779.666564941406),
  new_x_y(-367.751983642578,-777.671447753906),
  new_x_y(-367.891845703125,-775.676391601562),
  new_x_y(-368.03173828125,-773.681274414062),
  new_x_y(-368.171600341796,-771.686157226562),
  new_x_y(-368.311462402343,-769.691040039062),
  new_x_y(-368.448944091796,-767.69580078125),
  new_x_y(-368.578643798828,-765.700012207031),
  new_x_y(-368.700378417968,-763.703735351562),
  new_x_y(-368.81411743164,-761.706970214843),
  new_x_y(-368.919860839843,-759.709777832031),
  new_x_y(-369.017639160156,-757.712158203125),
  new_x_y(-369.107452392578,-755.714111328125),
  new_x_y(-369.19400024414,-753.716003417968),
  new_x_y(-369.280578613281,-751.717895507812),
  new_x_y(-369.367126464843,-749.719787597656),
  new_x_y(-369.453704833984,-747.721618652343),
  new_x_y(-369.540252685546,-745.723510742187),
  new_x_y(-369.626831054687,-743.725402832031),
  new_x_y(-369.713409423828,-741.727233886718),
  new_x_y(-369.79995727539,-739.729125976562),
  new_x_y(-369.886535644531,-737.731018066406),
  new_x_y(-369.973083496093,-735.73291015625),
  new_x_y(-370.059661865234,-733.734741210937),
  new_x_y(-370.146209716796,-731.736633300781),
  new_x_y(-370.232788085937,-729.738525390625),
  new_x_y(-370.319366455078,-727.740356445312),
  new_x_y(-370.40591430664,-725.742248535156),
  new_x_y(-370.492492675781,-723.744140625),
  new_x_y(-370.579040527343,-721.745971679687),
  new_x_y(-370.665618896484,-719.747863769531),
  new_x_y(-370.752166748046,-717.749755859375),
  new_x_y(-370.838745117187,-715.751647949218),
  new_x_y(-370.92529296875,-713.753479003906),
  new_x_y(-371.01187133789,-711.75537109375),
  new_x_y(-371.098449707031,-709.757263183593),
  new_x_y(-371.184997558593,-707.759094238281),
  new_x_y(-371.271575927734,-705.760986328125),
  new_x_y(-371.358123779296,-703.762878417968),
  new_x_y(-371.444702148437,-701.764770507812),
  new_x_y(-371.53125,-699.7666015625),
  new_x_y(-371.61782836914,-697.768493652343),
  new_x_y(-371.704406738281,-695.770385742187),
  new_x_y(-371.790954589843,-693.772216796875),
  new_x_y(-371.877532958984,-691.774108886718),
  new_x_y(-371.964080810546,-689.776000976562),
  new_x_y(-372.050659179687,-687.77783203125),
  new_x_y(-372.135681152343,-685.779663085937),
  new_x_y(-372.213256835937,-683.781188964843),
  new_x_y(-372.28286743164,-681.782409667968),
  new_x_y(-372.344451904296,-679.783325195312),
  new_x_y(-372.398040771484,-677.784057617187),
  new_x_y(-372.443634033203,-675.784606933593),
  new_x_y(-372.481262207031,-673.784973144531),
  new_x_y(-372.510864257812,-671.78515625),
  new_x_y(-372.532440185546,-669.785278320312),
  new_x_y(-372.54605102539,-667.785339355468),
  new_x_y(-372.551666259765,-665.785339355468),
  new_x_y(-372.549255371093,-663.785339355468),
  new_x_y(-372.538848876953,-661.785400390625),
  new_x_y(-372.520477294921,-659.785461425781),
  new_x_y(-372.494079589843,-657.78564453125),
  new_x_y(-372.459686279296,-655.785949707031),
  new_x_y(-372.417266845703,-653.786376953125),
  new_x_y(-372.366882324218,-651.787048339843),
  new_x_y(-372.308502197265,-649.787902832031),
  new_x_y(-372.242126464843,-647.789001464843),
  new_x_y(-372.167724609375,-645.790344238281),
  new_x_y(-372.085357666015,-643.792053222656),
  new_x_y(-371.994995117187,-641.794128417968),
  new_x_y(-371.901214599609,-639.796325683593),
  new_x_y(-371.807434082031,-637.798522949218),
  new_x_y(-371.713623046875,-635.800720214843),
  new_x_y(-371.619842529296,-633.802917480468),
  new_x_y(-371.526062011718,-631.805114746093),
  new_x_y(-371.43228149414,-629.807312011718),
  new_x_y(-371.338470458984,-627.809509277343),
  new_x_y(-371.244689941406,-625.811706542968),
  new_x_y(-371.150909423828,-623.813903808593),
  new_x_y(-371.05712890625,-621.816101074218),
  new_x_y(-370.963317871093,-619.818298339843),
  new_x_y(-370.869537353515,-617.820495605468),
  new_x_y(-370.775756835937,-615.822692871093),
  new_x_y(-370.681976318359,-613.824890136718),
  new_x_y(-370.588195800781,-611.8271484375),
  new_x_y(-370.494384765625,-609.829345703125),
  new_x_y(-370.400604248046,-607.83154296875),
  new_x_y(-370.306823730468,-605.833740234375),
  new_x_y(-370.21304321289,-603.8359375),
  new_x_y(-370.119232177734,-601.838134765625),
  new_x_y(-370.025451660156,-599.84033203125),
  new_x_y(-369.931671142578,-597.842529296875),
  new_x_y(-369.837890625,-595.8447265625),
  new_x_y(-369.744079589843,-593.846923828125),
  new_x_y(-369.650299072265,-591.84912109375),
  new_x_y(-369.556518554687,-589.851318359375),
  new_x_y(-369.462738037109,-587.853515625),
  new_x_y(-369.368957519531,-585.855712890625),
  new_x_y(-369.275146484375,-583.85791015625),
  new_x_y(-369.181365966796,-581.860107421875),
  new_x_y(-369.087585449218,-579.8623046875),
  new_x_y(-368.99380493164,-577.864501953125),
  new_x_y(-368.899993896484,-575.86669921875),
  new_x_y(-368.806213378906,-573.868896484375),
  new_x_y(-368.712432861328,-571.87109375),
  new_x_y(-368.61865234375,-569.873291015625),
  new_x_y(-368.524841308593,-567.875549316406),
  new_x_y(-368.431060791015,-565.877746582031),
  new_x_y(-368.337280273437,-563.879943847656),
  new_x_y(-368.243499755859,-561.882141113281),
  new_x_y(-368.149719238281,-559.884338378906),
  new_x_y(-368.055908203125,-557.886535644531),
  new_x_y(-367.962127685546,-555.888732910156),
  new_x_y(-367.868347167968,-553.890930175781),
  new_x_y(-367.77456665039,-551.893127441406),
  new_x_y(-367.680755615234,-549.895324707031),
  new_x_y(-367.586975097656,-547.897521972656),
  new_x_y(-367.493194580078,-545.899719238281),
  new_x_y(-367.3994140625,-543.901916503906),
  new_x_y(-367.305603027343,-541.904113769531),
  new_x_y(-367.211822509765,-539.906311035156),
  new_x_y(-367.118041992187,-537.908508300781),
  new_x_y(-367.024261474609,-535.910705566406),
  new_x_y(-366.930450439453,-533.912902832031),
  new_x_y(-366.836669921875,-531.915161132812),
  new_x_y(-366.742889404296,-529.917358398437),
  new_x_y(-366.649108886718,-527.919555664062),
  new_x_y(-366.55532836914,-525.921752929687),
  new_x_y(-366.461517333984,-523.923950195312),
  new_x_y(-366.367736816406,-521.926147460937),
  new_x_y(-366.273956298828,-519.928344726562),
  new_x_y(-366.18017578125,-517.930541992187),
  new_x_y(-366.086364746093,-515.932739257812),
  new_x_y(-365.992584228515,-513.934936523437),
  new_x_y(-365.898803710937,-511.937133789062),
  new_x_y(-365.805023193359,-509.939331054687),
  new_x_y(-365.711212158203,-507.941528320312),
  new_x_y(-365.617431640625,-505.943725585937),
  new_x_y(-365.523651123046,-503.945922851562),
  new_x_y(-365.429870605468,-501.948120117187),
  new_x_y(-365.33609008789,-499.950317382812),
  new_x_y(-365.242279052734,-497.952514648437),
  new_x_y(-365.148498535156,-495.954711914062),
  new_x_y(-365.054718017578,-493.956909179687),
  new_x_y(-364.9609375,-491.95913696289),
  new_x_y(-364.867126464843,-489.961334228515),
  new_x_y(-364.773345947265,-487.96353149414),
  new_x_y(-364.679565429687,-485.965728759765),
  new_x_y(-364.585784912109,-483.96792602539),
  new_x_y(-364.491973876953,-481.970153808593),
  new_x_y(-364.398193359375,-479.972351074218),
  new_x_y(-364.304412841796,-477.974548339843),
  new_x_y(-364.210632324218,-475.976745605468),
  new_x_y(-364.116821289062,-473.978942871093),
  new_x_y(-364.023040771484,-471.981140136718),
  new_x_y(-363.929260253906,-469.983337402343),
  new_x_y(-363.835479736328,-467.985534667968),
  new_x_y(-363.74169921875,-465.987731933593),
  new_x_y(-363.647888183593,-463.989929199218),
  new_x_y(-363.554107666015,-461.992126464843),
  new_x_y(-363.460327148437,-459.994323730468),
  new_x_y(-363.366546630859,-457.996520996093),
  new_x_y(-363.272735595703,-455.998718261718),
  new_x_y(-363.178955078125,-454.000915527343),
  new_x_y(-363.085174560546,-452.003143310546),
  new_x_y(-362.991394042968,-450.005340576171),
  new_x_y(-362.897583007812,-448.007537841796),
  new_x_y(-362.803802490234,-446.009735107421),
  new_x_y(-362.710021972656,-444.011932373046),
  new_x_y(-362.616241455078,-442.01416015625),
  new_x_y(-362.5224609375,-440.016357421875),
  new_x_y(-362.428649902343,-438.0185546875),
  new_x_y(-362.334869384765,-436.020751953125),
  new_x_y(-362.241088867187,-434.02294921875),
  new_x_y(-362.147308349609,-432.025146484375),
  new_x_y(-362.053497314453,-430.02734375),
  new_x_y(-361.959716796875,-428.029541015625),
  new_x_y(-361.865936279296,-426.03173828125),
  new_x_y(-361.772155761718,-424.033935546875),
  new_x_y(-361.678344726562,-422.0361328125),
  new_x_y(-361.584564208984,-420.038330078125),
  new_x_y(-361.490783691406,-418.04052734375),
  new_x_y(-361.397003173828,-416.042724609375),
  new_x_y(-361.30322265625,-414.044921875),
  new_x_y(-361.209411621093,-412.047119140625),
  new_x_y(-361.115631103515,-410.049346923828),
  new_x_y(-361.021850585937,-408.051544189453),
  new_x_y(-360.928070068359,-406.053741455078),
  new_x_y(-360.834259033203,-404.055938720703),
  new_x_y(-360.740478515625,-402.058135986328),
  new_x_y(-360.646697998046,-400.060363769531),
  new_x_y(-360.552917480468,-398.062561035156),
  new_x_y(-360.459106445312,-396.064758300781),
  new_x_y(-360.365325927734,-394.066955566406),
  new_x_y(-360.271545410156,-392.069152832031),
  new_x_y(-360.177764892578,-390.071350097656),
  new_x_y(-360.083953857421,-388.073547363281),
  new_x_y(-359.990173339843,-386.075744628906),
  new_x_y(-359.896392822265,-384.077941894531),
  new_x_y(-359.802612304687,-382.080139160156),
  new_x_y(-359.708831787109,-380.082336425781),
  new_x_y(-359.615020751953,-378.084533691406),
  new_x_y(-359.521240234375,-376.086730957031),
  new_x_y(-359.427459716796,-374.088958740234),
  new_x_y(-359.333679199218,-372.091156005859),
  new_x_y(-359.239868164062,-370.093353271484),
  new_x_y(-359.146087646484,-368.095550537109),
  new_x_y(-359.052307128906,-366.097747802734),
  new_x_y(-358.958526611328,-364.099945068359),
  new_x_y(-358.864715576171,-362.102142333984),
  new_x_y(-358.770935058593,-360.104339599609),
  new_x_y(-358.677154541015,-358.106536865234),
  new_x_y(-358.583374023437,-356.108734130859),
  new_x_y(-358.489562988281,-354.110961914062),
  new_x_y(-358.395782470703,-352.113159179687),
  new_x_y(-358.302001953125,-350.115356445312),
  new_x_y(-358.208221435546,-348.117553710937),
  new_x_y(-358.114440917968,-346.119750976562),
  new_x_y(-358.020629882812,-344.121948242187),
  new_x_y(-357.926849365234,-342.124145507812),
  new_x_y(-357.833068847656,-340.126342773437),
  new_x_y(-357.739288330078,-338.128540039062),
  new_x_y(-357.645477294921,-336.130737304687),
  new_x_y(-357.551696777343,-334.13296508789),
  new_x_y(-357.457916259765,-332.135162353515),
  new_x_y(-357.364135742187,-330.13735961914),
  new_x_y(-357.270324707031,-328.139556884765),
  new_x_y(-357.176544189453,-326.14175415039),
  new_x_y(-357.082763671875,-324.143951416015),
  new_x_y(-356.988983154296,-322.14614868164),
  new_x_y(-356.895202636718,-320.148345947265),
  new_x_y(-356.801391601562,-318.15054321289),
  new_x_y(-356.707611083984,-316.152740478515),
  new_x_y(-356.613830566406,-314.154968261718),
  new_x_y(-356.520050048828,-312.157165527343),
  new_x_y(-356.426239013671,-310.159362792968),
  new_x_y(-356.332458496093,-308.161560058593),
  new_x_y(-356.238677978515,-306.163757324218),
  new_x_y(-356.144897460937,-304.165954589843),
  new_x_y(-356.051086425781,-302.168151855468),
  new_x_y(-355.957305908203,-300.170349121093),
  new_x_y(-355.863525390625,-298.172546386718),
  new_x_y(-355.769744873046,-296.174743652343),
  new_x_y(-355.675964355468,-294.176940917968),
  new_x_y(-355.582153320312,-292.179168701171),
  new_x_y(-355.488372802734,-290.181365966796),
  new_x_y(-355.394592285156,-288.183563232421),
  new_x_y(-355.300811767578,-286.185760498046),
  new_x_y(-355.207000732421,-284.187957763671),
  new_x_y(-355.113220214843,-282.190155029296),
  new_x_y(-355.019439697265,-280.192352294921),
  new_x_y(-354.925659179687,-278.194549560546),
  new_x_y(-354.831848144531,-276.196746826171),
  new_x_y(-354.738067626953,-274.198944091796),
  new_x_y(-354.644287109375,-272.201171875),
  new_x_y(-354.550506591796,-270.203369140625),
  new_x_y(-354.456726074218,-268.20556640625),
  new_x_y(-354.362915039062,-266.207763671875),
  new_x_y(-354.269134521484,-264.2099609375),
  new_x_y(-354.175354003906,-262.212158203125),
  new_x_y(-354.081573486328,-260.21435546875),
  new_x_y(-353.987762451171,-258.216552734375),
  new_x_y(-353.893981933593,-256.21875),
  new_x_y(-353.800201416015,-254.220947265625),
  new_x_y(-353.706420898437,-252.223175048828),
  new_x_y(-353.612609863281,-250.225372314453),
  new_x_y(-353.518829345703,-248.227569580078),
  new_x_y(-353.425170898437,-246.229736328125),
  new_x_y(-353.336547851562,-244.231704711914),
  new_x_y(-353.255920410156,-242.233337402343),
  new_x_y(-353.183288574218,-240.234649658203),
  new_x_y(-353.116302490234,-238.235778808593),
  new_x_y(-353.049591064453,-236.236892700195),
  new_x_y(-352.982879638671,-234.238006591796),
  new_x_y(-352.91616821289,-232.239120483398),
  new_x_y(-352.849456787109,-230.240234375),
  new_x_y(-352.782745361328,-228.241348266601),
  new_x_y(-352.716033935546,-226.242462158203),
  new_x_y(-352.649322509765,-224.243576049804),
  new_x_y(-352.582611083984,-222.244689941406),
  new_x_y(-352.515869140625,-220.245803833007),
  new_x_y(-352.449157714843,-218.246917724609),
  new_x_y(-352.382446289062,-216.24803161621),
  new_x_y(-352.315734863281,-214.249145507812),
  new_x_y(-352.2490234375,-212.250244140625),
  new_x_y(-352.182312011718,-210.251373291015),
  new_x_y(-352.115600585937,-208.252471923828),
  new_x_y(-352.048889160156,-206.253601074218),
  new_x_y(-351.982177734375,-204.254699707031),
  new_x_y(-351.915435791015,-202.255813598632),
  new_x_y(-351.848724365234,-200.256927490234),
  new_x_y(-351.782012939453,-198.258041381835),
  new_x_y(-351.715301513671,-196.259155273437),
  new_x_y(-351.64859008789,-194.260269165039),
  new_x_y(-351.581878662109,-192.26138305664),
  new_x_y(-351.515167236328,-190.262496948242),
  new_x_y(-351.448455810546,-188.263610839843),
  new_x_y(-351.381744384765,-186.264724731445),
  new_x_y(-351.315002441406,-184.265838623046),
  new_x_y(-351.248291015625,-182.266952514648),
  new_x_y(-351.181579589843,-180.26806640625),
  new_x_y(-351.114868164062,-178.269165039062),
  new_x_y(-351.048156738281,-176.270294189453),
  new_x_y(-350.9814453125,-174.271392822265),
  new_x_y(-350.914733886718,-172.272521972656),
  new_x_y(-350.848022460937,-170.273620605468),
  new_x_y(-350.781311035156,-168.274749755859),
  new_x_y(-350.714569091796,-166.275848388671),
  new_x_y(-350.647857666015,-164.276962280273),
  new_x_y(-350.581146240234,-162.278076171875),
  new_x_y(-350.514434814453,-160.279190063476),
  new_x_y(-350.447723388671,-158.280303955078),
  new_x_y(-350.38101196289,-156.281417846679),
  new_x_y(-350.314300537109,-154.282531738281),
  new_x_y(-350.247589111328,-152.283645629882),
  new_x_y(-350.180877685546,-150.284759521484),
  new_x_y(-350.114135742187,-148.285858154296),
  new_x_y(-350.047424316406,-146.286987304687),
  new_x_y(-349.980712890625,-144.2880859375),
  new_x_y(-349.914001464843,-142.28921508789),
  new_x_y(-349.847290039062,-140.290313720703),
  new_x_y(-349.780578613281,-138.291442871093),
  new_x_y(-349.7138671875,-136.292541503906),
  new_x_y(-349.647155761718,-134.293670654296),
  new_x_y(-349.580444335937,-132.294769287109),
  new_x_y(-349.513702392578,-130.29588317871),
  new_x_y(-349.446990966796,-128.296997070312),
  new_x_y(-349.380279541015,-126.298110961914),
  new_x_y(-349.313568115234,-124.299224853515),
  new_x_y(-349.246856689453,-122.300338745117),
  new_x_y(-349.180145263671,-120.301452636718),
  new_x_y(-349.11343383789,-118.30256652832),
  new_x_y(-349.046722412109,-116.303680419921),
  new_x_y(-348.980010986328,-114.304794311523),
  new_x_y(-348.913269042968,-112.30590057373),
  new_x_y(-348.846557617187,-110.307022094726),
  new_x_y(-348.779846191406,-108.308135986328),
  new_x_y(-348.713134765625,-106.309249877929),
  new_x_y(-348.646423339843,-104.310363769531),
  new_x_y(-348.579711914062,-102.311462402343),
  new_x_y(-348.513000488281,-100.312576293945),
  new_x_y(-348.4462890625,-98.3136901855468),
  new_x_y(-348.379577636718,-96.3148040771484),
  new_x_y(-348.312835693359,-94.31591796875),
  new_x_y(-348.246124267578,-92.3170318603515),
  new_x_y(-348.179412841796,-90.3181457519531),
  new_x_y(-348.112701416015,-88.3192596435546),
  new_x_y(-348.045989990234,-86.3203735351562),
  new_x_y(-347.979278564453,-84.3214874267578),
  new_x_y(-347.912567138671,-82.3226013183593),
  new_x_y(-347.84585571289,-80.3237152099609),
  new_x_y(-347.779144287109,-78.3248291015625),
  new_x_y(-347.71240234375,-76.325942993164),
  new_x_y(-347.645690917968,-74.3270568847656),
  new_x_y(-347.578979492187,-72.3281707763671),
  new_x_y(-347.512268066406,-70.3292846679687),
  new_x_y(-347.445556640625,-68.3303833007812),
  new_x_y(-347.378845214843,-66.3314971923828),
  new_x_y(-347.312133789062,-64.3326110839843),
  new_x_y(-347.245422363281,-62.3337249755859),
  new_x_y(-347.1787109375,-60.3348388671875),
  new_x_y(-347.11196899414,-58.335952758789),
  new_x_y(-347.045257568359,-56.3370666503906),
  new_x_y(-346.978546142578,-54.3381805419921),
  new_x_y(-346.911834716796,-52.3392944335937),
  new_x_y(-346.845123291015,-50.3404083251953),
  new_x_y(-346.778411865234,-48.3415222167968),
  new_x_y(-346.711700439453,-46.3426361083984),
  new_x_y(-346.644989013671,-44.34375),
  new_x_y(-346.578247070312,-42.3448638916015),
  new_x_y(-346.511535644531,-40.3459777832031),
  new_x_y(-346.44482421875,-38.3470916748046),
  new_x_y(-346.378112792968,-36.3482055664062),
  new_x_y(-346.311401367187,-34.3493194580078),
  new_x_y(-346.244689941406,-32.3504180908203),
  new_x_y(-346.177978515625,-30.3515319824218),
  new_x_y(-346.111267089843,-28.3526458740234),
  new_x_y(-346.044555664062,-26.353759765625),
  new_x_y(-345.977813720703,-24.3548736572265),
  new_x_y(-345.911102294921,-22.3559875488281),
  new_x_y(-345.84439086914,-20.3571014404296),
  new_x_y(-345.777679443359,-18.3582153320312),
  new_x_y(-345.710968017578,-16.3593292236328),
  new_x_y(-345.644256591796,-14.3604431152343),
  new_x_y(-345.577545166015,-12.3615570068359),
  new_x_y(-345.510833740234,-10.3626708984375),
  new_x_y(-345.444122314453,-8.36378479003906),
  new_x_y(-345.377380371093,-6.36489868164062),
  new_x_y(-345.310668945312,-4.36601257324218),
  new_x_y(-345.243957519531,-2.36712646484375),
  new_x_y(-345.17724609375,-0.368240356445312),
  new_x_y(-345.110534667968, 1.630645751953125),
  new_x_y(-345.043823242187, 3.629547119140625),
  new_x_y(-344.977111816406, 5.6284332275390625),
  new_x_y(-344.910400390625,7.6273193359375),
  new_x_y(-344.843688964843, 9.626205444335938),
  new_x_y(-344.776947021484, 11.625091552734375),
  new_x_y(-344.710235595703, 13.623977661132812),
  new_x_y(-344.643524169921, 15.62286376953125),
  new_x_y(-344.57681274414, 17.621749877929688),
  new_x_y(-344.510101318359, 19.620651245117188),
  new_x_y(-344.443389892578, 21.619522094726562),
  new_x_y(-344.376678466796, 23.618423461914062),
  new_x_y(-344.309967041015, 25.617294311523438),
  new_x_y(-344.243255615234, 27.616195678710938),
  new_x_y(-344.176513671875, 29.615066528320312),
  new_x_y(-344.109802246093, 31.613967895507812),
  new_x_y(-344.043090820312, 33.61283874511719),
  new_x_y(-343.976379394531, 35.61174011230469),
  new_x_y(-343.90966796875, 37.61061096191406),
  new_x_y(-343.842956542968, 39.60951232910156),
  new_x_y(-343.776245117187, 41.60838317871094),
  new_x_y(-343.709533691406, 43.60728454589844),
  new_x_y(-343.642822265625, 45.60615539550781),
  new_x_y(-343.56, 47.4),
  new_x_y(-343.5, 49.1),
  new_x_y(-343.4, 51.2),
  new_x_y(-343.35, 53.3),
  new_x_y(-343.28, 55.5),
  new_x_y(-343.2425231933594, 57.59950256347656),
  new_x_y(-343.2458117675781, 59.59837341308594),
  new_x_y(-343.24910034179686, 61.59727478027344),
  new_x_y(-343.2523889160156, 63.59614562988281),
  new_x_y(-343.2556469726562, 65.59504699707031),
  new_x_y(-343.258935546875, 67.59391784667969),
  new_x_y(-343.2622241210937, 69.59281921386719),
  new_x_y(-343.2655126953125, 71.59169006347656),
  new_x_y(-343.26880126953125, 73.59059143066406),
  new_x_y(-343.27208984375, 75.58946228027344),
  new_x_y(-343.27537841796874, 77.58836364746094),
  new_x_y(-343.2786669921875, 79.58723449707031),
  new_x_y(-343.2819555664062, 81.58613586425781),
  new_x_y(-343.2852136230469, 83.58500671386719),
  new_x_y(-343.28850219726564, 85.58390808105469),
  new_x_y(-343.2917907714844, 87.58277893066406),
  new_x_y(-343.29507934570313, 89.58168029785156),
  new_x_y(-343.2983679199219, 91.58058166503906),
  new_x_y(-343.3016564941406, 93.57945251464844),
  new_x_y(-343.30494506835936, 95.57835388183594),
  new_x_y(-343.3082336425781, 97.57722473144533),
  new_x_y(-343.3115222167969, 99.5761260986328),
  new_x_y(-343.3147802734375, 101.5749969482422),
  new_x_y(-343.31806884765626, 103.57389831542967),
  new_x_y(-343.321357421875, 105.57276916503906),
  new_x_y(-343.3246459960937, 107.57167053222656),
  new_x_y(-343.3279345703125, 109.57054138183594),
  new_x_y(-343.33122314453124, 111.56944274902344),
  new_x_y(-343.33451171875, 113.5683135986328),
  new_x_y(-343.3378002929687, 115.56721496582033),
  new_x_y(-343.3410888671875, 117.56608581542967),
  new_x_y(-343.34434692382814, 119.5649871826172),
  new_x_y(-343.3476354980469, 121.56385803222656),
  new_x_y(-343.3509240722656, 123.56275939941406),
  new_x_y(-343.35421264648437, 125.56166076660156),
  new_x_y(-343.3575012207031, 127.56053161621094),
  new_x_y(-343.36078979492186, 129.55943298339844),
  new_x_y(-343.3640783691406, 131.5583038330078),
  new_x_y(-343.3673669433594, 133.5572052001953),
  new_x_y(-343.370625, 135.5560760498047),
  new_x_y(-343.35, 137.5549774169922),
  new_x_y(-343.3072021484375, 139.55384826660156),
  new_x_y(-343.24049072265626, 141.55274963378906),
  new_x_y(-343.173779296875, 143.55162048339844),
  new_x_y(-343.1070678710937, 145.55052185058594),
  new_x_y(-343.0403564453125, 147.5493927001953),
  new_x_y(-342.97364501953126, 149.5482940673828),
  new_x_y(-342.90693359375, 151.5471649169922),
  new_x_y(-342.84019165039064, 153.5460662841797),
  new_x_y(-342.7734802246094, 155.54493713378906),
  new_x_y(-342.70676879882814, 157.54383850097656),
  new_x_y(-342.6400573730469, 159.54270935058594),
  new_x_y(-342.57334594726564, 161.54161071777344),
  new_x_y(-342.5066345214844, 163.54051208496094),
  new_x_y(-342.43992309570314, 165.5393829345703),
  new_x_y(-342.3732116699219, 167.5382843017578),
  new_x_y(-342.30650024414064, 169.5371551513672),
  new_x_y(-342.23975830078126, 171.5360565185547),
  new_x_y(-342.173046875, 173.53492736816406),
  new_x_y(-342.10633544921876, 175.53382873535156),
  new_x_y(-342.0396240234375, 177.53269958496094),
  new_x_y(-341.97291259765626, 179.53160095214844),
  new_x_y(-341.906201171875, 181.5304718017578),
  new_x_y(-341.8394897460937, 183.5293731689453),
  new_x_y(-341.7727783203125, 185.5282440185547),
  new_x_y(-341.70606689453126, 187.5271453857422),
  new_x_y(-341.6393249511719, 189.5260162353516),
  new_x_y(-341.57261352539064, 191.52491760253903),
  new_x_y(-341.5059020996094, 193.52378845214844),
  new_x_y(-341.43919067382814, 195.52268981933597),
  new_x_y(-341.3724792480469, 197.52159118652344),
  new_x_y(-341.30576782226564, 199.5204620361328),
  new_x_y(-341.2390563964844, 201.5193634033203),
  new_x_y(-341.17234497070314, 203.5182342529297),
  new_x_y(-341.1056335449219, 205.5171356201172),
  new_x_y(-341.0388916015625, 207.51600646972656),
  new_x_y(-340.97218017578126, 209.5149078369141),
  new_x_y(-340.90546875, 211.51377868652344),
  new_x_y(-340.83875732421876, 213.5126800537109),
  new_x_y(-340.7720458984375, 215.5115509033203),
  new_x_y(-340.70533447265626, 217.5104522705078),
  new_x_y(-340.638623046875, 219.5093231201172),
  new_x_y(-340.5719116210937, 221.5082244873047),
  new_x_y(-340.5052001953125, 223.5070953369141),
  new_x_y(-340.43845825195314, 225.5059967041016),
  new_x_y(-340.3717468261719, 227.5048675537109),
  new_x_y(-340.30503540039064, 229.50376892089844),
  new_x_y(-340.2383239746094, 231.50267028808597),
  new_x_y(-340.17161254882814, 233.5015411376953),
  new_x_y(-340.1049011230469, 235.5004425048828),
  new_x_y(-340.03818969726564, 237.4993133544922),
  new_x_y(-339.9714782714844, 239.4982147216797),
  new_x_y(-339.90476684570314, 241.49708557128903),
  new_x_y(-339.8380249023437, 243.49598693847656),
  new_x_y(-339.7713134765625, 245.49485778808597),
  new_x_y(-339.70460205078126, 247.49375915527344),
  new_x_y(-339.637890625, 249.4926300048828),
  new_x_y(-339.57117919921876, 251.4915313720703),
  new_x_y(-339.5044677734375, 253.4904022216797),
  new_x_y(-339.43775634765626, 255.4893035888672),
  new_x_y(-339.371044921875, 257.4881591796875),
  new_x_y(-339.3043334960937, 259.487060546875),
  new_x_y(-339.2375915527344, 261.4859619140625),
  new_x_y(-339.17088012695314, 263.48486328125),
  new_x_y(-339.1041687011719, 265.48370361328125),
  new_x_y(-339.03745727539064, 267.48260498046875),
  new_x_y(-338.9707458496094, 269.48150634765625),
  new_x_y(-338.90403442382814, 271.4804077148437),
  new_x_y(-338.8373229980469, 273.479248046875),
  new_x_y(-338.77061157226564, 275.4781494140625),
  new_x_y(-338.70386962890626, 277.47705078125),
  new_x_y(-338.637158203125, 279.4759521484375),
  new_x_y(-338.5704467773437, 281.47479248046875),
  new_x_y(-338.5037353515625, 283.47369384765625),
  new_x_y(-338.43702392578126, 285.4725952148437),
  new_x_y(-338.3, 287.4714660644531),
  new_x_y(-338.15, 289.4696960449219),
  new_x_y(-338, 291.4667358398437),
  new_x_y(-337.87, 293.4622802734375),
  new_x_y(-337.63, 295.57938104829776),
  new_x_y(-337.4, 297.6956472447914),
  new_x_y(-337.15758115312997, 299.81011987990416),
  new_x_y(-336.91836908806914, 301.9215914330887),
  new_x_y(-336.6418076495959, 304.0284823421357),
  new_x_y(-336.318683504231, 306.12871865486255),
  new_x_y(-335.9398960929732, 308.21961161765273),
  new_x_y(-335.4965100939307, 310.29774031792573),
  new_x_y(-334.9798238937089, 312.3588389125448),
  new_x_y(-334.38145639508144, 314.39769046277337),
  new_x_y(-333.69345423906987, 316.40802995065553),
  new_x_y(-332.90842117070656, 318.38245965990507),
  new_x_y(-332.01967080638593, 320.3123807501063),
  new_x_y(-331.02140344302677, 322.18794551404585),
  new_x_y(-329.9089067619942, 323.99803545528476),
  new_x_y(-328.67877930271305, 325.7302709198313),
  new_x_y(-327.3291743951622, 327.37105851663097),
  new_x_y(-325.8600608366352, 328.90568291218955),
  new_x_y(-324.27349497551563, 330.3184497216768),
  new_x_y(-322.57389703549154, 331.5928860707134),
  new_x_y(-320.7683225063256, 332.7120048904),
  new_x_y(-318.86671729112027, 333.6586380505436),
  new_x_y(-320.55279541015625, 332.7275085449219),
  new_x_y(-318.68414306640625, 333.4375305175781),
  new_x_y(-316.74951171875, 333.9408569335937),
  new_x_y(-314.7717590332031, 334.2315979003906),
  new_x_y(-312.7741394042969, 334.30633544921875),
  new_x_y(-310.7801818847656, 334.16412353515625),
  new_x_y(-308.80279541015625, 333.8643798828125),
  new_x_y(-307.814697265625, 333.7107238769531),
  new_x_y(-306.8265686035156, 333.5570678710937),
  new_x_y(-305.83843994140625, 333.4034423828125),
  new_x_y(-304.8503112792969, 333.2497863769531),
  new_x_y(-303.8621826171875, 333.0961303710937),
  new_x_y(-301.877197265625, 332.8551025390625),
  new_x_y(-299.88006591796875, 332.75640869140625),
  new_x_y(-297.8809814453125, 332.8007202148437),
  new_x_y(-295.8901672363281, 332.9877319335937),
  new_x_y(-293.9178161621094, 333.3164978027344),
  new_x_y(-291.9739990234375, 333.7853698730469),
  new_x_y(-290.0686340332031, 334.3919372558594),
  new_x_y(-290.0686340332031, 334.15),
  new_x_y(-288.6, 334.8),
  new_x_y(-287.2, 335.6),
  new_x_y(-285.53462028523313, 337),
  new_x_y(-283.8206015721414, 338.6180705351394),
  new_x_y(-282.2413695974792, 339.97542718319943),
  new_x_y(-281.8073997467029, 341.48555109159435),
  new_x_y(-280.52547159263526, 343.12681286859697),
  new_x_y(-279.3990548588583, 344.87855052651463),
  new_x_y(-277.4287151511894, 346.7214132459724),
  new_x_y(-277.0583801269531, 345.9961853027344),
  new_x_y(-276.4298400878906, 347.8937683105469),
  new_x_y(-276.01287841796875, 349.84881591796875),
  new_x_y(-275.8125305175781, 351.8377380371094),
  new_x_y(-275.83123779296875, 353.8366394042969),
  new_x_y(-276.0382080078125, 355.8256530761719),
  new_x_y(-276.2694091796875, 357.812255859375),
  new_x_y(-276.5009765625, 359.7987976074219),
  new_x_y(-276.7503662109375, 361.7831726074219),
  new_x_y(-277.02667236328125, 363.76397705078125),
  new_x_y(-277.329833984375, 365.7408447265625),
  new_x_y(-277.65985107421875, 367.7134094238281),
  new_x_y(-278.0165710449219, 369.68133544921875),
  new_x_y(-278.39996337890625, 371.64422607421875),
  new_x_y(-278.80999755859375, 373.6017150878906),
  new_x_y(-279.24658203125, 375.553466796875),
  new_x_y(-279.7095947265625, 377.4991455078125),
  new_x_y(-280.198974609375, 379.4383239746094),
  new_x_y(-283.324462890625, 385.2135009765625),
  new_x_y(-283.9183959960937, 387.1232604980469),
  new_x_y(-284.2, 388.8),
  new_x_y(-284.6, 390.5),
  new_x_y(-284.6, 392.0),
  new_x_y(-285.2, 393.5)
]

SEC_12_WAYPOINTS = [
  new_x_y(-343.2425231933594, 57.59950256347656),
  new_x_y(-343.2458117675781, 59.59837341308594),
  new_x_y(-343.24910034179686, 61.59727478027344),
  new_x_y(-343.2523889160156, 63.59614562988281),
  new_x_y(-343.2556469726562, 65.59504699707031),
  new_x_y(-343.258935546875, 67.59391784667969),
  new_x_y(-343.2622241210937, 69.59281921386719),
  new_x_y(-343.2655126953125, 71.59169006347656),
  new_x_y(-343.26880126953125, 73.59059143066406),
  new_x_y(-343.27208984375, 75.58946228027344),
  new_x_y(-343.27537841796874, 77.58836364746094),
  new_x_y(-343.2786669921875, 79.58723449707031),
  new_x_y(-343.2819555664062, 81.58613586425781),
  new_x_y(-343.2852136230469, 83.58500671386719),
  new_x_y(-343.28850219726564, 85.58390808105469),
  new_x_y(-343.2917907714844, 87.58277893066406),
  new_x_y(-343.29507934570313, 89.58168029785156),
  new_x_y(-343.2983679199219, 91.58058166503906),
  new_x_y(-343.3016564941406, 93.57945251464844),
  new_x_y(-343.30494506835936, 95.57835388183594),
  new_x_y(-343.3082336425781, 97.57722473144533),
  new_x_y(-343.3115222167969, 99.5761260986328),
  new_x_y(-343.3147802734375, 101.5749969482422),
  new_x_y(-343.31806884765626, 103.57389831542967),
  new_x_y(-343.321357421875, 105.57276916503906),
  new_x_y(-343.3246459960937, 107.57167053222656),
  new_x_y(-343.3279345703125, 109.57054138183594),
  new_x_y(-343.33122314453124, 111.56944274902344),
  new_x_y(-343.33451171875, 113.5683135986328),
  new_x_y(-343.3378002929687, 115.56721496582033),
  new_x_y(-343.3410888671875, 117.56608581542967),
  new_x_y(-343.34434692382814, 119.5649871826172),
  new_x_y(-343.3476354980469, 121.56385803222656),
  new_x_y(-343.3509240722656, 123.56275939941406),
  new_x_y(-343.35421264648437, 125.56166076660156),
  new_x_y(-343.3575012207031, 127.56053161621094),
  new_x_y(-343.36078979492186, 129.55943298339844),
  new_x_y(-343.3640783691406, 131.5583038330078),
  new_x_y(-343.3673669433594, 133.5572052001953),
  new_x_y(-343.370625, 135.5560760498047),
  new_x_y(-343.37391357421876, 137.5549774169922),
  new_x_y(-343.3072021484375, 139.55384826660156),
  new_x_y(-343.24049072265626, 141.55274963378906),
  new_x_y(-343.173779296875, 143.55162048339844),
  new_x_y(-343.1070678710937, 145.55052185058594),
  new_x_y(-343.0403564453125, 147.5493927001953),
  new_x_y(-342.97364501953126, 149.5482940673828),
  new_x_y(-342.90693359375, 151.5471649169922),
  new_x_y(-342.84019165039064, 153.5460662841797),
  new_x_y(-342.7734802246094, 155.54493713378906),
  new_x_y(-342.70676879882814, 157.54383850097656),
  new_x_y(-342.6400573730469, 159.54270935058594),
  new_x_y(-342.57334594726564, 161.54161071777344),
  new_x_y(-342.5066345214844, 163.54051208496094),
  new_x_y(-342.43992309570314, 165.5393829345703),
  new_x_y(-342.3732116699219, 167.5382843017578),
  new_x_y(-342.30650024414064, 169.5371551513672),
  new_x_y(-342.23975830078126, 171.5360565185547),
  new_x_y(-342.173046875, 173.53492736816406),
  new_x_y(-342.10633544921876, 175.53382873535156),
  new_x_y(-342.0396240234375, 177.53269958496094),
  new_x_y(-341.97291259765626, 179.53160095214844),
  new_x_y(-341.906201171875, 181.5304718017578),
  new_x_y(-341.8394897460937, 183.5293731689453),
  new_x_y(-341.7727783203125, 185.5282440185547),
  new_x_y(-341.70606689453126, 187.5271453857422),
  new_x_y(-341.6393249511719, 189.5260162353516),
  new_x_y(-341.57261352539064, 191.52491760253903),
  new_x_y(-341.5059020996094, 193.52378845214844),
  new_x_y(-341.43919067382814, 195.52268981933597),
  new_x_y(-341.3724792480469, 197.52159118652344),
  new_x_y(-341.30576782226564, 199.5204620361328),
  new_x_y(-341.2390563964844, 201.5193634033203),
  new_x_y(-341.17234497070314, 203.5182342529297),
  new_x_y(-341.1056335449219, 205.5171356201172),
  new_x_y(-341.0388916015625, 207.51600646972656),
  new_x_y(-340.97218017578126, 209.5149078369141),
  new_x_y(-340.90546875, 211.51377868652344),
  new_x_y(-340.83875732421876, 213.5126800537109),
  new_x_y(-340.7720458984375, 215.5115509033203),
  new_x_y(-340.70533447265626, 217.5104522705078),
  new_x_y(-340.638623046875, 219.5093231201172),
  new_x_y(-340.5719116210937, 221.5082244873047),
  new_x_y(-340.5052001953125, 223.5070953369141),
  new_x_y(-340.43845825195314, 225.5059967041016),
  new_x_y(-340.3717468261719, 227.5048675537109),
  new_x_y(-340.30503540039064, 229.50376892089844),
  new_x_y(-340.2383239746094, 231.50267028808597),
  new_x_y(-340.17161254882814, 233.5015411376953),
  new_x_y(-340.1049011230469, 235.5004425048828),
  new_x_y(-340.03818969726564, 237.4993133544922),
  new_x_y(-339.9714782714844, 239.4982147216797),
  new_x_y(-339.90476684570314, 241.49708557128903),
  new_x_y(-339.8380249023437, 243.49598693847656),
  new_x_y(-339.7713134765625, 245.49485778808597),
  new_x_y(-339.70460205078126, 247.49375915527344),
  new_x_y(-339.637890625, 249.4926300048828),
  new_x_y(-339.57117919921876, 251.4915313720703),
  new_x_y(-339.5044677734375, 253.4904022216797),
  new_x_y(-339.43775634765626, 255.4893035888672),
  new_x_y(-339.371044921875, 257.4881591796875),
  new_x_y(-339.3043334960937, 259.487060546875),
  new_x_y(-339.2375915527344, 261.4859619140625),
  new_x_y(-339.17088012695314, 263.48486328125),
  new_x_y(-339.1041687011719, 265.48370361328125),
  new_x_y(-339.03745727539064, 267.48260498046875),
  new_x_y(-338.9707458496094, 269.48150634765625),
  new_x_y(-338.90403442382814, 271.4804077148437),
  new_x_y(-338.8373229980469, 273.479248046875),
  new_x_y(-338.77061157226564, 275.4781494140625),
  new_x_y(-338.70386962890626, 277.47705078125),
  new_x_y(-338.637158203125, 279.4759521484375),
  new_x_y(-338.5704467773437, 281.47479248046875),
  new_x_y(-338.5037353515625, 283.47369384765625),
  new_x_y(-338.43702392578126, 285.4725952148437),
  new_x_y(-338.3699462890625, 287.4714660644531),
  new_x_y(-338.2862670898437, 289.4696960449219),
  new_x_y(-338.177685546875, 291.4667358398437),
  new_x_y(-337.74420166015625, 293.4622802734375),
  new_x_y(-337.561151551239, 295.57938104829776),
  new_x_y(-337.3687309999671, 297.6956472447914),
  new_x_y(-337.15758115312997, 299.81011987990416),
  new_x_y(-336.91836908806914, 301.9215914330887),
  new_x_y(-336.6418076495959, 304.0284823421357),
  new_x_y(-336.318683504231, 306.12871865486255),
  new_x_y(-335.9398960929732, 308.21961161765273),
  new_x_y(-335.4965100939307, 310.29774031792573),
  new_x_y(-334.9798238937089, 312.3588389125448),
  new_x_y(-334.38145639508144, 314.39769046277337),
  new_x_y(-333.69345423906987, 316.40802995065553),
  new_x_y(-332.90842117070656, 318.38245965990507),
  new_x_y(-332.01967080638593, 320.3123807501063),
  new_x_y(-331.02140344302677, 322.18794551404585),
  new_x_y(-329.9089067619942, 323.99803545528476),
  new_x_y(-328.67877930271305, 325.7302709198313),
  new_x_y(-327.3291743951622, 327.37105851663097),
  new_x_y(-325.8600608366352, 328.90568291218955),
  new_x_y(-324.27349497551563, 330.3184497216768),
  new_x_y(-322.57389703549154, 331.5928860707134),
  new_x_y(-320.7683225063256, 332.7120048904),
  new_x_y(-318.86671729112027, 333.6586380505436),
  new_x_y(-320.55279541015625, 332.7275085449219),
  new_x_y(-318.68414306640625, 333.4375305175781),
  new_x_y(-316.74951171875, 333.9408569335937),
  new_x_y(-314.7717590332031, 334.2315979003906),
  new_x_y(-312.7741394042969, 334.30633544921875),
  new_x_y(-310.7801818847656, 334.16412353515625),
  new_x_y(-308.80279541015625, 333.8643798828125),
  new_x_y(-307.814697265625, 333.7107238769531),
  new_x_y(-306.8265686035156, 333.5570678710937),
  new_x_y(-305.83843994140625, 333.4034423828125),
  new_x_y(-304.8503112792969, 333.2497863769531),
  new_x_y(-303.8621826171875, 333.0961303710937),
  new_x_y(-301.877197265625, 332.8551025390625),
  new_x_y(-299.88006591796875, 332.75640869140625),
  new_x_y(-297.8809814453125, 332.8007202148437),
  new_x_y(-295.8901672363281, 332.9877319335937),
  new_x_y(-293.9178161621094, 333.3164978027344),
  new_x_y(-291.9739990234375, 333.7853698730469),
  new_x_y(-290.0686340332031, 334.3919372558594),
  new_x_y(-287.36890955136124, 336.4502300627805),
  new_x_y(-285.53462028523313, 337.43563207506764),
  new_x_y(-283.8206015721414, 338.6180705351394),
  new_x_y(-282.2413695974792, 339.97542718319943),
  new_x_y(-280.8073997467029, 341.48555109159435),
  new_x_y(-279.52547159263526, 343.12681286859697),
  new_x_y(-278.3990548588583, 344.87855052651463),
  new_x_y(-277.4287151511894, 346.7214132459724),
  new_x_y(-276.6125219176662, 348.63761172938075),
  new_x_y(-275.9464446647921, 350.61108536348434),
  new_x_y(-275.424726785363, 352.62759715614163),
  new_x_y(-275.04022934994344, 354.6747675289015),
  new_x_y(-274.78473982892007, 356.7420576792383),
  new_x_y(-274.6492429260599, 358.8207125056033),
  new_x_y(-274.62415252333415, 360.9036721291275),
  new_x_y(-274.6995051839878, 362.98545994418),
  new_x_y(-274.86511677200605, 365.06205396436957),
  new_x_y(-275.11070456392184, 367.1307470623927),
  new_x_y(-275.42597779922124, 369.1900005776115),
  new_x_y(-275.8006999845239, 371.23929471755116),
  new_x_y(-276.22472647836435, 373.2789782309583),
  new_x_y(-276.68802097838517, 375.31011899439363),
  new_x_y(-277.18065454720767, 377.334356438785),
  new_x_y(-277.6927907782895, 379.3537561495886),
  new_x_y(-278.21466064453125, 381.3706665039063),
  new_x_y(-278.75653076171875, 383.2958679199219),
  new_x_y(-279.324462890625, 385.2135009765625),
  new_x_y(-279.9183959960937, 387.1232604980469),
  new_x_y(-280.5381774902344, 389.0247802734375),
  new_x_y(-281.29998779296875, 391.6999816894531),
  new_x_y(-282.1494140625, 393.758056640625)
<<<<<<< Updated upstream
]


# Section 0: 319
# Section 1: 175
# Section 2: 114
# Section 3: 146
# Section 4: 124
# Section 5: 77
# Section 6: 313
# Section 7: 211
# Section 8: 254
# Section 9: 75
# Section 10: 238
# Section 11: 189
# Section 12: 161
# Section 0: 207
# Section 1: 162
# Section 2: 112
# Section 3: 146
# Section 4: 124
# Section 5: 75
# Section 6: 315
# Section 7: 213
# Section 8: 252
# Section 9: 75
# Section 10: 241
# Section 11: 188
# Section 12: 163
# Section 0: 207
# Section 1: 162
# Section 2: 112
# Section 3: 146
# Section 4: 124
# Section 5: 77
# Section 6: 314
# Section 7: 212
# Section 8: 252
# Section 9: 75
# Section 10: 239
# Section 11: 188
# Section 12: 164
# end of the loop
# done
# Solution finished in 347.2500000000506 seconds
=======
]
>>>>>>> Stashed changes
