from pytocl.driver import Driver
from pytocl.car import State, Command
import logging
import csv
import math
import time
import numpy as np
from pytocl.analysis import DataLogWriter
from pytocl.car import State, Command, MPS_PER_KMH
from pytocl.controller import CompositeController, ProportionalController, \
	IntegrationController, DerivativeController

_logger = logging.getLogger(__name__)

class MySecondDriver(Driver):
		"""
        Driving logic.

        Implement the driving intelligence in this class by processing the current
        car state as inputs creating car control commands as a response. The
        ``drive`` function is called periodically every 20ms and must return a
        command within 10ms wall time.
        """

		def __init__(self, logdata=False):
			self.steering_ctrl = CompositeController(
				ProportionalController(0.4),
				IntegrationController(0.2, integral_limit=1.5),
				DerivativeController(2)
			)
			self.acceleration_ctrl = CompositeController(
				ProportionalController(3.7),
			)
			self.data_logger = DataLogWriter() if logdata else None

			self.train_data = []
			self.written = False

			self.been_outside_track = False
			self.time_outside_circuit = 0
			self.start_time = None
			self.time = 0

			with open('best_param_default.txt', 'r') as file:
				lines = file.readlines()
				self.brake_scaling = float(lines[0])
				self.brake_translation = float(lines[1])
				self.c = float(lines[2])
				self.D = float(lines[3])
				self.track_dev = float(lines[4])

				print('brake_scaling is', self.brake_scaling)
				print('brake_translation is', self.brake_translation)
				print('c is', self.c)
				print('D is', self.D)
				print('track_dev is', self.track_dev)

		@property
		def range_finder_angles(self):
			"""Iterable of 19 fixed range finder directions [deg].

            The values are used once at startup of the client to set the directions
            of range finders. During regular execution, a 19-valued vector of track
            distances in these directions is returned in ``state.State.tracks``.
            """
			return -90, -75, -60, -45, -30, -20, -15, -10, -5, 0, 5, 10, 15, 20, \
				   30, 45, 60, 75, 90

		def on_shutdown(self):
			"""
            Server requested driver shutdown.

            Optionally implement this event handler to clean up or write data
            before the application is stopped.
            """
			if self.data_logger:
				self.data_logger.close()
				self.data_logger = None

		def drive(self, carstate: State) -> Command:
			"""
            Produces driving command in response to newly received car state.

            This is a dummy driving routine, very dumb and not really considering a
            lot of inputs. But it will get the car (if not disturbed by other
            drivers) successfully driven along the race track.
            """
			avoidCollision = True
			otherPosition = 0
			with open('secondDriver.txt', 'w') as f:
				f.write('%d' % carstate.race_position)
			with open('fristDriver.txt') as f:
				for line in f:
					for s in line.split(' '):
						otherPosition = int(s)
			if (carstate.race_position < otherPosition):# and (carstate.race_position-otherPosition > 1)):
				#print("I am in front")
				avoidCollision = True
			else:
				#print("I am a loser")
				avoidCollision = False

			if ((carstate.race_position == 11 or carstate.race_position == 12) and (otherPosition == 11 or otherPosition == 12)):
				avoidCollision = True
			#print(otherPosition)
			#print(carstate.race_position)
			print("Driver 2 is: ",avoidCollision)
			command = Command()
			self.steer(carstate, 0.0, command,avoidCollision)

			# ACC_LATERAL_MAX = 6400 * 5
			# v_x = min(80, math.sqrt(ACC_LATERAL_MAX / abs(command.steering)))
			v_x = max(50, max(carstate.distances_from_edge))

			if v_x == 200.0:
				v_x = 500.0

			if (carstate.speed_x * 3.6 - v_x > 0):  # v_x is the maximum speed allowed at a certain point
				diff = carstate.speed_x * 3.6 - v_x  # Convert to km/h from m 12zs
				if avoidCollision == False and carstate.race_position < 12:
					command.brake = 1
				else:
					for i in range(0, 10):
						if carstate.opponents[i] < 10.0:
							if avoidCollision == False:
								print("brake extra!!1")
								command.brake = (self.brake_scaling / (
								1 + np.exp(-1 * (diff - self.brake_translation)))) * 1.2
					for i in range(27, len(carstate.opponents)):
						if carstate.opponents[i] < 10.0:
							if avoidCollision == False:
								print("brake extra!!1")
								command.brake = (self.brake_scaling / (
								1 + np.exp(-1 * (diff - self.brake_translation)))) * 1.2
					if avoidCollision == True:
						command.brake = self.brake_scaling / (1 + np.exp(-1 * (diff - self.brake_translation)))

			# print ('braking is',command.brake)

			self.accelerate(carstate, v_x, command,avoidCollision)
			# self.data_logger.log(carstate, command)
			data = []
			data.append(command.accelerator)
			data.append(command.brake)
			data.append(command.steering)
			data.append(carstate.speed_x)
			data.append(carstate.speed_y)  # NEW
			data.append(carstate.speed_z)  # NEW

			data.append(carstate.distance_from_center)
			data.append(carstate.angle)

			for i in carstate.wheel_velocities:
				data.append(i)

			for i in carstate.distances_from_edge:
				data.append(i)

			self.train_data.append(data)
			# a.writerow(data)
			'''
            if carstate.last_lap_time > 0.0 and not self.written:
                b = open('Joris-Data/Wheel2.csv', 'w')
                a = csv.writer(b)
                a.writerows(self.train_data)
                b.close()
                print ('Rondje gereden')
                self.written = True

            '''

			track_edges = carstate.distances_from_edge

			if sum(track_edges) < 0 and not self.been_outside_track:
				self.start_time = time.time()
				self.been_outside_track = True
			# print ('Ive been outside the track')

			if sum(track_edges) > 0 and self.been_outside_track:
				end_time = time.time()
				self.time_outside_circuit += end_time - self.start_time
				print('Im in the track again, and was out for', end_time - self.start_time)
				print('Total time out is', self.time_outside_circuit)
				self.been_outside_track = False

			if carstate.last_lap_time != self.time:
				self.time = carstate.last_lap_time
				lap_time = carstate.last_lap_time

				fitness = 10 * lap_time + 100 * self.time_outside_circuit + 2 * carstate.damage

				fitnesses = open('laptimes.txt', 'a')
				# fitnesses.write(str(lap_time) + ' ' + str(self.time_outside_circuit) + ' ' + str(carstate.damage) + '\n')
				fitnesses.write(str(fitness) + '\n')

			return command

		def accelerate(self, carstate, target_speed, command,avoid):
			# compensate engine deceleration, but invisible to controller to
			# prevent braking:
			speed_error = 1.0025 * target_speed * MPS_PER_KMH - carstate.speed_x
			acceleration = self.acceleration_ctrl.control(
				speed_error,
				carstate.current_lap_time
			)

			# stabilize use of gas and brake:
			acceleration = math.pow(acceleration, 3)

			if acceleration > 0:
				if abs(carstate.distance_from_center) >= 1:
					# off track, reduced grip:
					acceleration = min(0.4, acceleration)
				if avoid == False:
					command.accelerator = (min(acceleration, 1))
				else:
					command.accelerator = (min(acceleration, 1))*1.25

				if carstate.rpm > 8000:
					command.gear = carstate.gear + 1

			# else:
			#     command.brake = min(-acceleration, 1)

			if carstate.rpm < 3500:
				command.gear = carstate.gear - 1

			if not command.gear:
				command.gear = carstate.gear or 1

		def steer(self, carstate, target_track_pos, command,avoid):
			steering_error = target_track_pos - carstate.distance_from_center + self.track_dev
			# print ('steering error is',steering_error)
			for i in range(0, len(carstate.opponents)):
				if carstate.opponents[i] < 10.0:
					if i == 1 or i == 2 or i == 3 or i == 4 or i == 5 or i == 6 or i == 7 or i == 8 or i == 9:
						if avoid == True:
							steering_error += 0
						else:
							steering_error += 1
						# print ('Steering to the right')
					if i == 27 or i == 28 or i == 29 or i == 30 or i == 31 or i == 32 or i == 33 or i == 34 or i == 35:
						# print ('Steering to the left')
						if avoid == True:
							steering_error += 0
						else:
							steering_error += -1

			factor = 1. - (1. / (1. + np.exp(-self.c * (carstate.speed_x - self.D))))

			command.steering = factor * self.steering_ctrl.control(
				steering_error,
				carstate.current_lap_time)

