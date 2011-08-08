import cell
import pickle
import os
import time

import tweener

try:
	import bge
except:
	print("BGE import failed, normal if you are running the cell editor")

class Prop:
	def __init__(self, name="None", co=[0.0,0.0,0.0], scale=[1.0,1.0,1.0], dimensions=[1.0,1.0,1.0], rotation=[1.0,0.0,0.0]):
		self.id = 0
		self.name = name
		self.co = co
		self.scale = scale
		self.dimensions = dimensions
		self.rotation = rotation
		self.game_object = 0 #the BGE object pointer

class Entity:
	def __init__(self):
		self.id = 0
		self.name = "Monkey"
		self.co = [0.0,0.0,0.0]
		
class Lamp:
	def __init__(self, name="None", co=[0.0,0.0,0.0], rotation=[1.0,0.0,0.0], type="POINT", color=[0.0,0.0,0.0], distance=0.5, energy=50):
		self.id = 0
		self.name = name
		self.co = co
		self.rotation = rotation
		self.type = type
		self.color = color
		self.distance = distance
		self.energy = energy
		
class Cell:
	def __init__(self):
		self.id = 0
		self.name = ""
		self.props = []
		self.entities = [] #this needs consideration for save game state, probably just grab this from savefile unless it doesn't exist
		self.lamps = []
		self.terrain = 0 #string of terrain file to load if needed
		self.blends = [] #list of string filenames that should be loaded before building cell
		self.models = [] #list of string object names that are used in this cell
	def save(self, filename): #this is for level creation and shouldn't be used at runtime
		for thing in self.props:
			for entry in thing:
				if entry.name not in self.models:
					self.models.append( entry.name )
		
		for entry in self.lamps:
			print(entry.name)
			if entry.name not in self.models:
					self.models.append( entry.name )
		fo = open(filename, 'wb')
		pickle.dump(self,fo)
	
class CellManager:
	def __init__(self):
		self.objects_in_game = []
		
		# this will map out what objects are in what blends
		fo = open('./data/model_dict.data', 'rb')
		self.blend_dict = pickle.load( fo )
		
		self.updatetime = time.time()
		#needs a list of loaded libraries
		#self.load should check libraries needed, diff that with what's loaded
		
	def load(self, filepath):
		fo = open(filepath, 'rb')
		self.cell = pickle.load(fo)
		#set up a range of kdtrees

		self.kdtrees = []
		for pdata in self.cell.props:
			self.kdtrees.append( cell.kdNode( pdata ) )
			
		#tree for lamps
		self.lamp_kdtree = cell.kdNode( self.cell.lamps )
		print("---------")
		print("cell "+filepath+" loaded.")
		self.load_libs()
		
	def load_libs(self):
		libs = []
		for entry in self.cell.models:
			for key in self.blend_dict:
				if entry in self.blend_dict[key]:
					if key not in libs:
						libs.append(key)
		for entry in libs:
			bge.logic.LibLoad(entry, "Scene", load_actions=1)
			print(entry, " loaded..")
	
	def spawn(self, thing): #thing is either a prop or entity
		scene = bge.logic.getCurrentScene()
		new = scene.addObject(thing.name, "Cube")
		new.position = thing.co
		##### HACKS
		if isinstance(thing, cell.Lamp):
			print(new.position)
			print(new, type(new))

			d = "color[2]"
		else:
			new.color = [1.0,1.0,1.0,0.0]
			d = "color[3]"
			new.localScale = thing.scale
			
			tweener.singleton.add(new, d, 1.0, 1.0)
		
		
		new.localOrientation = thing.rotation
		return new
	
	def update(self, position):
		if time.time() - self.updatetime > .6:
			self.updatetime = time.time()
			
			found = []
			
			for i in range( len(self.kdtrees) ):
				self.kdtrees[i].getVertsInRange(position, pow(2,i)+i*20+1, found)
			#now add the lamps to this
			self.lamp_kdtree.getVertsInRange(position, 100, found)
			to_remove = []
			for entry in self.objects_in_game:
				if entry not in found:
					#### HACKS
					if isinstance(entry, cell.Lamp):
						print("removing lamp")
						d = "color[2]"
						entry.game_object.endObject()
					else:
						print(entry.name, " is an object.")
						d = "color[3]"
						
						tweener.singleton.add(entry.game_object, d, -1.0, 1.0, callback=entry.game_object.endObject)
					
					
					entry.game_object = 0
					to_remove.append(entry)
			for entry in to_remove:
				self.objects_in_game.remove(entry)
			for entry in found:
				if entry not in self.objects_in_game:
					self.objects_in_game.append(entry)
					entry.game_object = self.spawn(entry)
					

				
	