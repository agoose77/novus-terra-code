import entities
import item


class Pickup(entities.EntityBase):
	""" World representation of an item, interacting with it will add it the
	player's inventoy

	properties (set on the KX_GameObject):
		entity: set to 'Pickup'
		item: the ID of the item to represent
		amount: the amount of the item to add when picked up (default 1)
	"""

	def __init__(self, packet=0):
		super().__init__(packet)

		self.interact_label = 'Pickup'
		self.item = None
		self.amount = None

	def _wrap(self, ob):
		super()._wrap(ob)

		self.item = item.Item.items[self['item']]
		self.amount = self.get('amount', 1)

		self.interact_label = 'Pickup ' + self.item.name + ' (' + str(self.amount) + ')'

	def on_interact(self, player):
		""" Attempt to add the items to the inventory, leaving leftover items
		(items that couldn't be added to the inventory) on the world """
		leftover = player.inventory.add_item(self.item.id, self.amount)

		if leftover == self.amount:
			# Inventory is full
			# TODO - play denied sound effect
			pass

		elif leftover is not True:
			# Some, but not all, of the items were added to the inventory
			# TODO - play a sound effect
			self.amount = leftover
			self.interact_label = 'Pickup ' + self.item.name + ' (' + str(self.amount) + ')'

		else:
			# All the items were added to the inventory
			# TODO - play a sound effect
			self.remove()
