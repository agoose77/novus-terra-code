import os
import pickle
import time

import tweener
import terrain
import cell
from item import Item
from weapon import Weapon

try:
	import bge
	import mathutils
	import session
	import ui
	from entity_base import EntityBase
	from game import Game
	from paths import *
except:
	print("BGE imports failed, normal if you are running the cell editor")

class CellManager:
	""" Manages the current cell, keeps track of objects in the scene """
	
	singleton = None
	
	def __init__(self):
		CellManager.singleton = self
		self.cell = None
		self.props_in_game = []
		self.lamps_in_game = []
		self.entities_in_game = []
		self.prop_kdtrees = []
		self.lamp_kdtree = None
		self.points = []
		self.spots = []
		
		self.ready_to_load = 0
		self.hook = 0 # used for a tweener callback
		self.next_destination = None # ID of the destination to teleport the player to
		
		self.terrain = False
		
		# this will map out what objects are in what blends
		fo = open('./data/model_dict.data', 'rb')
		self.blend_dict = pickle.load( fo )
		fo.close()
		self.updatetime = time.time()
		
		# needs a list of loaded libraries
		# self.load should check libraries needed, diff that with what's loaded
		self.load_state = 0 # 1 when a cell has been loaded and stays that way
		
		# make a list of objects that aren't apart of the cell
		scene = bge.logic.getCurrentScene()
		self.clean_object_list = []
		for obj in scene.objects:
			self.clean_object_list.append(obj)

	def load(self, filepath):
		""" Creates a callback to begin loading a cell
		(cells aren't loaded straight away so the screen can fade out)
		"""
		self.load_state = 0
		ui.singleton.show_loading()
		tweener.singleton.add(self, "hook", 3, length=.5, callback= lambda: self.begin_loading(filepath))
		
	def begin_loading(self, filepath):
		""" Loads the cell """
		print("cell_manager.load()")
		print("---------")
		print("Loading "+filepath+"...")
		print("---------")
		scene = bge.logic.getCurrentScene()
		
		self.cleanup()
		
		try:
			fo = open(filepath, 'rb')
			self.cell = pickle.load(fo)
			self.cell.name = filepath
			fo.close
		except IOError:
			return("Unable to open "+filepath)
		except pickle.UnpicklingError:
			return("Unable to build cell, the cell might be outdated")
		
		# Setup prop kdtrees
		self.prop_kdtrees = []
		for prop_group in self.cell.props:
			self.prop_kdtrees.append( cell.kdNode( prop_group ) )
		
		# Setup lamp kdtree
		self.lamp_kdtree = cell.kdNode( self.cell.lamps )
		
		self.load_libs()

		if hasattr(self.cell, 'terrain'):
			if self.cell.terrain:
				self.load_terrain( self.cell.terrain)
			else:
				self.terrain = False
		
		self.load_state = 1
		tweener.singleton.add(self, "hook", 3, length=.5, callback=self.load_entities)	# using a callback so the entities are put into a built level
		
	
	def cleanup(self):
		""" Revert the scene to its default state """
		print("cell_manager.cleanup()")
		scene = bge.logic.getCurrentScene()
		
		if 'entity_hack' in self.__dict__: #JP forget what this is for
			self.__dict__.pop('entity_hack')
		
		self.props_in_game = []
		self.lamps_in_game = []
		self.entities_in_game = []
		self.prop_kdtrees = []
		self.lamp_kdtree = None

		# Update the entities setup packet, and unwrap from their objects
		if self.cell and self.cell.name in session.savefile.entities:
			for entity in session.savefile.entities[ self.cell.name ]:
				if entity._data:
					entity.packet.co = entity._data.position[:]
					entity.packet.rotation = entity._data.orientation.to_euler()[:]
					entity._data.endObject()
					entity._unwrap()
					
					
		# Remove props
		for prop in self.props_in_game:
			prop.kill()
		
		# Remove dirty objects
		for obj in scene.objects:
			if obj not in self.clean_object_list:
				obj.endObject()

		# set up light que (in lieu of cucumber branch)
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
	
	def load_terrain(self, filename):
		""" Load a terrain file """
		print("cell_manager.load_terrain()")
		bge.logic.addScene("background", 0)
		scene = bge.logic.getCurrentScene()
		new = scene.addObject('outdoor_sun_shadow', "CELL_MANAGER_HOOK")

		terrain.tr_singleton = terrain.Map_Manager() #should do this in cell manager init
		terrain.tr_singleton.load(filename)
		terrain.cq_singleton = terrain.Chunk_Que()
		
		width = terrain.tr_singleton.map.width
		height = terrain.tr_singleton.map.height
		best = max(width, height)
		## 4096 7
		## 2048 6
		## 1024 5
		## 512  4
		## 256  3
		## 128  2
		## 64   1
		depth = max(1, math.ceil(math.log(best, 2) - 5))
		size = math.pow(2, depth+5)
		
		terrain.qt_singleton = terrain.Quadtree(int(size/2), [0,0], 1, max_depth=depth, scale = terrain.tr_singleton.map.scale)
		self.terrain = 1

	def load_internal(self, filepath):
			pass
	
	def load_libs(self):
		""" Load all the libraries required for the current cell """
		print("cell_manager.load_libs()")
		print("=========")

		scene = bge.logic.getCurrentScene()
		liblist = bge.logic.LibList()
		libs_to_load = []
		
		# Determine which libs to load
		print(self.cell.models)
		for model in self.cell.models:
			if model in self.blend_dict:
				blend = self.blend_dict[model]
				if blend not in libs_to_load:
					libs_to_load.append(blend)

		# Free un used libs
		for lib in liblist:
			if self.convert_back(lib) not in libs_to_load:
				bge.logic.LibFree(lib)
				print("[freed]", blend)

		# Load terrain
		if self.cell.terrain:
			libs_to_load.append('./data/models/CHUNKS.blend')

		# Load libs
		for blend in libs_to_load:
			if str(self.convert_lib_name(blend)) not in liblist:
				print("[loading] ", blend, "...")
				bge.logic.LibLoad(blend, "Scene", load_actions=1)

	def load_entities(self):
		""" Load all the entities in the current cell """
		if self.cell.name in session.savefile.entities:
			# This cell has been visited before
			self.entities_in_game = session.savefile.entities[ self.cell.name ]
			for entity in self.entities_in_game:
				if entity.packet:
					ob = self.spawn_prop(entity.packet)
					entity._wrap( ob )
		
		else:
			# Cell is un visited
			for entity in self.cell.entities:
				new_entity = Game.entity_map[entity.class_] (entity)
				new_entity._wrap( self.spawn_prop(entity) )
				self.entities_in_game.append( new_entity )
			session.savefile.entities[ self.cell.name ] = self.entities_in_game
		
		tweener.singleton.add(ui.singleton.current, "color", "[*,*,*,0.0]", length=1.0, callback=ui.singleton.clear)


	def convert_lib_name(self, given):
		given = given.replace("/","\\")
		given = given.replace(".\\", "./")
		return given

	def convert_back(self, given):
		given = given.replace("\\","/")
		return given

	def spawn_prop(self, data):
		""" Spawn a single prop
		data - Prop or Entity object
		"""
		scene = bge.logic.getCurrentScene()
		
		prop = scene.addObject(data.name, "CELL_MANAGER_HOOK")
		prop.position = data.co
		prop.color = [1.0,1.0,1.0,0.0]
		prop.localScale = data.scale
		prop.localOrientation = data.rotation
		if hasattr(data, 'properties'):
			for name, value in data.properties:
				prop[name] = value
		
		if prop.name == 'player' and self.next_destination is not None: # TODO - this is probably a bad spot for this
			prop.worldPosition = self.cell.destinations[self.next_destination].co
			prop.worldOrientation = mathutils.Quaternion(self.cell.destinations[self.next_destination].rotation).to_matrix()
			self.next_destination = None
			
		tweener.singleton.add(prop, "color", "[*,*,*,1.0]", 2.0)
		print("[spawned]", prop)
		return prop
	
	def spawn_lamp(self, data): #thing is either a prop or entity
		""" Spawn a light 
		
		data - Lamp object
		"""
		scene = bge.logic.getCurrentScene()

		#lightque datas
		chosen = 'POINT'
		if data.type == 'POINT':
			if len(self.points) > 0:
				chosen = self.points.pop(0)
		elif data.type == 'SPOT':
			if len(self.spots) > 0:
				chosen = self.spots.pop(0)

		lamp = scene.addObject(chosen, "CELL_MANAGER_HOOK") #the main .blend should have light objects in another layer, the names should correspond to the type property
		lamp.position = data.co
		lamp.localOrientation = data.rotation
		lamp.distance = data.distance
		lamp.energy = data.energy

		if data.type == 'SPOT':
			lamp.type = 0
			lamp.spotsize = data.spot_size * 180 / 3.14
			lamp.spotblend = data.spot_blend
			#new.bias = data.spot_bias

		tweener.singleton.add(lamp, "color", str(data.color), 2.0)
		print('[spawned]', lamp)
		return lamp
		
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
		if self.next_destination is not None:
			position = mathutils.Vector(self.cell.destinations[self.next_destination].co)
		
		
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
			for i in range( len(self.prop_kdtrees) ):
				self.prop_kdtrees[i].getVertsInRange(position, pow(2,i)*6+i*60+1, found_props)
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

