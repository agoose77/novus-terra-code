import sys
sys.path.append('./src/')
sys.path.append('./src/bgui/')
import math

import aud
from paths import PATH_SOUNDS, PATH_MUSIC

import bge
from mathutils import Vector, Matrix

from entity_base import EntityBase
from finite_state_machine import FiniteStateMachine

from sound_manager import SoundManager
from Inventory import Inventory

import ui

###
class AIBase(EntityBase):

	def __init__(self):
		print("AIBase.__init__()")
		EntityBase.__init__(self, 'ai_base')

		#
		self.armature = self.armature = [child for child in self.childrenRecursive if 'Armature' in child][0]

		# Stats
		self.health = 100
		self.speed = 10
		self.ammo = 100

		#
		self.allies = []
		self.enemies = []

		# Pathfinding
		self.target = 'target_point'
		self.navmesh = None
		self.object = None

        # FSM States
		self.ai_state_machine = FiniteStateMachine(self)
		self.ai_state_machine.add_state('engage', self.handle_engage)
		self.ai_state_machine.add_state('idle', self.handle_idle)
		self.ai_state_machine.add_state('talk', self.handle_talk)
		self.ai_state_machine.add_state('flee', self.handle_flee)

		# Hacks...
		self.ai_state_machine.current_state = 'idle'

	def handle_engage(self, FSM):
		self.handle_movement()

	def handle_idle(self, FSM):
		self.detect_enemies()

	def handle_talk(self, FSM):
		pass

	def handle_flee(self, FSM):
		self.handle_movement(behavior=1)

	def detect_enemies(self):
		pass

	def handle_movement(self, behavior=3):
		#if cell.singleton.navmesh != False:
		#	nav = None
		#else:
		#	nav = cell.singleton.navmesh
		#nav = None

		# Stuff
		st = self.controllers[0].actuators['Steering']
		st.behaviour = behavior

		# Speed
		st.velocity = 0.5
		st.acceleration = 0.1
		st.turnspeed = 120

		#
		for obj in bge.logic.getCurrentScene().objects:
			if 'target_point' in obj.name:
				st.target = obj#'target_point' # Replace

		#if nav != None:
		st.navmesh = bge.logic.getCurrentScene().objects['Navmesh']

		# Activate it
		self['Steer'] = 1

		# Animations
		if self.armature.isPlayingAction() == False:
			self.armature.playAction("1_walk", 1, 33, layer=0, priority=0, blendin=0, play_mode=bge.logic.KX_ACTION_MODE_PLAY, speed=1.0)


	def is_scared():
		return False

	###
	def main(self):
		EntityBase.main(self)
		self.ai_state_machine.main()
		#print (self.armature.isPlayingAction())

		# Run away
		if self.is_scared == True:
			self.ai_state_machine.current_state = 'flee'