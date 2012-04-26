import entities
import game

class Container(entities.EntityBase):
	def __init__(self, packet=None):
		entities.EntityBase.__init__(self, packet)

		self.interact_label = 'Open '

	def _wrap(self, ob):
		super()._wrap(ob)

		self.interact_label = 'Open ' + self['inventory'].name
		
	def on_interact(self, entity=None):
		game.Game.singleton.ui_manager.show('item_swap', args=[self['inventory']])