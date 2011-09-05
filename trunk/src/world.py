import pickle

import bge
import random
from mathutils import Vector

from dialogue_system import DialogueSystem
from player import Player
import game
import cell

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
		#self.player.worldPosition = [15,15,5] - WHY?

		self.world_time = 0.0
		self.world_time_scale = 1.0

		### Light
		self.light_sources = None
		self.outside_lighting_ctrl = 'outdoor_sun_shadow'
		self.sky_dome = 'sky_dome'

		###
		self.gravity = Vector([0,0, -9.8])
		self.world_effects = {'mist color':[0.0,0.0,0.0], 'tint':[0.0,0.0,0.0]}
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
		self.world_time += self.world_time_scale

		### Exterior Cells only
		print (cell.singleton.terrain)

		if cell.singleton.terrain == True:
			bge.logic.getCurrentScene().objects[self.outside_lighting_ctrl]['time'] = self.world_time

			if self.world_time > 120:
				sky = bge.logic.getCurrentScene().objects[self.sky_dome]

				mesh = sky.meshes[0]
				amount = mesh.getVertexArrayLength(0)
				for a in range(0, amount):
					v = mesh.getVertex(0,a)
					v.setRGBA([0,1,0,1])


	def main(self):

		#JPLUR ENTITY HACKS
		if game.init_game == 1:
			self.player.main()

		self.handle_time()
		self.handle_weather()
		#print (cell.singleton.terrain)
		#print (self.sky_dome)

