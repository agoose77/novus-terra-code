import pickle
import random
import mathutils
import datetime

import aud
import bge
from mathutils import Vector

import cell, entity
import dialogue
import entities
import game
from ai_manager import AI_Manager
#from dialogue_system import DialogueSystem
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
		self.entity_manager = entity.EntityManager()
		self.dialogue_manager = dialogue.DialogueManager()

		### Time and date
		self.world_time = 0.0
		self.world_time_scale = 0.05

		self.date = datetime.date(2050, 1, 1) #Y, M, D

		### Weather:
		self.current_weather = None
		self.last_weather = None

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
		self.player.freeze()

	def resume(self):
		self.player.hold_mouse_update = 10  # don't update mouse look for 1 frame, stops jump
		self.suspended = False
		for entity in self.cell_manager.entities_in_game:
			entity.unfreeze()
		self.player.unfreeze()

	def spawn_player(self):
		""" Spawns the player """

		scene = bge.logic.getCurrentScene()
		player = scene.addObject('player', "CELL_MANAGER_HOOK")
		self.KX_player = player

		self.player._wrap(player)

		if self.cell_manager.next_destination:
			destination = self.cell_manager.cell.destinations[self.cell_manager.next_destination]
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
		if self.world_time < 256:
			self.world_time += self.world_time_scale
			self.date = self.date + datetime.timedelta(days=1)
		else:
			self.world_time = 1.0

		### HACK - set the Time prop for all the lighting effects
		if cell.CellManager.singleton.terrain != False:
			lighting = bge.logic.getCurrentScene().objects["outdoor_sun_shadow"]
			sun = bge.logic.getCurrentScene().objects['Sun_Main']

			lighting['Time'] = self.world_time
			sun['Time'] = self.world_time

			atmos = bge.logic.getCurrentScene().objects[self.atmosphere_ctrl]
			atmos['Time'] = self.world_time

		#print(self.world_time
	def lerp(self, n1, n2, n3):
		return ((n2 - n1)*n2)+n1


	def handle_weather(self):

		clear = {
			"Lerp":0.0,
			"Time":0.0,
			"Scale":0.015,
			"Amount":-0.500,
			"Sharpness":0.450,
			"Precipitation":"Rain",
			}

		cloudy = {
			"Lerp":0.0,
			"Time":0.0,
			"Scale":0.01,
			"Amount":-0.300,
			"Sharpness":0.750,
			"Precipitation":"None",
			}

		stormy = {
			"Lerp":0.0,
			"Time":0.0,
			"Scale":0.01,
			"Amount":-0.100,
			"Sharpness":0.850,
			"Precipitation":"None",
			}

		### INIT Weather
		if self.current_weather == None:
			self.current_weather = clear
			self.last_weather = clear

			self.current_weather["Lerp"] = 1.0
			self.current_weather["Time"] = self.world_time

		### Update Weather
		if self.current_weather["Amount"] != 1.0:
			self.current_weather["Lerp"] += 0.01
			amount = self.current_weather["Lerp"]

			clouds = bge.logic.getCurrentScene().objects['Clouds']
			
			clouds['Amount'] = self.lerp(self.current_weather["Amount"],self.last_weather["Amount"], amount)
			clouds['Sharpness'] = self.lerp(self.current_weather["Sharpness"],self.last_weather["Sharpness"], amount)
			clouds['Scale'] = self.lerp(self.current_weather["Scale"],self.last_weather["Scale"], amount)

		### Precipitation
		if self.current_weather['Precipitation'] == "Rain":
			weather_pos = bge.logic.getCurrentScene().objects['weather_pos']

			for child in weather_pos.children:
				if random.randrange(-1,1) == 1:
					new = bge.logic.getCurrentScene().addObject('rain', child)
					new.position = child.position # Need to add randomized position
		
		elif self.current_weather['Precipitation'] == "Dust":
			pass
		else:
			pass

		### Switch to new Weather Type
		if (self.current_weather["Time"] - self.world_time) > 100.0:
			random_number = random.randRange(0,10)

			self.last_weather = self.current_weather

			if random_number > 5:
				self.current_weather = clear
			elif random_number > 7:
				self.current_weather = stormy			
			else:
				self.current_weather = cloudy



	def main(self):

		self.handle_time()
		self.handle_weather()

		if bge.logic.keyboard.events[bge.events.IKEY] == bge.logic.KX_INPUT_ACTIVE:
			self.suspend()
		elif bge.logic.keyboard.events[bge.events.JKEY] == bge.logic.KX_INPUT_JUST_ACTIVATED:
			self.resume()
		
		if self.player._data and self.cell_manager.load_state:
			self.player.main()
		self.dialogue_manager.main()

		self.cell_manager.update()
		if len(self.entity_list) != 0:
			self.ai_manager.main()