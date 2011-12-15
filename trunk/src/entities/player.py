import sys
sys.path.append('./src/')
sys.path.append('./src/weapons/')


import math
import random
import aud
import bge
from mathutils import Vector, Matrix


from sound_manager import SoundManager
from inventory import Inventory
from dialogue_system import DialogueSystem
from finite_state_machine import FiniteStateMachine
from paths import PATH_SOUNDS, PATH_MUSIC

import entities
from item import Item
from weapon import Weapon

import game
import ui


###
class Player(entities.EntityBase):

	def __init__(self):
		print("player.__init__()")

		entities.EntityBase.__init__(self)

		# Player Stats
		self.health = 100
		self.faction = 1		 # Default Faction = Humans

		self.hunger = 0.0
		self.fatigue = 0.0
		self.alert = 0
		self.last_shot = 0.0
		self.reloading = False
		self.reload_start_time = 0.0

		self.walk_speed = 5.0
		self.run_speed = 9.0
		self.walk_temp = 0.0
		self.jump_speed = 10.0

		self.init_1 = False
		self.animations = {
			'walk':0,
			'run':0,
			'shoot':0,
			'reload':0,
			'idle':1,
			'cround':0
			}

		self.bullets_auto = 10
		self.bullets_shotgun = 10
		self.bullets_pistol = 10

		#
		self.impants = []
		self.stats = {'temp':'temp'}

		#
		self.current_weapon= None
		self.current_animations= {
			'walk':None,
			'run':None,
			'reload':None,
			'attack':None,
			'switch':None,
			'aim':None,
		}

		self.talking = False
		self.is_in_combat = False
		self.stored_state = None
		self.camera_on = True

		# Inventory
		self.inventory = Inventory()

		#adding some items for testing:
		self.inventory.add_item('cube', amount=9 )
		self.inventory.add_item('wrench', amount=9)

		#calculating this once for mouse move
		w = bge.render.getWindowWidth()
		h = bge.render.getWindowHeight()
		self.window_middle = [ int((w - int(w)%2)/2), int((h - int(h)%2)/2) ]

	def _wrap(self, object):
		entities.EntityBase._wrap(self, object)

		# Vehicle
		self.current_vehicle = None
		self.vehicle= None

		self.camera = [child for child in self.children if 'camera_1' in child][0]
		self.armature = [child for child in self.childrenRecursive if 'Armature' in child][0]
		self.bullet_spread = [child for child in self.childrenRecursive if 'spread' in child][0]


		# FSM States
		self.movement_state_machine = FiniteStateMachine(self)
		self.movement_state_machine.add_state('walk', self.handle_walk_state)
		self.movement_state_machine.add_state('fall', self.handle_fall_state)
		self.movement_state_machine.add_state('vehicle', self.handle_vehicle_state)
		self.movement_state_machine.add_state('none', self.handle_none_state)

		# FSM Transitions
		self.movement_state_machine.add_transition('fall', 'walk', self.is_grounded)
		self.movement_state_machine.add_transition('walk', 'vehicle', self.has_entered_vehicle)
		self.movement_state_machine.add_transition('vehicle', 'walk', self.has_exited_vehicle)

		game.Game.singleton.world.entity_list.append(self)

		# Dialogue
		#self.dialogue = DialogueSystem([cont.owner.get('ds_width', bge.render.getWindowWidth()-100),cont.owner.get('ds_height', 250)], theme)

		# HACKS
		self.temp_pos = 1
		self.set_loc = [child for child in self.childrenRecursive if 'set_loc' in child][0]
		self.lev = None

	def _unwrap(self):
		entities.EntityBase._unwrap(self)


	def handle_walk_state(self, FSM):
		keyboard = bge.logic.keyboard.events
		vel = self.getLinearVelocity()
		move = [0,0,0]

		### Keys
		if keyboard[bge.events.LEFTSHIFTKEY] and self.fatigue < 10:
			self.fatigue += 0.2
			speed = self.run_speed
		else:
			if self.fatigue > 0.0:
				self.fatigue += -0.2
			speed = self.walk_speed

		if keyboard[bge.events.WKEY]:
			move[0] += speed
		if keyboard[bge.events.SKEY]:
			move[0] -= speed
		if keyboard[bge.events.AKEY]:
			move[1] -= speed
		if keyboard[bge.events.DKEY]:
			move[1] += speed

		### Jump
		if keyboard[bge.events.SPACEKEY] == bge.logic.KX_INPUT_JUST_ACTIVATED:
			pos1 = [self.position[0],self.position[1],self.position[2]-10]
			ray = self.rayCast(pos1, self.position, 2, '', 0, 0, 0)

			if ray[0] != None:
				move[2] = self.jump_speed
				self.walk_temp = 19

		###
		com = vel[2]+move[2]
		self.localLinearVelocity = [move[1],move[0], com]

		###
		if move[0] != 0 or move[1] != 0:
			if speed == self.walk_speed:
				self.play_animation('walk')
				self.walk_temp += 1

			elif speed == self.run_speed:
				self.play_animation('run')
				self.walk_temp += 2
		else:
			#self.play_animation('idle')
			pass

		if self.walk_temp > 20:
			self.walk_temp = 0
			print("Play Sound")
			#session.game.sound_manager.play_sound('walk_grass_1.ogg', self)


	def play_animation(self,name):
		"""
		1 = shoot
		2 = reload
		3 =
		4 = idle
		5 = walk
		6 = run
		"""

		#if name == 'reload':
		#	self.armature.playAction(str(self.inventory.current_weapon.name) + "_reload", 1, 45, layer=2, priority=1, blendin=5, play_mode=bge.logic.KX_ACTION_MODE_LOOP, speed=1.0)

		self.animations[name] = 1


	def handle_animations(self):
		#self.armature.playAction(str(self.inventory.current_weapon.name) + "_idle", 1, 64, layer=1, priority=0, blendin=5, play_mode=bge.logic.KX_ACTION_MODE_LOOP, speed=1.0)

		if self.animations['reload'] == 1:
			print("Playing reload")
			self.armature.playAction(str(self.inventory.current_weapon.name) + "_reload", 1, 24, layer=1, priority=2, blendin=5, play_mode=bge.logic.KX_ACTION_MODE_PLAY, speed=1.0)
			#self.animations['reload'] = 0

		elif self.animations['shoot'] == 1:
			print("Playing shoot")
			self.armature.playAction(str(self.inventory.current_weapon.name) + "_shoot", 1, 5, layer=1, priority=3, blendin=5, play_mode=bge.logic.KX_ACTION_MODE_PLAY, speed=1.0)
			#self.animations['shoot'] = 0

		elif self.animations['walk'] == 1:
			print("Playing walk")
			self.armature.playAction(str(self.inventory.current_weapon.name) + "_walk", 1, 32, layer=1, priority=4, blendin=5, play_mode=bge.logic.KX_ACTION_MODE_PLAY, speed=1.0)
			#self.animations['walk'] = 0

		elif self.animations['run'] == 1:
			print("Playing Run")
			self.armature.playAction(str(self.inventory.current_weapon.name) + "_run", 1, 20, layer=1, priority=5, blendin=5, play_mode=bge.logic.KX_ACTION_MODE_PLAY, speed=1.0)
			#self.animations['run'] = 0

		#elif self.animations['idle'] == 1:
		#else:
			#self.armature.stopAction(1)
		#	print('playing idle')
		#	self.armature.playAction(str(self.inventory.current_weapon.name) + "_idle", 1, 64, layer=1, priority=0, blendin=5, play_mode=bge.logic.KX_ACTION_MODE_LOOP, speed=1.0)

		for name in self.animations:
			self.animations[name] = 0

	def handle_fall_state(self, FSM):
		pass

	def handle_vehicle_state(self, FSM):
		keyboard = bge.logic.keyboard

		bge.logic.getCurrentScene().active_camera = self.vehicle['Camera']

		# HACK
		self.camera_on = False # Turn off player camera
		self.position = [self.vehicle.position[0],self.vehicle.position[1],self.vehicle.position[2]+10]

		# Get out of vehicle
		if keyboard.events[bge.events.EKEY] == 1:
			self.camera_on = True
			self.vehicle['Vehicle'] = False
			self.position = [self.vehicle.position[0],self.vehicle.position[1],self.vehicle.position[2]+10] # add player above the vehicle
			self.vehicle = None

	def is_grounded(self, FSM):
		pos2 = [self.position[0],self.position[1],self.position[2]-5]
		ray2 = self.rayCast(pos2, self._data, 0, '', 0, 0, 0)
		return bool(ray2[0])

	def is_falling(self, FSM):
		pos2 = [self.position[0],self.position[1],self.position[2]-5]
		ray2 = self.rayCast(pos2, self._data, 0, '', 0, 0, 0)
		return not bool(ray2[0])

	def has_entered_vehicle(self, FSM):
		return bool(self.vehicle)
	def has_exited_vehicle(self, FSM):
		return bool(self.vehicle)

	def handle_none_state(self, FSM):
		pass

	def reload(self):
		print("Reloading...")
		if self.inventory.ammo['Assault'] > 0:
			if self.reload_start_time == 0.0:
				self.reload_start_time = game.Game.singleton.game_time

			print (game.Game.singleton.game_time - self.reload_start_time)
			self.play_animation('reload')

			if (game.Game.singleton.game_time - self.reload_start_time) > self.inventory.weapon_slot_1.reload_time:
				print ("DONE RELOADING")
				self.reloading = False

			if self.reloading == False:
				if self.inventory.ammo['Assault'] < self.inventory.weapon_slot_1.clip_size:
					self.inventory.weapon_slot_1.clip = self.inventory.ammo['Assault']
					self.inventory.ammo['Assault'] = 0
				else:
					self.inventory.weapon_slot_1.clip = self.inventory.weapon_slot_1.clip_size
					self.inventory.ammo['Assault'] += -self.inventory.weapon_slot_1.clip_size

				self.reload_start_time = 0.0
		else:
			print("Out Of Ammo!!")


	def handle_weapon(self):
		ray = self.bullet_spread.controllers[0].sensors['weapon_ray']
		ray.range = 200#self.current_weapon.range

		hit = ray.hitObject
		mouse = bge.logic.mouse
		keyboard = bge.logic.keyboard

		# Reload
		if keyboard.events[bge.events.RKEY] == 1:
			self.reloading = True

		# SHOOT
		if mouse.events[bge.events.LEFTMOUSE]:

			# Reload
			if self.inventory.weapon_slot_1.clip == 0:
				self.reloading = True

			# Shoot
			else:
				if self.reloading == False:
					print (game.Game.singleton.game_time - self.last_shot)
					if (game.Game.singleton.game_time - self.last_shot) > self.inventory.weapon_slot_1.fire_speed:
						self.last_shot = game.Game.singleton.game_time

						self.inventory.weapon_slot_1.shoot(self.camera, self.bullet_spread)
						self.play_animation('shoot')

						if hit != None:
							new = bge.logic.getCurrentScene().addObject('B_Hole', self.camera, 100)
							new.position = ray.hitPosition
							new.alignAxisToVect(ray.hitNormal, 2, 1.0)
							new.setParent(hit)

							if 'physics' in hit:
								hit['physics'] = 1

							if 'Health' in hit:
								hit['Health'] += -10

		# AIM
		if mouse.events[bge.events.RIGHTMOUSE] == 1:
			pass


	def handle_interactions(self):
		ray = self.camera.controllers[0].sensors['interact_ray']
		hit = ray.hitObject
		keyboard = bge.logic.keyboard

		if keyboard.events[bge.events.BKEY]: # Dominate
			self.armature.playAction(str(self.inventory.current_weapon.name) + "_walk", 1, 32, layer=5, priority=2, blendin=5, play_mode=bge.logic.KX_ACTION_MODE_LOOP, speed=1.0)
			#self.play_animation('run')

		elif keyboard.events[bge.events.NKEY]:
			self.armature.playAction(str(self.inventory.current_weapon.name) + "_reload", 1, 32, layer=5, priority=6, blendin=5, play_mode=bge.logic.KX_ACTION_MODE_LOOP, speed=1.0)

		else:
			self.armature.stopAction(5)

		if hit != None and 'entity_base' in hit:
			if keyboard.events[bge.events.EKEY] == 1:
				hit['entity_base'].on_interact(self)


	def fast_travel(self, location):
		self.position = location_id.position
		# handle world cells

	def handle_camera(self):
		bge.logic.getCurrentScene().active_camera = self.camera # set active_camera

		mpos = bge.logic.mouse.position

		bge.render.setMousePosition(self.window_middle[0], self.window_middle[1])
		#bge.render.setMousePosition(int(w/2), int(h/2))

		if not 'ml_rotx' in self.camera:
			self.camera['ml_rotx'] = -(self.camera.localOrientation.to_euler().x - (math.pi * 0.5))

		else:
			mouse_mx = (mpos[0] - 0.5) * 3#bge.logic.globalDict['game'].control_options[1]#MOUSE_SENSITIVITY # bge.logic.globalDict['game'].control_options[Game.MOUSE_SENSITIVITY]
			mouse_my = (mpos[1] - 0.5) * 3#bge.logic.globalDict['game'].control_options[1]#MOUSE_SENSITIVITY

			cap = 1.5

			if -(self.camera['ml_rotx'] + mouse_my) < cap and -(self.camera['ml_rotx'] + mouse_my) > -cap:
				if abs(mouse_mx) > 0.0025 or abs(mouse_my) > 0.0025:
					self.camera.parent.applyRotation([0, 0, -mouse_mx], 0) # X
					self.camera.applyRotation([-mouse_my, 0, 0], 1) # Y
					self.camera['ml_rotx'] += mouse_my

	def remove_controls(self):
		self.stored_state = self.movement_state_machine.current_state
	def restore_controls(self):
		self.movement_state_machine.current_state = self.stored_state

	###
	def main(self):
		if bge.logic.globalDict['pause'] == 0 and self._data:
			entities.EntityBase.main(self)

			self.movement_state_machine.main()
			self.handle_camera()
			self.handle_interactions()

			if self.inventory.current_weapon.name != 'Hands':
				self.handle_animations()
				self.handle_weapon()

			if self.reloading == True:
				self.reload()

