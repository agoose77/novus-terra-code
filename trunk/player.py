import math

import bge
from mathutils import Vector, Matrix

from entity_base import EntityBase
from finite_state_machine import FiniteStateMachine
from game import *
from sound_manager import SoundManager
from inventory import Inventory

class Player(EntityBase):

	def __init__(self):
		EntityBase.__init__(self, 'player')

		self.health = 100
		self.hunger = 0.0
		self.tiredness = 0.0 # - Right name? fatigue?
		self.stats = []
		self.items = []

		self.talking = False
		self.is_in_combat = False
		self.stored_state = None
		self.camera_on = True
		self.current_vehicle = None
		self.walking_speed = 5
		self.current_places = []

		self.walk_speed = 3.0
		self.run_speed = 9.0

		self.camera = [child for child in self.children if isinstance(child, bge.types.KX_Camera)][0]

		self.movement_state_machine = FiniteStateMachine(self)
		self.movement_state_machine.add_state('walk', self.handle_walk_state) # add state
		self.movement_state_machine.add_state('climb', self.handle_climb_state)
		#self.movement_state_machine.add_state('jump', self.handle_jump_state)
		self.movement_state_machine.add_state('fall', self.handle_fall_state)
		#self.movement_state_machine.add_state('land', self.handle_land_state2)
		self.movement_state_machine.add_state('vehicle', self.handle_vehicle_state)
		self.movement_state_machine.add_state('none', self.handle_none_state)

		self.movement_state_machine.add_transition('fall', 'walk', self.is_grounded)
		#self.movement_state_machine.add_transition('walk', 'fall', self.is_falling)
		self.inventory= Inventory()


	def handle_walk_state(self, FSM):
		keyboard = bge.logic.keyboard

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

	def handle_climb_state(self, FSM):
		pass

	def handle_fall_state(self, FSM):
		pass#print ('fall')

	def handle_vehicle_state(self, FSM):
		pass

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


	def has_entered_ladder(self, FSM):
		pass

	def has_exited_ladder(self, FSM):
		pass

	def has_entered_vehicle(self, FSM):
		pass

	def has_exited_vehicle(self, FSM):
		pass

	def has_pressed_jumpkey(self, FSM):
		pass

	def has_entered_none(self, FSM):
		pass

	def has_exited_none(self, FSM):
		pass


	###
	def handle_interactions(self):
		# cast ray from mouse into world, check if hasattr(hit_obj, 'on_interact')
		ray = self.camera.controllers[0].sensors['Ray']

		hit = ray.hitObject

		#if isinstance(ray, item):
		#   pass

		if hit != None:
			if 'Item' in hit:

                # Item
				if hit['Item'] == 'ITEM':
					print (hit['Item'].name)

					keyboard = bge.logic.keyboard

					if keyboard.events[bge.events.EKEY] == 1:
					  self.inventory.add_item(hit['Item'].id)
					  print ('added to inventory')
					  print (self.inventory.items)
					  hit.endObject() # replace with your enitybase one



	def fast_travel(self, location):
		self.position = location_id.position
		# handle world cells

	def handle_camera(self):
		from game import Game
		bge.logic.getCurrentScene().active_camera = self.camera # set active_camera

		mpos = bge.logic.mouse.position

		w = bge.render.getWindowWidth()
		h = bge.render.getWindowHeight()

		bge.render.setMousePosition(w//2, h//2)

		if not 'ml_rotx' in self.camera:
			self.camera['ml_rotx'] = -(self.camera.localOrientation.to_euler().x - (math.pi * 0.5))
		else:
			mouse_mx = (mpos[0] - 0.5) * bge.logic.globalDict['game'].control_options[Game.MOUSE_SENSITIVITY]#MOUSE_SENSITIVITY # bge.logic.globalDict['game'].control_options[Game.MOUSE_SENSITIVITY]
			mouse_my = (mpos[1] - 0.5) * bge.logic.globalDict['game'].control_options[Game.MOUSE_SENSITIVITY]#MOUSE_SENSITIVITY

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

	###
	def main(self):
		EntityBase.main(self)
		self.movement_state_machine.main()
		self.handle_camera()
		self.handle_interactions()

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