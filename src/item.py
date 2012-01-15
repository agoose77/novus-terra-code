import pickle

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

def load_items():
	file = open('./data/items.data', 'rb')
	items = pickle.load(file)
	file.close()
	
	for item_ in items:
		Item(id=item_[0], name=item_[1], type=item_[2], description=item_[3], icon=item_[4], cost=item_[5], size=item_[6], stack=item_[7])