import cell
import pickle

class Prop:
	def __init__(self, co=[0.0,0.0,0.0]):
		self.id = 0
		self.name = "Monkey"
		self.co = co

class Entity:
	def __init__(self):
		self.id = 0
		self.name = "Monkey"
		self.co = [0.0,0.0,0.0]
		
class Cell:
	def __init__(self):
		self.id = 0
		self.name = ""
		self.props = []
		self.entities = [] #this needs consideration for save game state, probably just grab this from savefile unless it doesn't exist
		self.terrain = 0 #string of terrain file to load if needed
		self.blends = [] #list of string filenames that should be loaded before building cell
	
class CellManager:
	def __init__(self):
		pass
		
	def load(self, filepath):
		fo = open(filepath, 'rb')
		self.cell = pickle.load(fo)
		self.kdtree = cell.kdNode( self.cell.props )
	
	def update(self, position):
		pass