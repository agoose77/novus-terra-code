import pickle


class Item:

	CONSUMABLE = 1
	QUEST = 2
	CLOTHING = 4
	WEAPON = 8

	items = {}

	def __init__(self, id, name, type, description='', icon='cube.png',
		cost=0, size=[1, 1], stack=10, properties={}):
		self.id = id
		self.type = type

		self.name = name
		self.description = description
		self.icon = icon
		self.size = size
		self.cost = cost
		self.stack = stack

		self.properties = properties

		Item.items[id] = self

	def activate_item(self):
		pass


def load_items():
	file = open('./data/items.data', 'rb')
	items = pickle.load(file)
	file.close()

	for item_ in items:
		Item(*item_)
