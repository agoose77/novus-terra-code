class Weapon:

	weapons = {}

	def __init__(self, id, name, description='', size=1, cost=0, effects={}, icon='cube.png', clip_size = 30, ammo_type = 1, weapon_type = 'Pistol'):
		self.id = len(self.weapons)+1
		self.type = type
		self.on_interact= 0

		self.name = name
		self.description = description
		self.icon = icon
		self.size = size
		self.cost = cost

		#
		self.weapon_type = weapon_type
		self.ammo_type = ammo_type
		self.clip_size = clip_size

		Weapon.weapons[id] = self

	def activate_item(self):
		pass
