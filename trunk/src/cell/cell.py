import pickle


class Cell:
	""" Pickleable object that stores cell data """
	def __init__(self):
		print("Cell.init()")
		self.id = 0
		self.name = ""
		self.filename = ""

		self.props = []
		self.entities = []
		self.lamps = []
		self.destinations = {}  # id => object relationship

		self.id_entity = {}  # id => entity object (only entities with assigned id's will be added)

		self.blends = []  # list of string filenames that should be loaded before building cell
		self.models = []  # list of string object names that are used in this cell

		self.terrain = None  # string of terrain file to load if needed
		self.navmesh = None  # navmesh or obstical avoidance

		self.modified = False

	def save(self):
		""" Pickle the data and save it to disk - used by cell editor """
		for prop_group in self.props:  # props are stored in a 2D array based on their size
			for prop in prop_group:
				if prop.name not in self.models:
					self.models.append(prop.name)

		for entity in self.entities:
			if entity.name not in self.models:
				self.models.append(entity.name)

		fo = open(self.filename, 'wb')
		pickle.dump(self, fo)
		fo.close()
