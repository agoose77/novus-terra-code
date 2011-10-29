import sys
sys.path.append('./src/')
sys.path.append('./src/weapons/')
#import pyglet
import math

import aud
from paths import PATH_SOUNDS, PATH_MUSIC

import bge
from mathutils import Vector, Matrix

from entity_base import EntityBase
from finite_state_machine import FiniteStateMachine
from behavior_tree import BehaviorTree

import random

try:
    from game import Game
except:
	print('problem importing Game')

#from game import *
from item import Item
from weapon import Weapon
from sound_manager import SoundManager
from Inventory import Inventory
from dialogue_system import DialogueSystem
#from world import World
import ui
import session

###
class Player(EntityBase):

	def __init__(self):
		print("player.__init__()")

		# Player Stats
		self.health = 100
		self.faction = 1 		# Default Faction = Humans

		self.hunger = 0.0
		self.fatigue = 0.0
		self.alert = 0

		self.walk_speed = 8.0
		self.run_speed = 15.0
		self.walk_temp = 0.0

		self.init_1 = False
		self.animations= []

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
		self.inventory.add_item( Item( 0, 2, 'SMG machine gun', description='This is a gun you use to shoot things./nJust point and shoot', size=1, cost=0, effects={}), amount=1 )
		self.inventory.add_item( Item( 0, 0, '22 mm ammo', description='ammo that goes in the gun', size=1, cost=0, effects={}), amount=56 )
		self.inventory.add_item( Item( 0, 0, 'wrench', description='a wrench', size=1, cost=0, effects={}, icon='wrench.png'), amount=1 )
		print (self.inventory.items)

	def _wrap(self, object):
		EntityBase._wrap(self, object)
		#JP - stuff i think might involve a specific wrapped object, was moved here from __init__
		# Vehicle
		self.current_vehicle = None
		self.vehicle= None

		self.camera = [child for child in self.children if 'camera_1' in child][0]
		#self.h_camera = [child for child in self.children if 'camera_2' in child][0]
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
		session.game.world.entity_list.append(self)

		# Dialogue
		#self.dialogue = DialogueSystem([cont.owner.get('ds_width', bge.render.getWindowWidth()-100),cont.owner.get('ds_height', 250)], theme)

		# HACKS
		self.temp_pos = 1
		self.set_loc = [child for child in self.childrenRecursive if 'set_loc' in child][0]
		self.lev = None

	def _unwrap(self):
		EntityBase._unwrap(self)

	def handle_walk_state(self, FSM):
		keyboard = bge.logic.keyboard.events
		vel = self.getLinearVelocity()
		move = [0,0,0]

		### Keys
		if keyboard[bge.events.LEFTSHIFTKEY]:
			speed = self.run_speed
		else:
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
		pos1 = [self.position[0],self.position[1],self.position[2]-10]
		ray = self.rayCast(pos1, self.position, 2, '', 0, 0, 0)

		if ray[0] != None:
			if keyboard[bge.events.SPACEKEY] == bge.logic.KX_INPUT_JUST_ACTIVATED:
				move[2] = 5
				self.walk_temp = 19

		###
		com = vel[2]+move[2]
		self.localLinearVelocity = [move[1],move[0], com]

		###
		if move[0] + move[1] != 0:
			if speed == self.walk_speed:
				self.play_animation('walk')
				self.walk_temp += 1

			elif speed == self.run_speed:
				self.play_animation('run')
				self.walk_temp += 2
		else:
			self.play_animation('idle')

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
			self.armature.playAction(str(self.inventory.current_weapon.name) + "_walk", 1, 32, layer=5, priority=1, blendin=5, play_mode=bge.logic.KX_ACTION_MODE_LOOP, speed=1.0)
			self.armature.stopAction(4)
			self.armature.stopAction(6)

		if name == 'run':
			self.armature.playAction(str(self.inventory.current_weapon.name) + "_run", 1, 64, layer=6, priority=1, blendin=5, play_mode=bge.logic.KX_ACTION_MODE_LOOP, speed=1.0)
			self.armature.stopAction(4)
			self.armature.stopAction(5)

	def somethin():
		if p[0] == 'Item':
			p[1] = Weapon(1, 'P90', description='', size=1, cost=0, effects={}, icon='cube.png', clip_size = 30, ammo_type = 1, weapon_type = 'Pistol')


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

	# ???
	def handle_none_state(self, FSM):
		pass

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

	def has_pressed_jumpkey(self, FSM):
		pass

	def has_entered_none(self, FSM):
		pass

	def has_exited_none(self, FSM):
		pass

	def reload(self):
		print("Reloading...")
		print (self.inventory.ammo['Assault'])

		if self.inventory.ammo['Assault'] < self.inventory.weapon_slot_1.clip_size:
			self.inventory.weapon_slot_1.clip = self.inventory.ammo['Assault']
			self.inventory.ammo['Assault'] = 0
		else:
			self.inventory.weapon_slot_1.clip = self.inventory.weapon_slot_1.clip_size
			self.inventory.ammo['Assault'] += -self.inventory.weapon_slot_1.clip_size

	def handle_weapon(self):
		ray = self.bullet_spread.controllers[0].sensors['weapon_ray']
		ray.range = 200#self.current_weapon.range

		hit = ray.hitObject
		mouse = bge.logic.mouse
		keyboard = bge.logic.keyboard

		# Reload
		if keyboard.events[bge.events.RKEY] == 1:
			self.reload()

		# SHOOT
		if mouse.events[bge.events.LEFTMOUSE] == 1:

			# Reload
			if self.inventory.weapon_slot_1.clip == 0:
				self.reload()
				self.inventory.weapon_slot_1.reload()

			# Shoot
			else:
				self.inventory.weapon_slot_1.shoot()

				#session.game.sound_manager.play_sound(self.inventory.weapon_slot_1.fire_sound, self)
				self.play_animation('shoot')

				# Spread
				self.bullet_spread['X'] = random.randrange(-5,5)
				self.bullet_spread['Z'] = random.randrange(-5,5)

				# Bullet Line
				line = bge.logic.getCurrentScene().addObject(self.inventory.weapon_slot_1.bullet_line, self.camera, 100)
				line.position = self.inventory.weapon_slot_1.muzzle.position
				line.orientation = self.bullet_spread.orientation

				flash = bge.logic.getCurrentScene().addObject(self.inventory.weapon_slot_1.flash, self.camera, 100)
				#flash = bge.logic.getCurrentScene().objects['Flass']
				flash.position = self.inventory.weapon_slot_1.muzzle.position
				flash.setParent(self.inventory.weapon_slot_1.muzzle)

				if hit != None:
					new = bge.logic.getCurrentScene().addObject('B_Hole', self.camera, 100)
					new.position = ray.hitPosition
					new.alignAxisToVect(ray.hitNormal, 2, 1.0)
					new.setParent(hit)

					if 'physics' in hit:
						hit['physics'] = 1

					if 'Health' in hit:
						hit['Health'] += -10
						#hit.health += -10
						#ai_base(hit).health += -10
						#print ('BAM!!!' + str(ai_base(hit).health)

					#print (hit.health)
					#print(type(hit))

				#bge.logic.getCurrentScene().objects['LF_User_Cam']["LF_VISIBLE"] = False

		# AIM
		if mouse.events[bge.events.RIGHTMOUSE] == 1:
			pass


	def handle_interactions(self):
		ray = self.camera.controllers[0].sensors['interact_ray']
		hit = ray.hitObject
		keyboard = bge.logic.keyboard

		if keyboard.events[bge.events.BKEY] == 1:
			self.build_tree()

		if hit != None:
			if 'Door' in hit:

				if keyboard.events[bge.events.EKEY] == 1:
					ui.singleton.show_loading('./data/cells/'+ hit['Door'] +'.cell')
					try:
						self.position = bge.logic.getCurrentScene.objects[hit['Start Object']].position
						self.orientation = bge.logic.getCurrentScene.objects[hit['Start Object']].orientation
					except: pass

			if 'Vehicle' in hit:
				if keyboard.events[bge.events.EKEY] == 1:
					hit['Vehicle'] = True
					self.vehicle = hit
					self.position = [self.vehicle.position[0],self.vehicle.position[1],self.vehicle.position[2]+10]


			# Items
			if 'Item' in hit:

				if keyboard.events[bge.events.EKEY] == 1:
				  self.inventory.add_item(hit['Item'])
                  #self.inventory.add_item( Item( 0, 0, '22 mm ammo', description='ammo that goes in the gun', size=1, cost=0, effects={}), amount=56 )
				  print ('added to inventory')
				  print (self.inventory.items)
				  hit.endObject()

			# Weapons
			if 'WeaponC' in hit:
				if keyboard.events[bge.events.EKEY] == 1:
					self.inventory.replace_weapon(hit.parent['Weapon'])
					new = self.inventory.weapon_slot_1.equip()
					#self.inventory.weapon_slot_1.finish(new)
					hit.parent.endObject()

			# pickup
			if 'pick' in hit:
				if keyboard.events[bge.events.TKEY] == 1:
					if self.lev != None:
						self.lev.removeParent()
						self.lev= None

					else:
						hit.position = self.set_loc.position
						hit.setParent(self.set_loc)
						self.lev= hit


			# toggle
			elif 'Toggle' in hit:
				keyboard = bge.logic.keyboard

				if keyboard.events[bge.events.EKEY] == 1:
					if hit['Toogle'] == 1:
						hit['Toogle'] = 0
					elif hit['Toogle'] == 0:
						hit['Toogle'] = 1


	def fast_travel(self, location):
		self.position = location_id.position
		# handle world cells

	def handle_camera(self):
		bge.logic.getCurrentScene().active_camera = self.camera # set active_camera

		mpos = bge.logic.mouse.position

		w = bge.render.getWindowWidth()
		h = bge.render.getWindowHeight()

		w,h = w, h
		w = (w - int(w)%2)/2
		h = (h - int(h)%2)/2

		bge.render.setMousePosition(int(w), int(h))
		#bge.render.setMousePosition(int(w/2), int(h/2))

		if not 'ml_rotx' in self.camera:
			self.camera['ml_rotx'] = -(self.camera.localOrientation.to_euler().x - (math.pi * 0.5))

		else:
			mouse_mx = (mpos[0] - 0.5) * 3#bge.logic.globalDict['game'].control_options[1]#MOUSE_SENSITIVITY # bge.logic.globalDict['game'].control_options[Game.MOUSE_SENSITIVITY]
			mouse_my = (mpos[1] - 0.5) * 3#bge.logic.globalDict['game'].control_options[1]#MOUSE_SENSITIVITY

			cap = 1.5

			if -(self.camera['ml_rotx'] + mouse_my) < cap and -(self.camera['ml_rotx'] + mouse_my) > -cap:
				if abs(mouse_mx) > 0.001 or abs(mouse_my) > 0.001:
					self.camera.parent.applyRotation([0, 0, -mouse_mx], 0) # X
					self.camera.applyRotation([-mouse_my, 0, 0], 1) # Y
					self.camera['ml_rotx'] += mouse_my


	def remove_controls(self):
		self.stored_state = self.movement_state_machine.current_state

	def restore_controls(self):
		self.movement_state_machine.current_state = self.stored_state

	def temp_pos2(self):
		if self.temp_pos == 1:
			#self.position = bge.logic.getCurrentScene().objects['player_location'].position
			self.temp_pos = 2
			#self.handle_lights()

	###
	def main(self):

		if bge.logic.globalDict['pause'] == 0 and self._data:
			EntityBase.main(self)

			self.movement_state_machine.main()
			self.handle_camera()
			self.handle_interactions()

			#self.temp_pos2()

			#if self.current_weapon != None:
			self.handle_weapon()

