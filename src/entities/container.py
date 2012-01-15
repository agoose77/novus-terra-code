import entities
import game

class Container(entities.EntityBase):
	def __init__(self, packet=None):
		entities.EntityBase.__init__(self, packet)
		
	def on_interact(self, entity=None):
		game.Game.singleton.ui_manager.show('item_swap', args=[self['inventory']])