import bge as bge
from entity_base import EntityBase
from finite_state_machine import FiniteStateMachine
import math
from game import Game
from sound_manager import SoundManager

class Player(EntityBase):

	def __init__(self):
		EntityBase.__init__(self, 'Cube')
		self.health = 100
		self.stats = []
		self.talking = False
		self.walking_speed = 5
		self.items = []
		self.is_in_combat = False
		self.hunger = 0.0
		self.tiredness = 0.0 # - Right name?
		self.is_talking = False
		self.current_vehicle = False
		self.current_places = []
		self.stored_state = None
		self.camera_on = True
		self.walk_speed = 3
		self.run_speed = 5
		self.camera = self.children[0]
		self.movement_state_machine = FiniteStateMachine(self)
		self.movement_state_machine.add_state('walk', self.handle_walk_state) # add state
		self.movement_state_machine.add_state('climb', self.handle_climb_state)
		#self.movement_state_machine.add_state('jump', self.handle_jump_state)
		self.movement_state_machine.add_state('fall', self.handle_fall_state)
		#self.movement_state_machine.add_state('land', self.handle_land_state)
		self.movement_state_machine.add_state('vehicle', self.handle_vehicle_state)
		self.movement_state_machine.add_state('none', self.handle_none_state)


	def handle_walk_state(self, FSM):
		print ('WAlk')
		###
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
		ray = self.rayCast(pos1, self.position, 1, '', 0, 0, 0)

		if ray[0] != None:
			if keyboard[bge.events.SPACEKEY] == 1:
				move[2] = 10

		###
		from mathutils import Vector
		com = vel[2]+move[2]
		t1 = move[1] * self.worldOrientation[2].copy()

		self.worldLinearVelocity = [move[1],move[0], com]

		# Handle sound


	def handle_climb_state(self, FSM):
		pass

	def handle_fall_state(self, FSM):
		print ('fall')

	def handle_vehicle_state(self, FSM):
		pass

	def handle_none_state(self, FSM):
		pass



	def is_grounded(self, FSM):
		pos2 = [self.position[0],self.position[1],self.position[2]-5]
		ray2 = self.rayCast(pos2, self.position, 0, '', 0, 0, 0)

		if ray2[0] == None:
			grounded = False

		else:
			grounded = True

		return grounded

	def is_falling(self, FSM):
		pos2 = [self.position[0],self.position[1],self.position[2]-5]
		ray2 = self.rayCast(pos2, self.position, 0, '', 0, 0, 0)

		if ray2[0] == None:
			falling = True

		else:
			falling = False

		return falling

	def has_entered_ladder(self, FSM):
		pass

	def has_exited_ladder(self, FSM):
		pass

	def has_entered_vehicle(self, FSM):
		pass

	def has_exited_vehicle(self, FSM):
		pass

	#def has_pressed_jumpkey(self, FSM):
	#	pass

	def has_entered_none(self, FSM):
		pass

	def has_exited_none(self, FSM):
		pass


	###
	def handle_interactions(self):
		pass

	def fast_travel(self, location):
		self.position = location_id.position
		# handle world cells

	def handle_camera(self):
		bge.logic.getCurrentScene().active_camera = self.camera # set active_camera

		mpos = bge.logic.mouse.position

		w = bge.render.getWindowWidth()
		h = bge.render.getWindowHeight()

		bge.render.setMousePosition(int(w/ 2), int(h/ 2))


		if not 'ml_rotx' in self.camera:
			self.camera['ml_rotx'] = -(self.camera.localOrientation.to_euler().x - (math.pi * 0.5))

		else:
			mouse_mx = (mpos[0] - 0.5) * Game.MOUSE_SENSITIVITY
			mouse_my = (mpos[1] - 0.5) * Game.MOUSE_SENSITIVITY

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

		if self.movement_state_machine.current_state == 'walk':
			self.movement_state_machine.add_transition('walk', 'fall', self.is_falling, self.handle_fall_state)
		else:
			self.movement_state_machine.add_transition('fall', 'walk', self.is_grounded, self.handle_walk_state)



### Testing
own = bge.logic.getCurrentController().owner

# Creat Entity
if not 'INIT' in own:
	bge.logic.globalDict['game'] = Player()
	own['INIT'] = ''

# If created already
else:
	Player.main(bge.logic.globalDict['game'])