import entities
import inventory

class Container(entities.EntityBase):
	def __init__(self, packet=None):
		entities.EntityBase.__init__(self, packet)
		
		self.inventory = inventory.Inventory()
		
	def on_interact(self, entity=None):
		pass