import bge as bge
from entity_base import EntityBase
from finite_state_machine import FiniteStateMachine

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
		self.movement_state_machine = FiniteStateMachine(self)
		self.movement_state_machine.add_state('walk', self.handle_walk_state) # add state
		self.movement_state_machine.add_state('climb', self.handle_climb_state)
		self.movement_state_machine.add_state('jump', self.handle_jump_state)
		self.movement_state_machine.add_state('fall', self.handle_fall_state)
		self.movement_state_machine.add_state('land', self.handle_land_state)
		self.movement_state_machine.add_state('vehicle', self.handle_vehicle_state)
		self.movement_state_machine.add_state('none', self.handle_none_state)


	def handle_walk_state(self, FSM):

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
		com = vel[2]+move[2]
		self.worldLinearVelocity = [move[1],move[0], com]


	def handle_climb_state(self, FSM):
		pass

	def handle_jump_state(self, FSM):
		pass

	def handle_fall_state(self, FSM):
		pass

	def handle_land_state(self, FSM):
		pass

	def handle_vehicle_state(self, FSM):
		pass

	def handle_none_state(self, FSM):
		pass

	def is_grounded(self, FSM):
		pass

	def is_not_grounded(self, FSM):
		pass

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

	#
	def has_entered_none(self, FSM): # for dialogs
		pass

	def has_exited_none(self, FSM):
		pass


	###
	def handle_interactions(self):
		pass

	def fast_travel(self, location_id):
		pass

	def handle_camera(self):
		pass

	def remove_controls(self):
		self.stored_state = self.movement_state_machine.current_state

	def restore_controls(self):
		self.movement_state_machine.current_state = self.stored_state

	###
	def main(self):
		EntityBase.main(self)
		self.movement_state_machine.main()



### Testing
own = bge.logic.getCurrentController().owner

# Creat Entity
if not 'INIT' in own:
	bge.logic.globalDict['game'] = Player()
	own['INIT'] = ''

# If created already
else:
	Player.main(bge.logic.globalDict['game'])