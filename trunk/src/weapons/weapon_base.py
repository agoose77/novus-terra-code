class WeaponBase:
	""" Base class for all weapons """
	def __init__(self, grid_id):
		self.grid_id = grid_id
		self.name = 'base'

	def equip(self, entity):
		""" override this method if needed

		entity is the entity to equip the weapon """
		pass

	def unequip(self, entity):
		""" override this method if needed """
		pass

	def main(self):
		""" override this method if needed """
		pass
