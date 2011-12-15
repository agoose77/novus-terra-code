class Savefile:
	def __init__(self, filename='default.save'):
		self.entities = {} # cell -> list of entities
		self.filename = filename
		self.current_cell = None
		
	def save(self, filename=None):
		if filename is not None and filename != self.filename:
			self.filename = filename
			
		file = open('./data/saves/' + filename, 'wb')
		pickle.dump(self, file)
		file.close()
	
	@classmethod	
	def load(self, filename):
		file = open('./data/saves/' + filename, 'rb')
		savefile = pickle.load(file)
		file.close()
		
		
