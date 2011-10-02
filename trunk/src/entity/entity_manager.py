import pickle
import os
import time

import tweener
import terrain
import cell


try:
	import bge
	import ui
	import mathutils
	from paths import *
except:
	print("BGE imports failed, normal if you are running the cell editor")



class EntityManager:
	def __init__(self):
		self.props_in_game = []
		self.lamps_in_game = []
		self.entities_in_game = []

		self.ready_to_load = 0

		self.terrain = False

		# this will map out what objects are in what blends
		fo = open('./data/model_dict.data', 'rb')
		self.blend_dict = pickle.load( fo )
		fo.close()
		self.updatetime = time.time()
		#needs a list of loaded libraries
		#self.load should check libraries needed, diff that with what's loaded
		self.load_state = 0 #1 when a cell has been loaded and stays that way

		scene = bge.logic.getCurrentScene()
		self.clean_object_list = []
		for entry in scene.objects:
			self.clean_object_list.append(entry)


	def load(self, filepath):
		print("cell_manager.load()")
		self.cleanup()

		try:
			fo = open(filepath, 'rb')
			self.cell = pickle.load(fo)
			fo.close
		except:
			return("Failure to load "+filepath)

		scene = bge.logic.getCurrentScene()
		print (scene.objects)

		#set up a range of kdtrees
		self.kdtrees = []

		for pdata in self.cell.props:
			self.kdtrees.append( cell.kdNode( pdata ) )

		#tree for lamps
		self.lamp_kdtree = cell.kdNode( self.cell.lamps )
		print("---------")
		print("Loading "+filepath+"...")
		print("---------")
		self.load_libs()

		if "terrain" in self.cell.__dict__:
			if self.cell.terrain:
				self.load_terrain( self.cell.terrain)
			else:
				self.terrain = False

		tweener.singleton.add(ui.singleton.current, "color", "[*,*,*,0.0]", length=5.0, callback=ui.singleton.clear)


	def load_libs(self):
		scene = bge.logic.getCurrentScene()
		print(scene.objects)
		print("cell_manager.load_libs()")
		liblist = bge.logic.LibList()
		libs = []
		accum = []
		print(self.blend_dict)
		for entry in self.cell.models:
			for key in self.blend_dict:
				if entry in self.blend_dict[key]:
					if key not in accum: #this is the list of all libraries needed for this cell including loaded
						accum.append(key)
					if key not in libs and str(self.convert_lib_name(key)) not in liblist: #this is the list of libraries to load
						libs.append(key)
		print(libs)
		fred = []
		for key in liblist:
			if self.convert_back(key) not in accum:
				#print ("*", self.convert_back(key) )
				bge.logic.LibFree(key)
		scene = bge.logic.getCurrentScene()

		if self.cell.terrain:
			libs.append( './data/models/CHUNKS.blend' )
		print("=======")
		for entry in libs:
			bge.logic.LibLoad(entry, "Scene", load_actions=1)
			print(entry, " loaded..")

		print(scene.objectsInactive)
		print(bge.logic.LibList())


	def convert_lib_name(self, given):
		given = given.replace("/","\\")
		given = given.replace(".\\", "./")
		return given
	def convert_back(self, given):
		given = given.replace("\\","/")
		return given
	def cleanup(self):
		print("cell_manager.cleanup()")
		if 'entity_hack' in self.__dict__:
			self.__dict__.pop('entity_hack')
		self.props_in_game, self.lamps_in_game, self.entities_in_game = [], [], []
		self.kdtrees = []
		self.lamp_kdtree = None

		#ENTITY HACKS
		import game, bge

		if 'game' in bge.logic.globalDict:
			bge.logic.globalDict.pop('game')
			#bge.logic.globalDict['game'].world.player = None

		tweener.singleton.nuke() #probably paranoia

		scene = bge.logic.getCurrentScene()
		for entry in scene.objects:
			if entry not in self.clean_object_list:
				#print("DIRTY:", entry)
				entry.endObject()

		game.init_game = 0

		#set up light que (in lieu of cucumber branch)
		self.spots = []
		self.points = []
		for entry in scene.objectsInactive:
			if "SPOT" in entry.name:
				self.spots.append(entry)
			if "POINT" in entry.name:
				self.points.append(entry)
		print(self.spots)
		print(self.points)

		#scene.restart()
		print("$$$$$$ CLEANED UP $$$$$")


	def spawn_prop(self, thing):
		scene = bge.logic.getCurrentScene()
		new = scene.addObject(thing.name, "CELL_MANAGER_HOOK")
		new.position = thing.co
		new.color = [1.0,1.0,1.0,0.0]
		new.localScale = thing.scale
		new.localOrientation = thing.rotation
		if 'properties' in thing.__dict__:
			for p in thing.properties:
				new[p[0]] = p[1]
				if p == 'ITEM':
					print ('ITEM')

		tweener.singleton.add(new, "color", "[*,*,*,1.0]", 2.0)
		return new

	def spawn_lamp(self, thing): #thing is either a prop or entity
		print("spawning lamp")
		scene = bge.logic.getCurrentScene()

		#lightque things
		chosen = 'POINT'
		if thing.type == 'POINT':
			if len(self.points) > 0:
				chosen = self.points.pop(0)
		elif thing.type == 'SPOT':
			if len(self.spots) > 0:
				chosen = self.spots.pop(0)

		new = scene.addObject(chosen, "CELL_MANAGER_HOOK") #the main .blend should have light objects in another layer, the names should correspond to the type property
		new.position = thing.co
		new.localOrientation = thing.rotation
		new.distance = thing.distance
		new.energy = thing.energy

		if thing.type == 'SPOT':
			new.type = 0
			new.spotsize = thing.spot_size * 180 / 3.14
			new.spotblend = thing.spot_blend
			#new.bias = thing.spot_bias

		tweener.singleton.add(new, "color", str(thing.color), 2.0)
		return new

	def update(self):
		if self.load_state == 0:
			return
		#HACKS ENTITY HACKS HERE
		scene = bge.logic.getCurrentScene()
		position = 0
		if 'player' in scene.objects:
			position = scene.objects['player'].position
		else:
			for entry in self.cell.props:
				for prop in entry:
					if prop.name == "player_location":
						position = mathutils.Vector( prop.co )
		if 'explorer' in scene.objects:
			position = scene.objects['explorer'].position
		if position == 0:
			position = mathutils.Vector([0,0,0])
		if 'outdoor_sun_shadow' in scene.objects:
			scene.objects['outdoor_sun_shadow'].position = position

		# TERRAIN
		if self.terrain:
			terrain.qt_singleton.update_terrain(position)
			terrain.cq_singleton.update()

		if time.time() - self.updatetime > .5:
			self.updatetime = time.time()

			#lamps are seperated because they need a little different setup
			found_props = []
			found_lamps = []
			for i in range( len(self.kdtrees) ):
				self.kdtrees[i].getVertsInRange(position, pow(2,i)*6+i*60+1, found_props)
			#now add the lamps to this
			self.lamp_kdtree.getVertsInRange(position, 100, found_lamps)

			#loop for props
			to_remove = []
			for entry in self.props_in_game:
				if entry not in found_props:
					#ENTITY HACKS
					if entry.name not in ["player_location","Spaceship","helicopter",'Player', 'Vehicle', 'explorer']:
						tweener.singleton.add(entry.game_object, "color", "[*,*,*,0.0]", 2.0, callback=entry.kill)

			for entry in found_props:
				if entry not in self.props_in_game:
					if entry.name in scene.objectsInactive:
						self.props_in_game.append(entry)
						entry.game_object = self.spawn_prop(entry)
					else:
						print (entry.name)
						print( "ERROR: Trying to spawn a prop that doesn't have an object loaded")

			#loop for lamps
			to_remove = []
			for entry in self.lamps_in_game:
				if entry not in found_lamps:
					if entry.game_object:
						tweener.singleton.add(entry.game_object, "color", "[0,0,0.0]", 2.0, callback=entry.kill)

			for entry in found_lamps:
				if entry not in self.lamps_in_game:
					if ( entry.type == "POINT" and len(self.points) > 0 ) or ( entry.type == "SPOT" and len(self.spots) > 0 ):
						self.lamps_in_game.append(entry)
						entry.game_object = self.spawn_lamp(entry)

