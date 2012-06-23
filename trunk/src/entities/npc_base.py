import entities
import game

import bge


""" editor properties:
 - dialogue - a string of the dialogue file, minus the path and file extension
 """
class NPCBase(entities.EntityBase):
	""" A simple entity for talking to """
	def __init__(self, packet=None):
		super().__init__(packet)
		'''

		self.interact_label = 'Talk'
		self.armature = None
		self.animations = {}


	### ANIMATIONS ###
	def play_animation(self, name):
		self.animations[name] = 1

	def stop_animation(self, layer):
		for n in range(0, 7):
			if n != layer:
				self.armature.stopAction(n)

	def handle_animations(self):
		weapon = self.inventory.primary_weapon

		i = 0
		while(i < len(self.animations)):
			if self.animations[i] == 1:
				self.armature.playAction(str(weapon.name) + "_"+self.animations[i], 1, 64, layer=i, priority=2, blendin=5, play_mode=bge.logic.KX_ACTION_MODE_PLAY, speed=1.0)
				self.stop_animation(i)

		for name in self.animations:
			self.animations[name] = 0


	### METHODS ###
	def damage(self, amount=1, object=None):
		""" meant to be overidden """
		pass

	def move_to(self, target_obj, behavior=3):
		""" meant to be overidden """
		pass

	def on_interact(self, player):
		""" meant to be overidden """
		pass
		'''