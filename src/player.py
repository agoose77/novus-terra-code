import sys
sys.path.append('./src/')
sys.path.append('./src/owyl/')
#import pyglet
import math

import aud
from paths import PATH_SOUNDS, PATH_MUSIC

import bge
from mathutils import Vector, Matrix

from entity_base import EntityBase
from finite_state_machine import FiniteStateMachine
from behavior_tree import BehaviorTree

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
		self.walk_speed = 8.0
		self.run_speed = 15.0
		self.walk_temp = 0.0
		self.init_1 = False
		self.animations= []

		#
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



		# Sound manager?
		#self.sound= SoundManager()

		# Dialogue
		#self.dialogue = DialogueSystem([cont.owner.get('ds_width', bge.render.getWindowWidth()-100),cont.owner.get('ds_height', 250)], theme)

		#self.dialogue = DialogueSystem(	[bge.render.getWindowWidth(), 250], theme='Frame')

		# HACKS
		self.temp_pos = 1
		self.set_loc = [child for child in self.childrenRecursive if 'set_loc' in child][0]
		self.lev = None

	def _unwrap(self):
		EntityBase._unwrap(self)

	# Animations
	def handle_animations(self):
		pass

	# Update Animations when current weapon changes
	def update_animations(self, name, do):
		#self.current_weapon.animations['idle'] = self.current_weapon['name']+' idle'
		#self.current_weapon.animations['walk'] = self.current_weapon['name']+' walk'
		#self.current_weapon.animations['run'] = self.inventory.current_weapon.name['name']+' run'
		#self.current_weapon.animations['reload'] = self.inventory.current_weapon['name']+' reload'
		#self.current_weapon.animations['attack'] = self.inventory.current_weapon['name']+' attack'
		#self.current_weapon.animations['switch'] = self.inventory.current_weapon['name']+' switch'
		#self.current_weapon.animations['aim'] = self.inventory.current_weapon['name']+' aim'
		#self.current_animations[''] = self.current_weapon['name']+' '

		if do == 'check':
			if name in self.animations:
				return True
			else:
				self.animations.append(name)
				return False
		elif do == 'remove':
			try:
				self.animations.remove(name)
			except:
				pass

	def equip_weapon(self):
		weapon = self.inventory.current_weapon#self.current_weapon.name
		name = weapon.name

		new = bge.logic.getCurrentScene().addObject(name,'weapon_position')
		new.position = bge.logic.getCurrentScene().objects['weapon_position'].position
		new.orientation =bge.logic.getCurrentScene().objects['weapon_position'].orientation
		new.setParent(bge.logic.getCurrentScene().objects['weapon_position'])

		# Update Animations
		#self.update_animations()

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
				move[2] = 5

		###
		com = vel[2]+move[2]
		self.localLinearVelocity = [move[1],move[0], com]

		###
		if move[0] + move[1] != 0:
			print("Walking")
			self.armature.playAction("P90_walk", 1, 32, layer=5, priority=2, blendin=5, play_mode=bge.logic.KX_ACTION_MODE_LOOP, speed=1.0)
			self.armature.stopAction(4)

		else:
			print("IDLE")
			self.armature.playAction("P90_idle", 1, 64, layer=4, priority=1, blendin=5, play_mode=bge.logic.KX_ACTION_MODE_LOOP, speed=1.0)
			self.armature.stopAction(5)


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
		return bool(self.vehicle)

	def has_exited_vehicle(self, FSM):
		return bool(self.vehicle)

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
			#self.sound.play_sound('shoot_temp.ogg', self)
			#sound = aud.Factory(PATH_SOUNDS+'shoot_temp.ogg')
			#handle = aud.device().play(sound)
			#Game.sound_manager.play_sound('shoot_temp.ogg', self)
			bge.logic.globalDict['game'].sound_manager.play_sound('shoot_temp.ogg', self)


			if hit != None:

				# Impact Effects
				new = bge.logic.getCurrentScene().addObject('B_Hole', bge.logic.getCurrentController().owner, 100)
				new.position = ray.hitPosition
				new.alignAxisToVect(ray.hitNormal, 2, 1.0)
				new.setParent(hit)

				if 'physics' in hit:
					hit['physics'] = 1

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
				  self.equip_weapon()
                  #self.inventory.add_item( Item( 0, 0, '22 mm ammo', description='ammo that goes in the gun', size=1, cost=0, effects={}), amount=56 )
				  #print ('added to inventory')
				  #print (self.inventory.items)
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
			#self.b_tree.main()

		#if self.init_1 == 0:
			#bge.logic.globalDict['game'].world.entity_list.append(self)
		#	session.game.world.entity_list.append(self)
		#	self.init_1 = 1

		#if self.camera_on == True:
			self.handle_camera()

			#if self.camera_on == True:
			#	self.handle_camera()

			self.handle_interactions()
			self.temp_pos2()

			#if self.current_weapon != None:
			self.handle_weapon()
			#self.sound.main()

			# handle dialogue
			#self.dialogue.main()

