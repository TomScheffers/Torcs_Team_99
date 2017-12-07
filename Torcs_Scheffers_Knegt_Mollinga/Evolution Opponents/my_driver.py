from pytocl.driver import Driver
import time
from pytocl.car import State, Command
import numpy as np
from nn_all import predict_output, load_keras_model
from nn_opponent import predict_opponent_output, load_keras_opponent_model

class MyDriver(Driver):
	def __init__(self):
		self.model = load_keras_model('EVO_Best_1.h5')
		self.opponent_model = load_keras_model('opponent_model_generation_13.h5')
		self.time_offset = 0
		self.time = 0
		self.been_outside_track = False
		self.time_outside_circuit = 0
		self.start_time = None
	def drive(self, carstate: State) -> Command:
		data = []
		command = Command()
		angle = carstate.angle
		speed_x = carstate.speed_x
		track_position = carstate.distance_from_center
		track_edges = carstate.distances_from_edge
		data.append(speed_x)
		data.append(track_position)
		data.append(angle)
		for i in track_edges:
			data.append(i)
		out1, str1 = predict_output(self.model, data,"MLP")

		opponent_data =[]
		ranking = carstate.race_position
		opponent_distance = carstate.opponents
		opponent_data.append(out1)
		opponent_data.append(str1)
		opponent_data.append(ranking)
		for k in opponent_distance:
			opponent_data.append(k)
		out2, str2 = predict_opponent_output(self.opponent_model, opponent_data)

		out = out1 + out2
		command.steering = str1 + str2
		if out > 0
			command.accelerator = out
			command.brake = 0
		elif out <= 0:
			command.accelerator = 0
			command.brake = -out
		if carstate.rpm > 5000:
			command.gear = carstate.gear + 1
		elif carstate.rpm < 2500 and carstate.gear > 1:
			command.gear = carstate.gear - 1
		if not command.gear:
			command.gear = carstate.gear or 1

		if sum (track_edges) < 0 and not self.been_outside_track:
			self.start_time = time.time()
			self.been_outside_track = True
			#print ('Ive been outside the track')

		if sum (track_edges) > 0 and self.been_outside_track:
			end_time = time.time()
			self.time_outside_circuit += end_time - self.start_time
			print ('Im in the track again, and was out for',end_time - self.start_time)
			print ('Total time out is',self.time_outside_circuit)
			self.been_outside_track = False

		if carstate.last_lap_time != self.time:
			self.time = carstate.last_lap_time
			fitness = carstate.last_lap_time
			fitnesses = open('laptimes.txt', 'a')
			fitnesses.write(str(fitness) + ' ' + str(self.time_outside_circuit) + ' ' +str(carstate.damage) + ' '+str(carstate.race_position)+'\n')

		return command
