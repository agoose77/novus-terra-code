import entities
import inventory
import ui

class Container(entities.EntityBase):
	def __init__(self, packet=None):
		entities.EntityBase.__init__(self, packet)
		
	def on_interact(self, entity=None):
		ui.singleton.show_item_swap(self['inventory'])