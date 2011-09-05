import sys
sys.path.append('./src/')
sys.path.append('./src/owyl/')
#import pyglet
import math

import bge
from mathutils import Vector, Matrix

from entity_base import EntityBase
from finite_state_machine import FiniteStateMachine
from behavior_tree import BehaviorTree

#from game import Game
#from game import *
from item import Item
from sound_manager import SoundManager
from Inventory import Inventory

import ui


###
import owyl
from owyl import blackboard

###
class Player(EntityBase):

	def __init__(self):
		print("player.__init__()")
		EntityBase.__init__(self, 'player')

		# Player Stats
		self.health = 100
		self.faction = 1 		# Default Faction = Humans
		self.hunger = 0.0
		self.fatigue = 0.0
		self.walk_speed = 8.0
		self.run_speed = 15.0

		self.bb = blackboard
	#	self.tree = self.build_tree()

		self.impants = []
		self.stats = {'temp':'temp'}

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

		# Vehicle
		self.current_vehicle = None
		self.vehicle= None

		self.camera = [child for child in self.children if isinstance(child, bge.types.KX_Camera)][0]
		self.armature = [child for child in self.childrenRecursive if 'Armature' in child][0]

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

		# BF
		#self.b_tree = BehaviorTree(self)
		#self.b_tree.add_condition('Hungry', self.if_hungry)
		#self.b_tree.add_action('Hungry', self.test123)

		# Inventory
		self.inventory = Inventory()
		self.sounds = SoundManager()

		# HACKS
		self.temp_pos = 1
		self.set_loc = [child for child in self.childrenRecursive if 'set_loc' in child][0]
		self.lev = None


	### ### ###
	def if_hungry(self):
		return True

	# Animations
	def handle_animations(self):
		pass

	def test123(self):
		print ('TESTSETISEJTISDNFIDIFSDHf')



	# Update Animations when current weapon changes
	def update_animations(self):
		self.current_animations['idle'] = self.current_weapon['name']+' idle'
		self.current_animations['walk'] = self.current_weapon['name']+' walk'
		self.current_animations['run'] = self.current_weapon['name']+' run'
		self.current_animations['reload'] = self.current_weapon['name']+' reload'
		self.current_animations['attack'] = self.current_weapon['name']+' attack'
		self.current_animations['switch'] = self.current_weapon['name']+' switch'
		self.current_animations['aim'] = self.current_weapon['name']+' aim'
		#self.current_animations[''] = self.current_weapon['name']+' '


	def equip_weapon(self,id):
		print (self.inventory.items)
		self.current_weapon = Item.items[id]
		name = self.current_weapon.name

		new = bge.logic.getCurrentScene().addObject(name,'weapon_location')
		new.position = bge.logic.getCurrentScene().objects['weapon_location'].position
		new.orientation =bge.logic.getCurrentScene().objects['weapon_location'].orientation
		new.setParent(bge.logic.getCurrentScene().objects['weapon_location'])

		# Update Animations

		# Finished
		print ('Equiped')


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
				move[2] = 10

		###
		com = vel[2]+move[2]
		self.localLinearVelocity = [move[1],move[0], com]

		''' - a101 movement code - get errors
		fx = 0.0
		fy = 0.0

		if keyboard.events[bge.events.WKEY] == bge.logic.KX_INPUT_ACTIVE:
			fy += 1.0
		if keyboard.events[bge.events.SKEY] == bge.logic.KX_INPUT_ACTIVE:
			fy -= 1.0
		if keyboard.events[bge.events.AKEY] == bge.logic.KX_INPUT_ACTIVE:
			fx -= 1.0
		if keyboard.events[bge.events.DKEY] == bge.logic.KX_INPUT_ACTIVE:
			fx += 1.0

		if keyboard.events[bge.events.TKEY] == 1:
			self.equip_weapon(8)

		if fx or fy:
			ray_end = self.worldPosition.copy()
			ray_end.z -= 2.0
			hit_obj, hit_pos, hit_normal = self.rayCast(ray_end, self._data)		### TEMP - needs fixing (self._data)

			# Direction along the xy plane to apply the force  (rotated 90 degrees, for when cross product is taken)
			force_xy = Vector([fx, fy, 0]) * Matrix.Rotation(-math.pi/2, 3, [0, 0, 1])

			# Direction to apply force, taking into account slope of ground plane
			force_xyz = 100 * hit_normal.cross(force_xy).normalized()

			self.applyForce(force_xyz, True)

			# limit velocity
			if keyboard.events[bge.events.LEFTSHIFTKEY] == bge.logic.KX_INPUT_ACTIVE:
				vel_limit = self.run_speed
			else:
				vel_limit = self.walk_speed

			vel = self.worldLinearVelocity
			if vel.magnitude > vel_limit:
				vel.magnitude = vel_limit
				self.worldLinearVelocity = vel

			# Animations
			self.handle_animations()
			'''
	def handle_fall_state(self, FSM):
		pass

	def handle_vehicle_state(self, FSM):
		keyboard = bge.logic.keyboard

		bge.logic.getCurrentScene().active_camera = self.vehicle['Camera']


		# HACK
		self.camera_on = False # Turn off player camera
		self.position = [self.vehicle.position[0],self.vehicle.position[1],self.vehicle.position[2]+10]
		#self.visible

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
		#temp = False
		#if self.vehicle != None:
		#	print ('test!')
		#	temp = True
		return bool(self.vehicle)#temp

	def has_exited_vehicle(self, FSM):
		#temp = False
		#self.want_exit_vehicle= False
		#if self.vehicle == None:
		#	print ('test!')
		#	temp = True
		return bool(self.vehicle)#temp

	def has_pressed_jumpkey(self, FSM):
		pass

	def has_entered_none(self, FSM):
		pass

	def has_exited_none(self, FSM):
		pass

	def handle_weapon(self):
		ray = self.camera.controllers[0].sensors['weapon_ray']
		ray.range = 200#self.current_weapon.range

		hit = ray.hitObject
		mouse = bge.logic.mouse
		keyboard = bge.logic.keyboard

		# Reload
		if keyboard.events[bge.events.RKEY] == 1:
			pass

		# SHOOT
		if mouse.events[bge.events.LEFTMOUSE] == 1:
			self.sounds.play_sound('shoot_temp.ogg')
			if hit != None:

				# Impact Effects
				new = bge.logic.getCurrentScene().addObject('B_Hole', bge.logic.getCurrentController().owner, 100)
				new.position = ray.hitPosition
				new.alignAxisToVect(ray.hitNormal, 2, 1.0)
				new.setParent(hit)
				#print ('HITTED')
				#print (hit)
				if 'physics' in hit:
					hit['physics'] = 1
					#print ('SEt true')

		# AIM
		if mouse.events[bge.events.RIGHTMOUSE] == 1:
			pass


	def handle_interactions(self):
  	# cast ray from mouse into world, check if hasattr(hit_obj, 'on_interact')
		ray = self.camera.controllers[0].sensors['interact_ray']
		hit = ray.hitObject
		keyboard = bge.logic.keyboard

		if keyboard.events[bge.events.BKEY] == 1:
			self.build_tree()

		if hit != None:
			if 'Door' in hit:
				print (hit['Door'])
				if keyboard.events[bge.events.EKEY] == 1:
					ui.singleton.show_loading('./data/cells/'+ hit['Door'] +'.cell')
					self.position = bge.logic.getCurrentScene.objects[hit['Start Object']].position
					self.orientation = bge.logic.getCurrentScene.objects[hit['Start Object']].orientation

			if 'Vehicle' in hit:
				if keyboard.events[bge.events.EKEY] == 1:
					hit['Vehicle'] = True
					self.vehicle = hit
					self.position = [self.vehicle.position[0],self.vehicle.position[1],self.vehicle.position[2]+10]


			# Items
			if 'Item' in hit:
				print ('Tiem')
				print (hit['Item'].name)

				if keyboard.events[bge.events.EKEY] == 1:
				  self.inventory.add_item(hit['Item'].id)
				  print ('added to inventory')
				  print (self.inventory.items)
				  hit.endObject()

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


			# Small peice of code that can add a bunch of easy features
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

		w,h = int(w), int(h)
		w = (w - w%2)/2
		h = (h - h%2)/2

		bge.render.setMousePosition(int(w), int(h))

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
			self.position = bge.logic.getCurrentScene().objects['player_location'].position
			self.temp_pos = 2
			#self.handle_lights()

	###
	def main(self):
		EntityBase.main(self)
		self.movement_state_machine.main()
		#self.b_tree.main()

		if self.camera_on == True:
			self.handle_camera()

		self.handle_interactions()
		self.temp_pos2()

		#self.sounds.play_sound('walk_grass.ogg', wait=True)

		#if self.current_weapon != None:
		self.handle_weapon()
		self.sounds.main()

"""
### Testing
own = bge.logic.getCurrentController().owner

# Creat Entity
if not 'INIT' in own:
	bge.logic.globalDict['game'] = Player()
	own['INIT'] = ''

# If created already
else:
	Player.main(bge.logic.globalDict['game'])"""


