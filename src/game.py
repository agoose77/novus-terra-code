import pickle
import sys
import time
sys.path.append('./src/')

import bge

import entities
from paths import safepath
from item import Item
from sound_manager import SoundManager
from world import World
from ai_manager import AI_Manager
from console_ import Console
import session

def main():
	if Game.singleton is None:
		Game()

	Game.singleton.update()

class Game:
	FORWARD_KEY = 0
	BACKWARD_KEY = 1
	STRAFE_LEFT_KEY = 2
	STRAFE_RIGHT_KEY = 3
	ACTION_KEY = 4
	SWITCH_WEAPON_KEY = 5
	JUMP_KEY = 6
	RUN_KEY = 7
	AIM_WEAPON_KEY = 8
	SHOOT_WEAPON_KEY = 9
	MOUSE_SENSITIVITY = 6

	entity_map = { # Maps class names to class definitions
		'Door': entities.Door,
		'EntityBase' : entities.EntityBase,
		'WeaponPickup' : entities.WeaponPickup,
		'Container' : entities.Container
	}

	singleton = None

	def __init__(self):
		print("game.__init__()")
		Game.singleton = self
		self.game_started = time.time()
		self.game_time = 0.0
		self.delta_time = 0.0001

		self.graphics_options = {
			'Fade in props':True,
			'HDR':False,
			'Bloom':False,
			'DOF':False,
			'SSAO':True,
			'SSAO_samples':3,
			'SSAA':False,
			'Color':False,
			'Motion Blur':False,
			'Fog':True,
			'camera_clip': 1000,
			}

		self.game_options = {
			'Difficulty':1,
			'Hardcore':False,
			}

		self.sound_options = {
			'Effect Volume':1.0,
			'Music Volume':1.0,
			'Voice Volume':1.0,
			}

		self.control_options = {\
			Game.FORWARD_KEY: bge.events.WKEY,
			Game.BACKWARD_KEY: bge.events.SKEY,
			Game.STRAFE_LEFT_KEY: bge.events.AKEY,
			Game.STRAFE_RIGHT_KEY: bge.events.DKEY,
			Game.ACTION_KEY: bge.events.EKEY,
			Game.SWITCH_WEAPON_KEY: bge.events.FKEY,
			Game.JUMP_KEY: bge.events.SPACEKEY,
			Game.RUN_KEY: bge.events.LEFTSHIFTKEY,
			Game.AIM_WEAPON_KEY: bge.events.RIGHTMOUSE,
			Game.SHOOT_WEAPON_KEY: bge.events.LEFTMOUSE,
			Game.MOUSE_SENSITIVITY: 5.0,
		}

		self.default_cell = 'terrain.cell'

		self.world = None
		self.sound_manager = SoundManager()

		self.console = Console(safepath('./data/fonts/phaisarn.ttf'), bge.events.ACCENTGRAVEKEY)

		self.fx_object = bge.logic.getCurrentScene().objects['FX']
		self.fx_object_blur = bge.logic.getCurrentScene().objects['FX BLUR']
		
		# load items
		file = open('./data/items.data', 'rb')
		items = pickle.load(file)
		file.close()
		
		for item in items:
			Item(id=item[0], name=item[1], type=item[2], description=item[3], icon=item[4], cost=item[5], size=item[6], stack=item[7])


	def update_filters(self):
		print("Updating Filters v2")
		session.profiler.start_timer('fx.update')

		for prop in session.game.graphics_options:
			"""
			if prop != 'camera_clip':
				pass
			elif prop != 'SSAO_sample':
				pass
			"""
			if prop != 'Motion Blur':
				self.fx_object[prop] = session.game.graphics_options[prop]
			else:
				self.fx_object_blur[prop] = session.game.graphics_options[prop]

		session.profiler.stop_timer('fx.update')
		print("Updating Filters v2 DONE")


	def update(self):
		self.delta_time = (time.time()-self.game_started) - self.game_time
		self.game_time += self.delta_time

		if self.world == None:
			self.world = World()

		self.world.main()
		self.sound_manager.main()
		self.console.main()

