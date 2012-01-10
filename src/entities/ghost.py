import entities
import sudo
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
			loc = sudo.world.player.position
			l = [loc[0]-self.position[0], loc[1]-self.position[1], 0]
			self._data.alignAxisToVect(l, 1, 1.0)
			self._data.alignAxisToVect([0,0,1], 2, 1.0)

			self._data.setLinearVelocity( [0,6,-3], True)

	def damage(self, amount=1, object=None):
		self.health -= amount
		self.color = [1.0,self.health*.01,self.health*.01, 1.0]
		if self.health < 0:
			self.remove()