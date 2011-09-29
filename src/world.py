
import pickle
from paths import PATH_SOUNDS, PATH_MUSIC
import bge
import aud
import random
from mathutils import Vector
from ai_manager import AI_Manager
from dialogue_system import DialogueSystem
from player import Player
import game
import cell

class World:

	INTERIOR_WORLD = 0
	EXTERIOR_WORLD = 1

	def __init__(self):
		print("world.__init__()")

		# Needed?
		self.current_world_file = None
		self.current_cell = None
		self.loaded_libs = None
		self.loaded_kdtrees = None
		self.loaded_entities = None
		self.entity_loading_queue = None
		self.entity_list = []

		self.player = Player()
		self.ai_manager = AI_Manager()

		self.world_time = 0.0
		self.world_time_scale = 0.05

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
			'HDR':True,
            'Bloom':True,
            'DOF':False,
            'SSAO':False,
            'SSAA':False,
            'Color':True,
            'Motion Blur':True,
			'Color settings':[1.0, 1.0, 1.0],
		}


	# Hackity hack :P
	def filters(self):
		### Set FX to cell settings
		#self.fx = cell.singleton.fx - DISABLED for now

		fx_obj = bge.logic.getCurrentScene().objects[self.fx_object]
		blur_obj = bge.logic.getCurrentScene().objects[self.fx_motion_blur]

		for fx in self.fx:
			if Game.graphics_options[fx] == True:
				if fx != 'Motion Blur':
					fx_obj[fx] = self.fx[fx]
				else:
					blur_obj[fx] = self.fx[fx]


	def handle_time(self):

		# Add timescale to current time
		if self.world_time < 240:
			self.world_time += self.world_time_scale
		else:
			self.world_time = 1.0

        ### HACK - set the Time prop for all the lighting effects
		if cell.singleton.terrain != False:
			try:
				atmos = bge.logic.getSceneList()[0].objects[self.atmosphere_ctrl]
				lighting = bge.logic.getCurrentScene().objects[self.outside_lighting_ctrl]
				sun = bge.logic.getCurrentScene().objects['Sun_Main']
				lighting['Time'] = self.world_time
				atmos['Time'] = self.world_time
				sun['Time'] = self.world_time

			except:
				pass


	def main(self):

		#JPLUR ENTITY HACKS
		if game.init_game == 1:
			self.player.main()
			#self.ai_manager.main()
        #	self.filters()

			# MUSIC
			#sound = aud.Factory(PATH_SOUNDS+'music_1.ogg')
			#handle = aud.device().play(sound)

		self.handle_time()

