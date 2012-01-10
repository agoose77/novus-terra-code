import entities
import sudo
import bge, random
""" editor properties:
 - dialogue - a string of the dialogue file, minus the path and file extension
 """
class Ghost(entities.EntityBase):
	""" A simple entity for talking to """
	def __init__(self, packet=None):
		super().__init__(packet)

		self.interact_label = 'Talk'
		self.health = 100
		print ('ghost init')

	def on_interact(self, player):
		sudo.world.dialogue_manager.display_dialogue('./data/dialogue/' + self['dialogue'] + '.xml')

	def update(self):
		if sudo.world.player.position:

			if self['Steer'] == 0:
				scene = bge.logic.getCurrentScene()
				if random.randint(0,5) == 4:
					name = random.choice(scene.objects)
				else:	
					name = scene.objects['player']
				self.move_to(name, 3)
		'''
		if sudo.world.player.position:
			loc = sudo.world.player.position
			l = [loc[0]-self.position[0], loc[1]-self.position[1], 0]
			self._data.alignAxisToVect(l, 1, 1.0)
			self._data.alignAxisToVect([0,0,1], 2, 1.0)

			self._data.setLinearVelocity( [0,6,-3], True)
		'''

	def damage(self, amount=1, object=None):
		self.health -= amount
		self.color = [1.0,self.health*.01,self.health*.01, 1.0]
		if self.health < 0:
			self.remove()

	def move_to(self, target_obj, behavior=3):

		# Stuff
		
		speed = 10

		# More Stuff
		st = self.controllers[0].actuators['Steering']
		st.behaviour = behavior

		# Speed
		st.velocity = speed
		st.acceleration = 0.5
		st.turnspeed = 10


		st.target = target_obj

		st.navmesh = bge.logic.getCurrentScene().objects['terrain_navmesh']

		# Activate it
		self['Steer'] = 1
