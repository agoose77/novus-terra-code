import sys
sys.path.append('./src/')

import time

import bge

from entity_base import EntityBase
from player import Player
from item import Item
#from savefile import Savefile
#from sound_manager import SoundManager
from world import World

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

	entity = {\
		'EntityBase': EntityBase,
		'Player': Player,
		'Item': Item,
		}

	def __init__(self):
		print("game.__init__()")
		self.game_started = time.time()
		self.game_time = 0.0
		self.delta_time = 0.0001

		self.graphics_options = {\

			}

		self.game_options = {\

			}

		self.sound_options = {\

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

		#self.current_savefile = self.get_last_played_savefile()
		#self.sound_manager = SoundManager()
		self.world = None

		#bge.logic.getCurrentScene().replace('world')

	def main(self):

		self.delta_time = (time.time()-self.game_started) - self.game_time
		self.game_time += self.delta_time

		if self.world == None:
			print ('TEsTSET =====================')
			self.world = World()
		#    self.world.create('novus_terra.world')

		self.world.main()

	def get_last_played_savefile(self):
		return Savefile('/saves/blah')
