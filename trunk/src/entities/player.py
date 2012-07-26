from mathutils import *
from bge import render as R
import math
import sys
sys.path.append('./src/')
sys.path.append('./src/weapons/')
sys.path.append('./src/entities/')

import bge
import mathutils

import entities
import game
import sudo
from inventory import Inventory
from finite_state_machine import FiniteStateMachine


###
class Player(entities.Actor):

	def __init__(self):
		print("player.__init__()")

		super().__init__()

		# Player Stats
		self.health = 100
		self.faction = 1		 # Default Faction = Humans
		#self.name = 'player'

		self.hunger = 0.0
		self.fatigue = 0.0
		self.alert = 0
		self.last_shot = 0.0
		self.reloading = False
		self.reload_start_time = 0.0
		self.roll = 0.0

		self.walk_speed = 5.0
		self.run_speed = 45.0
		self.walk_temp = 0.0
		self.last_move = 0.0
		self.jump_speed = 10.0

		# Stops mouse events from triggering for a frame
		# Used for when a UI screen is exited
		self.hold_mouse_update = False

		self.init_1 = False
		self.animations = {
			'walk': 0,
			'run': 0,
			'shoot': 0,
			'reload': 0,
			'idle': 1,
			'cround': 0
			}

		self.bullets_auto = 10
		self.bullets_shotgun = 10
		self.bullets_pistol = 10

		# Smooth Camera
		self.oldX = None

		#
		self.impants = []
		self.stats = {'temp': 'temp'}

		#
		self.current_weapon = None  # TODO - outdated reference, has this been moved to inventory?
		self.current_animations = {
			'walk': None,
			'run': None,
			'reload': None,
			'attack': None,
			'switch': None,
			'aim': None,
		}

		self.talking = False
		self.is_in_combat = False
		self.stored_state = None
		self.camera_on = True

		# Inventory
		self.inventory = Inventory()
		self.inventory.id = 'Player'

		# adding some items for testing: # TODO - remove
		self.inventory.add_item('cube', item_amount=9)
		self.inventory.add_item('wrench', item_amount=9)
		self.inventory.add_item('p90')

		# calculating this once for mouse move
		w = bge.render.getWindowWidth()
		h = bge.render.getWindowHeight()
		self.window_middle = [int((w - int(w) % 2) / 2),
							int((h - int(h) % 2) / 2)]

	def _wrap(self, object):
		entities.EntityBase._wrap(self, object)

		# Vehicle
		self.current_vehicle = None
		self.in_vehicle = False

		self.camera = [child for child in self.children if 'camera_temp' in child][0]
		self.lens = self.camera.lens

		self.armature = [child for child in self.childrenRecursive if 'Armature' in child][0]
		self.bullet_spread = [child for child in self.childrenRecursive if 'spread' in child][0]
		self.weapon_pos = [child for child in self.childrenRecursive if 'weapon_pos' in child][0]
		self.climb_ray =[child for child in self.childrenRecursive if 'climb_ray' in child][0] 
		self.c_r_t = [child for child in self.childrenRecursive if 'c_r_t' in child][0] 
		self.c_r_b = [child for child in self.childrenRecursive if 'c_r_b' in child][0] 

		self.c_r_top = [child for child in self.childrenRecursive if 'c_r_top' in child][0] 

		# FSM States
		self.movement_state_machine = FiniteStateMachine(self)
		self.movement_state_machine.add_state('walk', self.handle_walk_state)
		self.movement_state_machine.add_state('fall', self.handle_fall_state)
		self.movement_state_machine.add_state('vehicle', self.handle_vehicle_state)
		self.movement_state_machine.add_state('none', self.handle_none_state)

		# FSM Transitions
		self.movement_state_machine.add_transition('fall', 'walk', self.is_grounded)
		self.movement_state_machine.add_transition('walk', 'vehicle', self.is_in_vehicle)

		# HACKS
		self.temp_pos = 1
		self.set_loc = [child for child in self.childrenRecursive if 'set_loc' in child][0]
		self.lev = None

		# WEAPON STARTING
		self.inventory.replace_weapon("F2000")
		self.inventory.primary_weapon.equip(self)

	def _unwrap(self):
		entities.EntityBase._unwrap(self)

	def damage(self, amount, object=None):
		self.health += amount
		print("HURT")

	def is_in_vehicle(self, FSM):
		return bool(self.in_vehicle)

	def handle_walk_state(self, FSM):
		keyboard = bge.logic.keyboard.events
		vel = self.getLinearVelocity()
		move = [0, 0, 0]

		#bottom_ray = self._data.rayCast(self.c_r_top, self.c_r_b)
		#top_ray = self._data.rayCast(self.climb_ray, self.c_r_t)

		#if (bottom_ray[0] != None) and (top_ray[0] == None):
			#self.localLinearVelocity = Vector([0.0,2.5,0.0])
			#self.localLinearVelocity[2] += (2.0-self.getDistanceTo(bottom_ray[1])) * 0.75
		#	self.last_move = (2.0-self.getDistanceTo(bottom_ray[1])) * 2.0
		#else:
			#self.localLinearVelocity = Vector([0.0,0.0,0.0])
			#self.localLinearVelocity[2] = self.last_move*0.2
		#	self.last_move = self.last_move*0.75

		
		#print ("--", top_ray)
		#print ("Bottom",bottom_ray)
		#print ("==", move[2])

		### Keys
		if keyboard[bge.events.LEFTSHIFTKEY]:  # and self.fatigue < 10:
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
			pos1 = [self.position[0], self.position[1], self.position[2] - 10]
			ray = self.rayCast(pos1, self.position, 2, '', 0, 0, 0)

			if ray[0] != None:
				move[2] = self.jump_speed
				self.walk_temp = 19

		###
		com = vel[2] + move[2]
		self.localLinearVelocity = Vector([move[1], move[0], com])

		###
		if move[0] != 0 or move[1] != 0:

			if speed == self.walk_speed:
				self.roll += 0.5
				self.camera.applyRotation([0, math.sin(self.roll*0.5)*0.002, math.sin(self.roll*0.5)*0.003], 1)  # Y
				self.camera.localPosition[2] += math.sin(self.roll)*0.03
				self.play_animation('walk')
				self.walk_temp += 1

			elif speed == self.run_speed:
				self.roll += 0.75
				self.camera.applyRotation([math.sin(self.roll)*0.004, 0, 0], 1)  # Y
				self.play_animation('run')
				self.walk_temp += 2
		else:
			self.play_animation('idle')
			#pass


		if self.walk_temp > 20:
			self.walk_temp = 0
			print("Play Sound")
			#session.game.sound_manager.play_sound('walk_grass_1.ogg', self)

	def update_path_follow(self):
		""" """
		super().update_path_follow()
		self.play_animation('walk')

	### ANIMATIONS ###
	def play_animation(self, name):
		self.animations[name] = 1

	def stop_animation(self, layer):
		for n in range(0, 7):
			if n != layer:
				self.armature.stopAction(n)

	def handle_animations(self):
		weapon = self.inventory.primary_weapon

		if self.animations['reload'] == 1:
			self.armature.playAction(str(weapon.name) + "_reload", 1, 200, layer=4, priority=2, blendin=5, play_mode=bge.logic.KX_ACTION_MODE_PLAY, speed=1.0)
			self.stop_animation(4)

		elif self.animations['shoot'] == 1:
			self.armature.playAction(str(weapon.name) + "_shoot", 1, 5, layer=3, priority=3, blendin=5, play_mode=bge.logic.KX_ACTION_MODE_PLAY, speed=1.0)
			self.stop_animation(3)

		elif self.animations['walk'] == 1:
			self.armature.playAction(str(weapon.name) + "_walk", 1, 21, layer=2, priority=2, blendin=5, play_mode=bge.logic.KX_ACTION_MODE_LOOP, speed=1.0)
			self.stop_animation(2)

		elif self.animations['run'] == 1:
			self.armature.playAction(str(weapon.name) + "_run", 1, 17, layer=1, priority=3, blendin=5, play_mode=bge.logic.KX_ACTION_MODE_LOOP, speed=1.0)
			self.stop_animation(1)

		else:
			self.stop_animation(0)
			self.armature.playAction(str(weapon.name) + "_idle", 1, 101, layer=0, priority=5, blendin=5, play_mode=bge.logic.KX_ACTION_MODE_LOOP, speed=1.0)

		for name in self.animations:
			self.animations[name] = 0

	def handle_fall_state(self, FSM):
		pass

	def handle_vehicle_state(self, FSM):
		keyboard = bge.logic.keyboard

		bge.logic.getCurrentScene().active_camera = self.current_vehicle.camera

		# HACK
		self.camera_on = False  # Turn off player camera
		self.position = [self.current_vehicle.position[0],
						self.current_vehicle.position[1],
						self.current_vehicle.position[2] + 10]

		# Get out of vehicle
		if keyboard.events[bge.events.EKEY] == 1:
			self.camera_on = True
			self.position = [self.current_vehicle.position[0],
							self.current_vehicle.position[1],
							self.current_vehicle.position[2] + 10]  # add player above the vehicle

			self.current_vehicle.vehicle_on = False
			self.in_vehicle = False
			self.movement_state_machine.current_state = 'walk'
			self.current_vehicle.FSM.current_state = 'off'
			self.current_vehicle = None

	def is_grounded(self, FSM):
		pos2 = [self.position[0], self.position[1], self.position[2] - 5]
		ray2 = self.rayCast(pos2, self._data, 0, '', 0, 0, 0)
		return bool(ray2[0])

	def is_falling(self, FSM):
		pos2 = [self.position[0], self.position[1], self.position[2] - 5]
		ray2 = self.rayCast(pos2, self._data, 0, '', 0, 0, 0)
		return not bool(ray2[0])

	def has_entered_vehicle(self, FSM):
		return bool(self.vehicle)

	def has_exited_vehicle(self, FSM):
		return bool(self.vehicle)

	def handle_none_state(self, FSM):
		pass

	"""def reload(self):
		print("Reloading...")


		if self.inventory.ammo['Assault'] > 0:
			if self.reload_start_time == 0.0:
				self.reload_start_time = sudo.game.game_time
				self.entity.play_animation('reload')
				self.reloading = True

			elif self.reload_start_time + self.reload_time < sudo.game.game_time:
				self.reload_start_time = 0.0
				self.in_clip = self.clip_size
				self.reloading = False

				if self.inventory.ammo['Assault'] < self.inventory.weapon_slot_1.clip_size:
					self.inventory.weapon_slot_1.clip = self.inventory.ammo['Assault']
					self.inventory.ammo['Assault'] = 0
				else:
					self.inventory.weapon_slot_1.clip = self.inventory.weapon_slot_1.clip_size
					self.inventory.ammo['Assault'] += -self.inventory.weapon_slot_1.clip_size

				self.reload_start_time = 0.0

			else:
				self.play_animation('reload')
		else:
			print("Out Of Ammo!!")
			"""

	def handle_weapon(self):
		if self.hold_mouse_update != 0:
			# Don't fire the gun after exiting a screen
			return

		weapon = self.inventory.primary_weapon  # TODO - add secondary weapon

		if weapon is not None:
			weapon.main()

	def handle_interactions(self):
		ray = self.camera.controllers[0].sensors['interact_ray']
		hit = ray.hitObject
		keyboard = bge.logic.keyboard

		if hit != None and 'entity_base' in hit:
			sudo.ui_manager.screens['hud'].set_interact_text(hit['entity_base'].interact_label, hit['entity_base'].interact_icon)
			if type(hit['entity_base']) is str:
				temp = __import__("weapon_pickup")
				temp = temp.WeaponPickup(hit, hit['info'], hit['name'])  # ex hack
				hit['entity_base'] = temp
			else:
				if keyboard.events[bge.events.EKEY] == 1:
					hit['entity_base'].on_interact(self)
		else:
			sudo.ui_manager.screens['hud'].set_interact_text('')
			pass

	def fast_travel(self, location):
		self.position = location_id.position
		# handle world cells

	def handle_camera(self):
		bge.logic.getCurrentScene().active_camera = self.camera  # set active_camera

		"""
		w = R.getWindowWidth()//2
		h = R.getWindowHeight()//2
		screen_center = (w, h)

		Mouse = bge.logic.mouse
		speed = 0.08				# walk speed
		sensitivity = 0.002		# mouse sensitivity
		smooth = 0.7			# mouse smoothing (0.0 - 0.99)

		if self.oldX == None:

			R.setMousePosition(w + 1, h + 1)
			
			self.oldX = 0.0
			self.oldY = 0.0

		else:
			
			scrc = Vector(screen_center)
			mpos = Vector(Mouse.position)
			
			x = scrc.x-mpos.x
			y = scrc.y-mpos.y

			# Smooth movement
			self.oldX = (self.oldX*smooth + x*(1.0-smooth))
			self.oldY = (self.oldY*smooth + y*(1.0-smooth))
			
			x = self.oldX* sensitivity
			y = self.oldY* sensitivity
			 
			# set the values
			self.applyRotation([0, 0, x], False)
			self.applyRotation([y, 0, 0], False)
			
			# Center mouse in game window
			R.setMousePosition(*screen_center)
			

		"""
		smooth = 0.5
		sensitivity = 1.5
		mpos = bge.logic.mouse.position[:]
		mouse = bge.logic.mouse

		if self.oldX == None:
			self.oldX = [0.0,0.0]

		if self.hold_mouse_update != 0:
			self.hold_mouse_update -= 1
			mpos = [0.5, 0.5]

		if mouse.events[bge.events.RIGHTMOUSE]:
			#self.camera.lens = self.inventory.primary_weapon.zoom_lens
			self.camera.lens += (self.inventory.primary_weapon.zoom_lens - self.camera.lens)*0.1
			bge.logic.getCurrentScene().objects['FX']['autofocus'] = True
		else:
			bge.logic.getCurrentScene().objects['FX']['autofocus'] = False
			self.camera.lens = self.lens

		bge.render.setMousePosition(self.window_middle[0], self.window_middle[1])

		if not 'ml_rotx' in self.camera:
			self.camera['ml_rotx'] = -(self.camera.localOrientation.to_euler().x - (math.pi * 0.5))

		else:
			#mouse_mx = (self.oldX[0]*smooth)+((mpos[0] - 0.5) * 3)*(1.0-smooth)#bge.logic.globalDict['game'].control_options[1]#MOUSE_SENSITIVITY # bge.logic.globalDict['game'].control_options[Game.MOUSE_SENSITIVITY]
			#mouse_my = (self.oldX[1]*smooth)+((mpos[1] - 0.5) * 3)*(1.0-smooth)#bge.logic.globalDict['game'].control_options[1]#MOUSE_SENSITIVITY
			self.oldX[0] = (self.oldX[0]*smooth)+((mpos[0] - 0.5) * 3)*(1.0-smooth)
			self.oldX[1] = (self.oldX[1]*smooth)+((mpos[1] - 0.5) * 3)*(1.0-smooth)

			mouse_mx = self.oldX[0]* sensitivity
			mouse_my = self.oldX[1]* sensitivity

			cap = 1.5

			if -(self.camera['ml_rotx'] + mouse_my) < cap and -(self.camera['ml_rotx'] + mouse_my) > -cap:
				if abs(mouse_mx) > 0.0025 or abs(mouse_my) > 0.0025:
					self.camera.parent.applyRotation([0, 0, -mouse_mx], 0)  # X
					self.camera.applyRotation([-mouse_my, 0, 0], 1)  # Y
					self.camera['ml_rotx'] += mouse_my


	def remove_controls(self):
		self.stored_state = self.movement_state_machine.current_state

	def restore_controls(self):
		self.movement_state_machine.current_state = self.stored_state

	###
	def update(self):
		if bge.logic.globalDict['pause'] == 0 and self._data:
			if not self.frozen:
				self.movement_state_machine.main()
			#self.handle_animations()

				if self.in_vehicle == False:
					self.handle_camera()
					self.handle_interactions()

					if self.inventory.primary_weapon is not None:
						self.handle_animations()
						self.handle_weapon()

					#if self.reloading == True:
					#	self.reload()
