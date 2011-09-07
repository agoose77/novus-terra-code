
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

		self.world_time = 0.0
		self.world_time_scale = 0.30

		### Light
		self.light_sources = None
		self.outside_lighting_ctrl = 'outdoor_sun_shadow'
		self.sky_dome = 'sky_dome'
		self.atmosphere_ctrl = 'atmosphere_time'

		###
		self.gravity = Vector([0,0, -9.8])
		self.world_effects = {'mist color':[0.0,0.0,0.0], 'tint':[0.0,0.0,0.0]}
		self.current_weather = None
		self.last_weather_change = 1.0


	def handle_time(self):

		# Add timescale to current time
		if self.world_time < 240:
			self.world_time += self.world_time_scale
		else:
			self.world_time = 1.0

        ### HACK - set the Time prop for all the lighting effects
		atmos = bge.logic.getSceneList()[0].objects[self.atmosphere_ctrl]
		lighting = bge.logic.getCurrentScene().objects[self.outside_lighting_ctrl]
		sun = bge.logic.getCurrentScene().objects['Sun_Main']
		lighting['Time'] = self.world_time
		atmos['Time'] = self.world_time
		sun['Time'] = self.world_time


	def main(self):

		#JPLUR ENTITY HACKS
		if game.init_game == 1:
			self.player.main()

		self.handle_time()

