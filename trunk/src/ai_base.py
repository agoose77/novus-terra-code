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
import session

###
class AIBase(EntityBase):

	def __init__(self):
		print("AIBase.__init__()")
		#EntityBase.__init__(self, 'ai_base')

	def _wrap(self, object):
		EntityBase._wrap(self, object)
		#bge.logic.globalDict['game'].world.entity_list.append(self)

		#
		self.armature = [child for child in self.childrenRecursive if 'Armature' in child][0]
		self.target_obj = [child for child in self.childrenRecursive if 'target_obj' in child][0]
		self.target_obj.removeParent()

		self.aimer = [child for child in self.childrenRecursive if 'aimer' in child][0]
		self.weapon_pos = [child for child in self.childrenRecursive if 'weapon_pos' in child][0]

		# Stats
		self.health = 100
		self.speed = 10
		self.ammo = 100
		self.faction = -1
		self.alert = 0

		# Track
		self.allies = []
		self.enemies = []
		self.animations= []

		# Pathfinding
		self.target = None
		self.navmesh = None
		self.object = None

		#
		self.current_weapon= None
		self.current_weapon_clip = 50

		# Inventory
		self.inventory = Inventory()

        # FSM States
		self.ai_state_machine = FiniteStateMachine(self)
		self.ai_state_machine.add_state('engage', self.handle_engage)
		self.ai_state_machine.add_state('idle', self.handle_idle)
		self.ai_state_machine.add_state('talk', self.handle_talk)
		self.ai_state_machine.add_state('flee', self.handle_flee)

		self.ai_state_machine.add_transition('idle', 'engage', self.is_enemy_near)
		self.ai_state_machine.add_transition('engage', 'flee', self.is_fleeing)

		# Hacks...
		self.ai_state_machine.current_state = 'engage'

		#
	#	self.inventory.add_item()
	#	self.inventory.add_item()


	###
	def handle_engage(self, FSM):
		#print("Engage")
		enemies = self.detect_enemies()
		closest = enemies[0]
		self.target = closest[1]
		dist = closest[0]

		ray = self.aimer.rayCast(self.target.position, self.position, 0, '', 0, 0, 0)

		if dist > 10:
			self.handle_movement()
		else:
			if ray != self.target:
				self.handle_attack()
				self['Steer'] = 0
			else:
				self.handle_movement()

	def handle_idle(self, FSM):
		self['Steer'] = 0
		#self.armature.playAction("walk", 1, 32, layer=5, priority=0, blendin=0, play_mode=bge.logic.KX_ACTION_MODE_LOOP, speed=1.0)

	def handle_talk(self, FSM):
		self['Steer'] = 0
		#self.armature.playAction("walk", 1, 32, layer=5, priority=0, blendin=0, play_mode=bge.logic.KX_ACTION_MODE_LOOP, speed=1.0)

	def handle_flee(self, FSM):
		self.handle_movement(behavior=1)

	###
	def detect_enemies(self):
		temp = []

		self.allies = []
		self.enemies = []

		for obj in session.game.world.entity_list:
			if obj.name != self.name:
				if obj.faction != self.faction:

					# Dont need to see enemy
					if self.alert == 1:
						dist = self.getDistanceTo(obj.position)
						temp.append([dist, obj])
					else:
						# Ray Cast  -----
						dist = self.getDistanceTo(obj.position)
						temp.append([dist, obj])
				else:
					self.allies.append(obj)

		temp.sort()
		return temp

	def handle_movement(self, behavior=3):

		# Stuff
		st = self.controllers[0].actuators['Steering']
		st.behaviour = behavior

		# Speed
		st.velocity = 0.5
		st.acceleration = 0.1
		st.turnspeed = 120

		#
		self.target_obj.position = self.target.position
		st.target = self.target_obj

		#if nav != None:
		st.navmesh = bge.logic.getCurrentScene().objects['Navmesh']

		# Activate it
		self['Steer'] = 1

		# Animations
		#if self.do_animation('pistol_walk', 'check') == False:
			#self.do_animation('pistol_idle', 'remove')
		self.armature.playAction("walk", 1, 33, layer=5, priority=1, blendin=5, play_mode=bge.logic.KX_ACTION_MODE_LOOP, speed=1.0)

	def handle_attack(self):
		#print("Attacking")
		self.track()

		# Play Sound
		#bge.logic.globalDict['game'].sound_manager.play_sound('shoot_temp.ogg', self)

        # Remove Ammo from clip
		if self.current_weapon_clip > 0:
			self.current_weapon_clip += -1
		else:
			print("Reload")
			self.current_weapon_clip = 30
		# Hurt Target

		frame = self.armature.getActionFrame()

		if frame > 3.00 and frame < 3.10:
			print("BAM")
			bge.logic.globalDict['game'].sound_manager.play_sound('shoot_temp.ogg', self)


		#if self.do_animation('pistol_shoot', 'check') == False:
			#self.do_animation('pistol_walk', 'remove')
			#self.do_animation('pistol_idle', 'remove')
		self.armature.playAction("walk", 1, 33, layer=5, priority=1, blendin=5, play_mode=bge.logic.KX_ACTION_MODE_LOOP, speed=1.0)

	def is_scared():
		return False

	def is_enemy_near(self, FSM):
		enemies = self.detect_enemies()
		return bool(enemies != None)

	def is_fleeing(self, FSM):
		moral = 0
		moral += -len(self.enemies)
		moral += len(self.allies)
		moral += -(self.health - 100)*0.25
		return False

	def play_animation(self,name):

		"""
		1 = shoot
		2 = reload
		3 =
		4 = idle
		5 = walk
		6 = run
		"""

		if name == 'idle':
			self.armature.playAction(str(self.inventory.current_weapon.name) + "_idle", 1, 64, layer=4, priority=1, blendin=5, play_mode=bge.logic.KX_ACTION_MODE_LOOP, speed=1.0)
			self.armature.stopAction(5)
			self.armature.stopAction(6)

		if name == 'shoot':
			self.armature.playAction(str(self.inventory.current_weapon.name) + "_shoot", 1, 5, layer=1, priority=1, blendin=5, play_mode=bge.logic.KX_ACTION_MODE_LOOP, speed=1.0)
			self.armature.stopAction(4)
			self.armature.stopAction(5)
			self.armature.stopAction(6)

		if name == 'reload':
			self.armature.playAction(str(self.inventory.current_weapon.name) + "_reload", 1, 24, layer=2, priority=1, blendin=5, play_mode=bge.logic.KX_ACTION_MODE_LOOP, speed=1.0)
			self.armature.stopAction(5)

		if name == 'walk':
			self.armature.playAction("walk", 1, 32, layer=5, priority=1, blendin=5, play_mode=bge.logic.KX_ACTION_MODE_LOOP, speed=1.0)
			self.armature.stopAction(4)
			self.armature.stopAction(6)

		if name == 'run':
			self.armature.playAction(str(self.inventory.current_weapon.name) + "_run", 1, 64, layer=6, priority=1, blendin=5, play_mode=bge.logic.KX_ACTION_MODE_LOOP, speed=1.0)
			self.armature.stopAction(4)
			self.armature.stopAction(5)


	def track(self):
		vec = self.getVectTo(self.target.position)
		self.alignAxisToVect(-vec[1], 1, 0.5)
		self.alignAxisToVect([0,0,1], 2, 1)

	###
	def main(self):
		EntityBase.main(self)
		self.ai_state_machine.main()
	#	print (self.armature.isPlayingAction())

		# Run away
		if self.is_scared == True:
			self.ai_state_machine.current_state = 'flee'



