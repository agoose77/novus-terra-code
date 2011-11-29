import pickle
import random

import aud
import bge
from mathutils import Vector

import cell
import game
import entities
from ai_manager import AI_Manager
from dialogue_system import DialogueSystem
from paths import PATH_SOUNDS, PATH_MUSIC
import session

class World:

	INTERIOR_WORLD = 0
	EXTERIOR_WORLD = 1

	singleton = None

	def __init__(self):
		print("world.__init__()")

		World.singleton = self

		self.entity_list = []

		self.player = entities.Player()
		self.ai_manager = AI_Manager()
		self.cell_manager = cell.CellManager()
		#self.entity_list.append(self.player)

		self.world_time = 0.0
		self.world_time_scale = 0.01

		### Light
		self.light_sources = None
		self.outside_lighting_ctrl = 'outdoor_sun_shadow'
		self.sky_dome = 'sky_dome'
		self.atmosphere_ctrl = 'atmosphere_time'
		self.fx_object = 'FX'
		self.fx_motion_blur = 'FX BLUR'

		###
		self.gravity = Vector([0,0, -9.8])
		self.world_effects = {'mist color':[0.0,0.0,0.0], 'tint':[0.0,0.0,0.0]}

		self.fx = {
			#'prop_fade':True,
			#'terrain_lod_distance':5.0,
			'HDR':True,
			'Bloom':True,
			'DOF':False,
			'SSAO':False,
			'SSAA':False,
			'Color':True,
			'Motion Blur':True,
			#'Color settings':[1.0, 1.0, 1.0]
		}


	# Hackity hack :P
	def filters(self):
		### Set FX to cell settings
		#self.fx = cell.singleton.fx - DISABLED for now

		fx_obj = bge.logic.getCurrentScene().objects[self.fx_object]
		blur_obj = bge.logic.getCurrentScene().objects[self.fx_motion_blur]

		for fx in session.game.graphics_options:
			fx_obj[fx] = session.game.graphics_options[fx]


		"""for fx in self.fx:
			if session.game.graphics_options[fx] == True:
				if fx != 'Motion Blur':
					if fx != "Fade in props" or fx != "terrain_lod_distance":
						fx_obj[fx] = session.game.grapics_options[fx]
				else:
					blur_obj[fx] = self.fx[fx]
					"""


	def handle_time(self):
        #print("Updating Time:", self.world_time)

		# Add timescale to current time
		if self.world_time < 240:
			self.world_time += self.world_time_scale
		else:
			self.world_time = 1.0

		### HACK - set the Time prop for all the lighting effects
		if cell.CellManager.singleton.terrain != False:
			lighting = bge.logic.getCurrentScene().objects[self.outside_lighting_ctrl]
			sun = bge.logic.getCurrentScene().objects['Sun_Main']

			lighting['Time'] = self.world_time
			sun['Time'] = self.world_time

			#atmos = bge.logic.getSceneList()[0].objects[self.atmosphere_ctrl]
			#atmos['Time'] = self.world_time


	def main(self):
		session.profiler.start_timer('world.main')
		self.handle_time()
		self.filters()

		if 'player' in bge.logic.getCurrentScene().objects:
			if self.player._data == bge.logic.getCurrentScene().objects['player']:
				self.player.main()
			else:
				self.player._wrap(bge.logic.getCurrentScene().objects['player'])
		else:
			self.player._unwrap()
		self.cell_manager.update()
		if len(self.entity_list) != 0:
			self.ai_manager.main()
		session.profiler.stop_timer('world.main')
