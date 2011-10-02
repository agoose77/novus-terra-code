class Item:

	CONSUMABLE_ITEM = 1
	QUEST_ITEM = 2
	CLOTHING_ITEM = 4
	WEAPON_ITEM = 8

	items = {}

	def __init__(self, id, type, name, description='', size=1, cost=0, effects={}, icon='cube.png'):
		self.id = id
		self.type = type
		self.on_interact= 0

		self.name = name
		self.description = description
		self.icon = icon
		self.size = size
		self.cost = cost

		self.effects=effects

		Item.items[id] = self

	def activate_item(self):
		pass
