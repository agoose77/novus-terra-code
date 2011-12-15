import pickle
import random
import mathutils

import aud
import bge
from mathutils import Vector

import cell
import game
import entities
from ai_manager import AI_Manager
from dialogue_system import DialogueSystem
from paths import PATH_SOUNDS, PATH_MUSIC

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

		self.world_time = 80.0
		self.world_time_scale = 0.01

		### Light
		self.light_sources = None
		self.outside_lighting_ctrl = 'outdoor_sun_shadow'
		self.sky_dome = 'sky_dome'
		self.atmosphere_ctrl = 'atmosphere_time'

		###
		self.gravity = Vector([0,0, -9.8])
		self.world_effects = {'mist color':[0.0,0.0,0.0], 'tint':[0.0,0.0,0.0]}
		
		self.gamestate = 'loading'
		self.KX_player = False

	def cell_loaded(self):
		self.gamestate = 'loaded'
		self.spawn_player()
		
	def cell_loading(self):
		self.gamestate = 'loading'
		self.KX_player = False
		
	def spawn_player(self):
		""" 
		Spawns the player
		"""
		scene = bge.logic.getCurrentScene()
		player = scene.addObject('player', "CELL_MANAGER_HOOK")
		if self.cell_manager.next_destination:
			destination = self.cell_manager.next_destination
		elif 'default' in self.cell_manager.cell.destinations:
			destination = self.cell_manager.cell.destinations['default']
		else:
			destination = False
			
		if destination:
			player.worldPosition = destination.co
			player.worldOrientation = mathutils.Quaternion(destination.rotation).to_matrix()
			self.cell_manager.next_destination = None
		self.KX_player = player

	def handle_time(self):
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

			atmos = bge.logic.getSceneList()[0].objects[self.atmosphere_ctrl]
			atmos['Time'] = self.world_time


	def main(self):
		game.Game.singleton.profiler.start_timer('world.main')
		self.handle_time()

		if self.KX_player:
			if self.player._data == self.KX_player:
				#TODO hook in pause menu here
				self.player.main()
			else:
				self.player._wrap(self.KX_player)
		else:
			self.player._unwrap()		

		self.cell_manager.update()
		if len(self.entity_list) != 0:
			self.ai_manager.main()
		game.Game.singleton.profiler.stop_timer('world.main')
