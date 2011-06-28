import math

import bge
from mathutils import Vector

from entity_base import EntityBase
from finite_state_machine import FiniteStateMachine
from game import *
from sound_manager import SoundManager

class Player(EntityBase):

	def __init__(self):
		EntityBase.__init__(self, 'Cube')
		
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
		self.run_speed = 5.0
		#self.camera = [child for child in self.children if isinstance(child, bge.types.KX_Camera)][0]
		
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


	def handle_walk_state(self, FSM):
		#print ('walk')
		###
		keyboard = bge.logic.keyboard.events
		vel = self.getLinearVelocity()
		move = [0,0,0]

		#controls = bge.logic.globalDict['game'].control_options

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
		ray = self.rayCast(pos1, self.position, 1, '', 0, 0, 0)

		if ray[0] != None:
			if keyboard[bge.events.SPACEKEY] == bge.logic.KX_INPUT_JUST_ACTIVATED:
				move[2] = 10

		###
		com = vel[2]+move[2]
		t1 = move[1] * self.worldOrientation[2].copy()

		self.localLinearVelocity = [move[1],move[0], com]

		# Handle sound - would be connected to animation data I suppose, which frame the foot is on the ground
		
		""" Alternative movement code, always apply force along slope of the ground
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
			hit_obj, hit_pos, hit_normal = self.rayCast(ray_end, self._data)        ### TEMP - needs fixing (self._data)
			
			# Direction along the xy plane to apply the force  (rotated 90 degrees, for when cross product is taken)
			force_xy = Vector([fx, fy, 0]) * Matrix.Rotation(math.pi/2, 3, [0, 0, 1])
			
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
		"""    

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
		pass

	def fast_travel(self, location):
		self.position = location_id.position
		# handle world cells

	def handle_camera(self):
		bge.logic.getCurrentScene().active_camera = self.camera # set active_camera

		mpos = bge.logic.mouse.position

		w = bge.render.getWindowWidth()
		h = bge.render.getWindowHeight()

		bge.render.setMousePosition(w//2, h//2)

		if not 'ml_rotx' in self.camera:
			self.camera['ml_rotx'] = -(self.camera.localOrientation.to_euler().x - (math.pi * 0.5))
		else:
			mouse_mx = (mpos[0] - 0.5) * Game.MOUSE_SENSITIVITY # bge.logic.globalDict['game'].control_options[Game.MOUSE_SENSITIVITY]
			mouse_my = (mpos[1] - 0.5) * Game.MOUSE_SENSITIVITY

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
		#self.handle_camera()

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