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
		print("CELL INIT")
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
		print(self.models)
		fo = open(filename, 'wb')
		pickle.dump(self,fo)
	
class CellManager:
	def __init__(self):
		self.props_in_game = []
		self.lamps_in_game = []
		self.entities_in_game = []
		
		# this will map out what objects are in what blends
		fo = open('./data/model_dict.data', 'rb')
		self.blend_dict = pickle.load( fo )
		
		self.updatetime = time.time()
		#needs a list of loaded libraries
		#self.load should check libraries needed, diff that with what's loaded
		
		scene = bge.logic.getCurrentScene()
		self.clean_object_list = []
		for entry in scene.objects:
			self.clean_object_list.append(entry)
		
	def load(self, filepath):
		self.cleanup()
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
		liblist = bge.logic.LibList()
		libs = []
		accum = []
		for entry in self.cell.models:
			for key in self.blend_dict:
				if entry in self.blend_dict[key]:
					if key not in accum: #this is the list of all libraries needed for this cell including loaded
						accum.append(key)
					if key not in libs and str(self.convert_lib_name(key)) not in liblist: #this is the list of libraries to load
						libs.append(key)
		#print(libs)
		for key in liblist:
			if self.convert_back(key) not in accum:
				print ("*", self.convert_back(key) )
				#bge.logic.LibFree(key)

		scene = bge.logic.getCurrentScene()
		print(scene.objects)
		print(scene.objectsInactive)
		print("=======")
		for entry in libs:
			bge.logic.LibLoad(entry, "Scene", load_actions=1)
			print(entry, " loaded..")
			
	def convert_lib_name(self, given):
		given = given.replace("/","\\")
		given = given.replace(".\\", "./")
		return given
	def convert_back(self, given):
		given = given.replace("\\","/")
		return given
	def cleanup(self):
		for entry in self.props_in_game:
			entry.game_object.endObject()
		for entry in self.lamps_in_game:
			entry.game_object.endObject()
		for entry in self.entities_in_game:
			entry.game_object.endObject()
		self.props_in_game, self.lamps_in_game, self.entities_in_game = [], [], []
		self.kdtrees = []
		self.lamp_kdtree = None
		
		scene = bge.logic.getCurrentScene()
		for entry in scene.objects:
			if entry not in self.clean_object_list:
				print("DIRTY:", entry)
				entry.endObject()
		print(self.clean_object_list)
		print("$$$$$$ CLEANED UP $$$$$")
		print(scene.objects)
		
	def spawn_prop(self, thing): 
		scene = bge.logic.getCurrentScene()
		new = scene.addObject(thing.name, "Cube")
		new.position = thing.co
		new.color = [1.0,1.0,1.0,0.0]
		new.localScale = thing.scale
		new.localOrientation = thing.rotation
		tweener.singleton.add(new, "color", "[*,*,*,1.0]", 1.0)
		return new
		
	def spawn_lamp(self, thing): #thing is either a prop or entity
		scene = bge.logic.getCurrentScene()
		new = scene.addObject(thing.type, "Cube") #the main .blend should have light objects in another layer, the names should correspond to the type property
		new.position = thing.co
		new.localOrientation = thing.rotation
		return new
	
	def update(self, position):
		#HACKS ENTITY HACKS HERE
		scene = bge.logic.getCurrentScene()
		if 'player' in scene.objects:
			position = scene.objects['player'].position
	
		if time.time() - self.updatetime > .6:
			self.updatetime = time.time()
			
			#lamps are seperated because they need a little different setup
			found_props = []
			found_lamps = []
			for i in range( len(self.kdtrees) ):
				self.kdtrees[i].getVertsInRange(position, pow(2,i)+i*20+1, found_props)
			#now add the lamps to this
			self.lamp_kdtree.getVertsInRange(position, 100, found_lamps)
			
			#loop for props
			to_remove = []
			for entry in self.props_in_game:
				if entry not in found_props:
					#ENTITY HACKS
					if entry.name != "player_location":
						tweener.singleton.add(entry.game_object, "color", "[*,*,*,0.0]", 1.0, callback=entry.game_object.endObject)
						entry.game_object = 0
						to_remove.append(entry)
			for entry in to_remove:
				self.props_in_game.remove(entry)
			for entry in found_props:
				if entry not in self.props_in_game:
					self.props_in_game.append(entry)
					entry.game_object = self.spawn_prop(entry)

			#loop for lamps			
			to_remove = []
			for entry in self.lamps_in_game:
				if entry not in found_lamps:
					entry.game_object = 0
					to_remove.append(entry)
			for entry in to_remove:
				self.lamps_in_game.remove(entry)
			for entry in found_lamps:
				if entry not in self.lamps_in_game:
					self.lamps_in_game.append(entry)
					entry.game_object = self.spawn_lamp(entry)

	