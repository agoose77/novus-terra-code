import cell
import pickle
import bge

class Prop:
	def __init__(self, co=[0.0,0.0,0.0], scale=[1.0,1.0,1.0]):
		self.id = 0
		self.name = "Monkey"
		self.co = co
		self.scale = scale
		self.game_object = 0 #the BGE object pointer

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
		
	def save(self, filename): #this is for level creation and shouldn't be used at runtime
		fo = open(filename, 'wb')
		pickle.dump(self,fo)
	
class CellManager:
	def __init__(self):
		self.objects_in_game = []
		
	def load(self, filepath):
		fo = open(filepath, 'rb')
		self.cell = pickle.load(fo)
		self.kdtree = cell.kdNode( self.cell.props )
		print("cell "+filepath+" loaded.")
		print( len(self.cell.props) )
	
	def spawn(self, thing): #thing is either a prop or entity
		scene = bge.logic.getCurrentScene()
		new = scene.addObject("Monkey", "Cube")
		new.position = thing.co
		return new
	
	def update(self, position):
		found = []
		self.kdtree.getVertsInRange(position, 20, found)
		#print(found)
		to_remove = []
		for entry in self.objects_in_game:
			if entry not in found:
				try:
					entry.game_object.endObject()
				except:
					pass
				entry.game_object = 0
				to_remove.append(entry)
		for entry in to_remove:
			self.objects_in_game.remove(entry)
		for entry in found:
			if entry not in self.objects_in_game:
				self.objects_in_game.append(entry)
				entry.game_object = self.spawn(entry)
				