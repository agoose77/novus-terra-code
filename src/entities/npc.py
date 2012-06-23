import entities
import game
""" editor properties:
 - dialogue - a string of the dialogue file, minus the path and file extension
 """
class NPC(entities.NPCBase):
	""" A simple entity for talking to """
	def __init__(self, packet=None):
		super().__init__(packet)

		self.interact_label = 'Talk'

	def on_interact(self, player):
		game.Game.singleton.world.dialogue_manager.display_dialogue('./data/dialogue/' + self['dialogue'] + '.xml')