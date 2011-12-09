class Item:

	CONSUMABLE = 1
	QUEST = 2
	CLOTHING = 4

	items = {}

	def __init__(self, id, type, name, description='', size=1, cost=0, stack=10, effects={}, icon='cube.png'):
		self.id = id
		self.type = type
		self.on_interact= 0

		self.name = name
		self.description = description
		self.icon = icon
		self.size = size
		self.cost = cost
		self.stack = stack

		self.effects=effects
		Item.items[id] = self

	def activate_item(self):
		pass