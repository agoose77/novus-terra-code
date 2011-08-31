import pickle

import bge
import random
from mathutils import Vector

from dialogue_system import DialogueSystem
from player import Player
import game

class World:

	INTERIOR_WORLD = 0
	EXTERIOR_WORLD = 1

	def __init__(self):
		print("world.__init__()")
		self.current_world_file = None
		self.current_cell = None
		self.loaded_libs = None
		self.loaded_kdtrees = None
		self.loaded_entities = None
		self.entity_loading_queue = None

		self.player = Player()
		self.player.worldPosition = [15,15,5]

		self.world_time = 0.0
		self.world_time_rate = 1.0

		### Light
		self.light_sources = None
		self.outside_lighting_ctrl = 'outdoor_sun_shadow'

		###
		self.gravity = Vector([0,0, -9.8])
		self.current_weather = None
		self.last_weather_change = 0.0

	def handle_weather(self):
		'''
		0 = Clear
		1 = Dust storm
		2 = Heat storm
		3 = Cloudy
		4 = ???
		'''

		# if that weather has been there for awhile
		if (self.last_weather_change-self.world_time) > 20.0:
			random_num = random.range(0,5)
			self.current_weather = random_num
			self.last_weather_change = self.world_time


	def handle_time(self):
		self.world_time += self.world_time_rate



	def main(self):

		#JPLUR ENTITY HACKS
		if game.init_game == 1:
			self.player.main()

		self.handle_time()
		self.handle_weather()

