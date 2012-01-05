import pickle
import random
import mathutils

import aud
import bge
from mathutils import Vector

import cell
import dialogue
import entities
import game
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
		self.dialogue_manager = dialogue.DialogueManager()

		self.world_time = 80.0
		self.world_time_scale = 0.01

		### Light
		self.light_sources = None
		self.outside_lighting_ctrl = 'outdoor_sun_shadow'
		self.sky_dome = 'sky_dome'
		self.atmosphere_ctrl = 'atmosphere_time'

		###
		self.gravity = Vector([0,0, -9.8])
		bge.logic.setGravity([0,0,0])
		self.world_effects = {'mist color':[0.0,0.0,0.0], 'tint':[0.0,0.0,0.0]}
		
		self.gamestate = 'loading'
		self.suspended = False
		self.KX_player = False

	def cell_loaded(self):
		self.gamestate = 'loaded'
		self.spawn_player()
		
	def cell_loading(self):
		self.gamestate = 'loading'
		self.KX_player = False
		
	def suspend(self):
		self.suspended = True
		for entity in self.cell_manager.entities_in_game:
			entity.freeze()

	def resume(self):
		self.suspended = False
		for entity in self.cell_manager.entities_in_game:
			entity.unfreeze()

	def spawn_player(self):
		""" 
		Spawns the player
		"""
		# player needs to be spawned
		scene = bge.logic.getCurrentScene()
		player = scene.addObject('player', "CELL_MANAGER_HOOK")

		self.player._wrap(player)

		if self.cell_manager.next_destination:
			destination = self.cell_manager.next_destination
		elif 'default' in self.cell_manager.cell.destinations:
			destination = self.cell_manager.cell.destinations['default']
		else:
			destination = False
		
		if destination:
			self.player.worldPosition = destination.co
			self.player.worldOrientation = mathutils.Quaternion(destination.rotation).to_matrix()
			self.cell_manager.next_destination = None

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

		if bge.logic.keyboard.events[bge.events.IKEY] == bge.logic.KX_INPUT_ACTIVE:
			self.suspend()
		elif bge.logic.keyboard.events[bge.events.JKEY] == bge.logic.KX_INPUT_JUST_ACTIVATED:
			self.resume()
		
		if self.player._data and self.cell_manager.load_state and not self.suspended:
			self.player.main()
		self.dialogue_manager.main()

		self.cell_manager.update()
		if len(self.entity_list) != 0:
			self.ai_manager.main()
		game.Game.singleton.profiler.stop_timer('world.main')
