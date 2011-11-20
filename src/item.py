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
		


Item( '1', 0, '22 mm ammo', description='ammo that goes in the gun', size=1, cost=0, effects={}, icon='wrench.png')
Item( '2', 0, 'wrench', description='a wrench', size=1, cost=0, effects={}, icon='wrench.png')
Item( '0', 2, 'SMG machine gun', description='This is a gun you use to shoot things./nJust point and shoot', size=1, cost=0, effects={})
Item('3', 0, '')
Item('4', 0, '')
Item('5', 0, '')
Item(6, 0, '')
Item(7, 0, '')
Item(8, 0, '')
Item(9, 0, '')
Item(10, 0, '')