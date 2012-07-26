import entities
import game


class Container(entities.EntityBase):
	""" An entity for 'containing' items. The entity has an associated
	inventory and ineracting with the entity will bring up the items
	swap screen.

	properties (set on the KX_GameObject):
		- entity: Set to 'Door'
		- cell: the name of the cell to teleport to
		- destination: the name of the object in the destination cell to teleport to
	"""

	def __init__(self, packet=None):
		super().__init__(packet)

		self.interact_label = 'Open'

	def _wrap(self, ob):
		super()._wrap(ob)

		self.interact_label = 'Open ' + self['inventory'].name

	def on_interact(self, player):
		game.Game.singleton.ui_manager.show('item_swap', args=[self['inventory']])
