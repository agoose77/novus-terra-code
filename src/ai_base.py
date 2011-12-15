import math
import random
import sys
sys.path.append('./src/')
sys.path.append('./src/bgui/')

import aud
import bge
from mathutils import Vector, Matrix

import game
import ui
from entities import EntityBase
from finite_state_machine import FiniteStateMachine
from inventory import Inventory
from paths import PATH_SOUNDS, PATH_MUSIC
from sound_manager import SoundManager

###
class AIBase(EntityBase):

	def __init__(self, object):
		print("AIBase.__init__()")
		EntityBase.__init__(self)
		EntityBase._wrap(self, object)

		# Stats
		self.health = 100
		self.speed = 10
		self.ammo = 100
		self.faction = -1

		self.alert = 0
		self.sighted = 0
		self.impatience = 0

		# Track
		self.allies = []
		self.enemies = []
		self.animations= []
		self.ryn = random.randrange(-5,5)
		self.rxn = random.randrange(-5,5)

		# Pathfinding
		self.target_entity = None
		self.navmesh = None
		self.object = None

		# Inventory
		self.current_weapon= None
		self.current_weapon_clip = 50
		self.inventory = Inventory()

		# Children
		self.armature = [child for child in self.childrenRecursive if 'Armature' in child][0]
		self.target_obj = [child for child in self.childrenRecursive if 'target_obj' in child][0]

		self.aimer = [child for child in self.childrenRecursive if 'aimer' in child][0]
		self.bullet_spread = [child for child in self.childrenRecursive if 'spread' in child][0]
		self.weapon_pos = [child for child in self.childrenRecursive if 'weapon_pos' in child][0]

		# FSM States
		self.ai_state_machine = FiniteStateMachine(self)
		self.ai_state_machine.add_state('engage', self.handle_engage)
		self.ai_state_machine.add_state('idle', self.handle_idle)
		self.ai_state_machine.add_state('talk', self.handle_talk)
		self.ai_state_machine.add_state('flee', self.handle_flee)
		self.ai_state_machine.add_state('dead', self.handle_dead)

		#self.ai_state_machine.add_transition('idle', 'engage', self.is_enemy_near)
		#self.ai_state_machine.add_transition('engage', 'flee', self.is_fleeing)
		#self.ai_state_machine.add_transition('engage', 'dead', self.is_dead)

		# Hacks...
		self.ai_state_machine.current_state = 'engage'


	def _unwrap(self):
		EntityBase._unwrap(self)


	""" FSM States """
	def handle_engage(self, FSM):
		enemies = self.detect_enemies()
		cover = self.find_cover()

		if self.target == None:
			print("AI: -- Get Target --")
			if len(enemies) > 0:
				closest = enemies[0]
				self.target_entity = closest[1]

		else:
			dist = self.getDistanceTo(self.target.position)

			ray = self.rayCast(self.target.position, self.aimer.position, 0, '', 0, 0, 0)
			print(self.target.name)

			self.impatience += 0.01
			"""
			if self.impatience > 50:
				# In sight
				if str(ray[0]) == str(self.target.name):
					self.attack()
					self.armature.playAction("pistol_shoot", 1, 32, layer=1, priority=1, blendin=0, play_mode=bge.logic.KX_ACTION_MODE_LOOP, speed=1.0)
					self['Steer'] = 0
					self.sighted = 1

				# Walk
				else:
					self.move_to(self.target, offset = 1)


			else:
			"""
		

			# Far away > move closer
			if dist > 200:
				print("Test")
				self.move_to(self.target.position, offset = 1)

			# Close enough
			else:
				print("YY")

				# In sight
				if str(ray[0]) == str(self.target.name):
					self.attack()
					self.armature.playAction("pistol_shoot", 1, 32, layer=1, priority=1, blendin=0, play_mode=bge.logic.KX_ACTION_MODE_LOOP, speed=1.0)
					self['Steer'] = 0
					self.sighted = 1

				# Walk
				else:
					self.move_to(self.target.position, offset = 1)
				"""
				else:
					# In sight
					if str(ray[0]) == str(self.target.name):
						self.attack()
						self.armature.playAction("pistol_shoot", 1, 32, layer=1, priority=1, blendin=0, play_mode=bge.logic.KX_ACTION_MODE_LOOP, speed=1.0)
						self['Steer'] = 0

					# Walk
					else:
						print('Test')
						cover = self.find_cover()

						if len(cover) > 0:
							if cover[0][0] > 2:
								print(cover[0])
								self.move_to(cover[0][1], offset = 1)
							else:
								printf("on the Look out")
								self.defend()
						else:
							print('Test')
							self.move_to(self.target, offset = 1)
							"""



	def handle_dead(self, FSM):
		print("Dead!!!")
		self['Steer'] = 0
		#self.armature.playAction("pistol_idle", 1, 32, layer=1, priority=0, blendin=0, play_mode=bge.logic.KX_ACTION_MODE_LOOP, speed=1.0)

	def handle_idle(self, FSM):
		self['Steer'] = 0
		self.armature.playAction("pistol_idle", 1, 32, layer=1, priority=0, blendin=0, play_mode=bge.logic.KX_ACTION_MODE_LOOP, speed=1.0)

	def handle_talk(self, FSM):
		self['Steer'] = 0
		self.armature.playAction("pistol_idle", 1, 32, layer=1, priority=0, blendin=0, play_mode=bge.logic.KX_ACTION_MODE_LOOP, speed=1.0)

	def handle_flee(self, FSM):
		self.move_to(behavior=1)
		self.armature.playAction("pistol_run", 1, 32, layer=1, priority=0, blendin=0, play_mode=bge.logic.KX_ACTION_MODE_LOOP, speed=1.0)






	""" Misc Functions """
	def find_cover(self):
		scene = bge.logic.getCurrentScene()
		temp = []

		for obj in scene.objects:
			if 'cover' in obj:
				dist = self.getDistanceTo(obj)
				if self.target != None:
					dist2 = self.target.getDistanceTo(obj)
				else:
					dist2 = 0

				temp.append([dist, obj, dist2])
		temp.sort()
		return temp


	def detect_enemies(self):
		temp = []

		self.allies = []
		self.enemies = []

		radar = self.aimer.controllers[0].sensors['Radar']

		for objt in radar.hitObjectList:
			objl = [temp for temp in game.Game.singleton.world.entity_list if temp._data == objt]

			for temp2 in game.Game.singleton.world.entity_list:
				if temp2.faction != self.faction:

					t_dist = self.getDistanceTo(temp2.position)

					if t_dist < 5:
						return [[t_dist, temp2],[1],[1]]

			if len(objl) > 0:
				obj = objl[0]
				if obj.faction != self.faction:

					if self.alert == 0:
						ray = self.rayCast(obj.position, self.aimer.position, 0, '', 0, 0, 0)

						if ray[0].name == obj.name:
							dist = self.getDistanceTo(obj.position)
							temp.append([dist, obj])
							self.alert = 1
					else:
						dist = self.getDistanceTo(obj.position)
						temp.append([dist, obj])

				else:
					self.allies.append(obj)

		temp.sort()
		return temp


	###
	def move_to(self, target_pos, behavior=3, offset=0, speed=2):

		# Stuff
		st = self.controllers[0].actuators['Steering']
		st.behaviour = behavior

		# Speed
		st.velocity = speed
		st.acceleration = 0.5
		st.turnspeed = 10

		# Offset Target
		if offset == 1:
			ry = target_pos[0] + self.ryn
			rx = target_pos[1] + self.rxn
		else:
			ry = target_pos[0]#self.target.position[0] + self.ryn
			rx = target_pos[1]#self.target.position[1] + self.rxn

		self.target_obj.position = [ry, rx, self.target.position[2]]
		st.target = self.target_obj


		st.navmesh = bge.logic.getCurrentScene().objects['Navmesh1']

		# Activate it
		self['Steer'] = 1
		self.armature.playAction("pistol_walk", 1, 33, layer=5, priority=1, blendin=5, play_mode=bge.logic.KX_ACTION_MODE_LOOP, speed=1.0)


	def defend(self):
		self.track()
		self.armature.playAction("crouch", 1, 33, layer=5, priority=1, blendin=5, play_mode=bge.logic.KX_ACTION_MODE_LOOP, speed=1.0)


	def attack(self):
		self.track()

		# Play Sound
		ray = self.bullet_spread.controllers[0].sensors['weapon_ray']
		hit = ray.hitObject
		#frame = self.armature.getActionFrame()

		# SHOOT
		#if frame > 3.00 and frame < 3.10:

		### Reload
		#if self.inventory.weapon_slot_1.clip == 0:
		#if 1 == 2:
		#	pass
		#	self.reload()
			#self.inventory.weapon_slot_1.reload()

		# Shoot
		#else:
		#self.inventory.weapon_slot_1.shoot()

		#session.game.sound_manager.play_sound(self.inventory.weapon_slot_1.fire_sound, self)
		#self.play_animation('shoot')
		#print("Shoot")

		# Spread
		self.bullet_spread['X'] = random.randrange(-5,5)
		self.bullet_spread['Z'] = random.randrange(-5,5)

		# Bullet Line
		line = bge.logic.getCurrentScene().addObject('bullet_line', self.aimer, 100)
		#line.position = self.inventory.weapon_slot_1.muzzle.position
		line.orientation = self.bullet_spread.orientation

		#self.notify()

		#flash = bge.logic.getCurrentScene().addObject(self.inventory.weapon_slot_1.flash, self.camera, 100)
		#flash.position = self.inventory.weapon_slot_1.muzzle.position

		if hit != None:
			new = bge.logic.getCurrentScene().addObject('B_Hole', self.aimer, 100)
			new.position = ray.hitPosition
			new.alignAxisToVect(ray.hitNormal, 2, 1.0)
			new.setParent(hit)

			if 'physics' in hit:
				hit['physics'] = 1


		self.armature.playAction("pistol_walk", 1, 33, layer=5, priority=1, blendin=5, play_mode=bge.logic.KX_ACTION_MODE_LOOP, speed=1.0)
		#print("done Shoot")


	def play_animation(self,name):

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



	""" Checks """
	def is_scared():
		return False

	def is_dead(self, FSM):
		if self['Health'] < 0:
			return True
		else:
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



	""" Main """
	def main(self):
		self.target_obj.removeParent()

		EntityBase.main(self)
		self.ai_state_machine.main() # Please turn back on
		#self.detect_enemies()

		if self.alert == 1:
			for entity in game.Game.singleton.world.entity_list:
				dist = self.getDistanceTo(entity.position)

				if dist < 5:
					entity.alert = 1

		# Run away
		if self.is_scared == True:
			self.ai_state_machine.current_state = 'flee'



