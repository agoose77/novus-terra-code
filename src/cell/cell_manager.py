import pickle

import tweener

import cell
import math
import terrain
import sudo


try:
	import bge
	import mathutils
	import entities
	from game import Game
	from paths import *
	import savefile  # TODO - won't need this import when saving/loading is properly implimented
except:
	print("BGE imports failed, normal if you are running the cell editor")


class CellManager:
	""" Implements several KD Trees to keep track of props in the current cell.
	Adds and removes props and lights as the player moves towards and away from them.

	Also handles the construction of new cells.
	"""

	singleton = None

	def __init__(self):
		CellManager.singleton = self
		self.cell = None
		self.props_in_game = [[],  [],  [],  [],  [], [], [], [], [], [], [], [], [], [], []]
		self.lamps_in_game = []
		self.entities_in_game = []
		self.prop_kdtrees = []
		self.lamp_kdtree = None
		self.points = []
		self.spots = []
		self.alights = []

		self.ready_to_load = 0
		self.hook = 0  # used for a tweener callback
		self.next_destination = None  # ID of the destination to teleport the player to

		self.terrain = False

		# this will map out what objects are in what blends
		with open('./data/model_dict.data', 'rb') as fo:
			self.blend_dict = pickle.load(fo)

		self.updatetime = Game.singleton.game_time

		# needs a list of loaded libraries
		# self.load should check libraries needed, diff that with what's loaded
		self.load_state = 0  # 1 when a cell has been loaded and stays that way

		# make a list of objects that aren't apart of the cell (won't get removed on clean up)
		scene = bge.logic.getCurrentScene()
		self.clean_object_list = []

		for ob, blend in self.blend_dict.items():
			if blend == './data/models/entities/player_file.blend':
				self.clean_object_list.append(ob)

		for ob in scene.objects:
			self.clean_object_list.append(ob.name)

	def load(self, filepath):
		""" Creates a callback to begin loading a cell
		(cells aren't loaded straight away so the screen can fade out)
		"""

		if Game.singleton.savefile is None:
			Game.singleton.savefile = savefile.Savefile()  # TODO - this should be handled when New Game / Load Game
														  # options are called.
		self.load_state = 0
		Game.singleton.ui_manager.show('loading')
		tweener.singleton.add(self, "hook", 3, length=1.0, callback=lambda: self.begin_loading(filepath))

	def begin_loading(self, filepath):
		""" Loads the cell """
		print("cell_manager.load()")
		print("---------")
		print("Loading " + filepath + "...")
		print("---------")

		#hook for world to handle player stuff
		Game.singleton.world.cell_loading()

		self.cleanup()

		try:
			fo = open(filepath, 'rb')
			self.cell = pickle.load(fo)
			self.cell.name = filepath
			fo.close
		except IOError:
			print("Unable to open " + filepath)
			return("Unable to open " + filepath)
		except (pickle.UnpicklingError, AttributeError, ImportError, EOFError):
			print("Unable to build cell, the cell might be outdated\nTry baking with the latest cell editor")
			return("Unable to build cell, the cell might be outdated")

		# FX
		self.fx = self.cell.fx

		for item in self.fx:
			bge.logic.getCurrentScene().objects['FX'][item] = self.fx[item]
			print (item, self.fx[item], bge.logic.getCurrentScene().objects['FX'][item])

		# Setup prop kdtrees
		self.prop_kdtrees = []
		for prop_group in self.cell.props:
			self.prop_kdtrees.append(cell.kdNode(prop_group))

		# Setup lamp kdtree
		self.lamp_kdtree = cell.kdNode(self.cell.lamps)

		self.load_libs()

		if hasattr(self.cell, 'terrain'):  # TODO - remove this if statement, its for compatability to older cells
			if self.cell.terrain:
				self.load_terrain(self.cell.terrain)
			else:
				self.terrain = False

		tweener.singleton.add(self, "hook", 3, length=.5, callback=self.load_entities)  # using a callback so the entities are put into a built level

	def cleanup(self):
		""" Revert the scene to its default state """
		print("cell_manager.cleanup()")
		scene = bge.logic.getCurrentScene()

		if 'entity_hack' in self.__dict__:  # JP forget what this is for
			self.__dict__.pop('entity_hack')

		# Update the entities setup packet, and unwrap from their objects
		if self.cell:
			self.cell.id_entity = {}
			if self.cell.name in Game.singleton.savefile.entities:
				for entity in Game.singleton.savefile.entities[self.cell.name]:
					if entity._data:
						entity.packet.co = entity._data.position[:]
						entity.packet.rotation = entity._data.orientation.to_euler()[:]
						entity._data.endObject()
						entity._unwrap()

		# Remove props
		for prop_group in self.props_in_game:
			for prop in prop_group:
				prop.kill()

		# Remove dirty objects
		for obj in scene.objects:
			if obj.name not in self.clean_object_list:
				obj.endObject()

		# set up light que (in lieu of cucumber branch)
		self.spots = []
		self.points = []
		for entry in scene.objectsInactive:
			#self.alights.append(entry)
			if "SPOT" in entry.name:
				self.spots.append(entry)
			if "POINT" in entry.name:
				self.points.append(entry)

		self.props_in_game = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
		self.lamps_in_game = []
		self.entities_in_game = []
		self.prop_kdtrees = []
		self.lamp_kdtree = None

	def load_terrain(self, filename):
		""" Load a terrain file """
		print("cell_manager.load_terrain()")
		#bge.logic.addScene("background", 0)
		scene = bge.logic.getCurrentScene()
		sudo.sun = scene.addObject('outdoor_sun_shadow', "CELL_MANAGER_HOOK")
		#atmosphere = scene.addObject('Atmosphere2', "CELL_MANAGER_HOOK")
		terrain.tr_singleton = terrain.Map_Manager()  # should do this in cell manager init
		if len(filename.split('\\')) > 1:
			filename = filename.split('\\')[-1]  # redundant, but making sure it's just the filename not the path - # TODO
		terrain.tr_singleton.load('./data/terrains/' + filename)
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
		size = math.pow(2, depth + 5)  # TODO - variable never assigned - remove?

		terrain.qt_singleton = terrain.tr_singleton.map.quadtree
		self.terrain = 1

	def load_libs(self):
		""" Load all the libraries required for the current cell """
		print("cell_manager.load_libs()")
		print("=========")

		liblist = bge.logic.LibList()
		libs_to_load = []

		# Determine which libs to load
		for model in self.cell.models:
			if model in self.blend_dict:
				blend = self.blend_dict[model]
				if blend not in libs_to_load:
					libs_to_load.append(blend)

		#JP hardcoding player and a few other things, might not be the perfect place for this? MANDATORY.blend is included in cells via the editor
		for entry in sudo.game.mandatory_blends:
			if entry not in libs_to_load:
				libs_to_load.append(entry)

		# Free un used libs
		for lib in liblist:
			if self.convert_back(lib) not in libs_to_load and 'player.blend' not in lib:
				bge.logic.LibFree(lib)
				print("[freed]", lib)

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
		#hook for world to handle player stuff
		Game.singleton.world.cell_loaded()

		self.cell.id_entity['player'] = sudo.player

		if self.cell.name in Game.singleton.savefile.entities:
			# This cell has been visited before
			self.entities_in_game = Game.singleton.savefile.entities[self.cell.name]

		else:
			# Cell is un visited
			for entity in self.cell.entities:
				new_entity = getattr(entities, entity.class_)(entity)
				self.entities_in_game.append(new_entity)
			Game.singleton.savefile.entities[self.cell.name] = self.entities_in_game

		Game.singleton.ui_manager.hide('loading')
		self.load_state = 1

	def convert_lib_name(self, given):
		given = given.replace("/", "\\")
		given = given.replace(".\\", "./")
		return given

	def convert_back(self, given):
		#given = given.replace("\\\\","/")
		given = given.replace("\\", "/")
		return given

	def spawn_prop(self, data):
		""" Spawn a single prop
		data - Prop or Entity object
		"""
		scene = bge.logic.getCurrentScene()

		prop = scene.addObject(data.name, "CELL_MANAGER_HOOK")
		prop.position = data.co
		prop.color = [1.0, 1.0, 1.0, 0.0]
		prop.localScale = data.scale
		prop.localOrientation = data.rotation
		if hasattr(data, 'properties'):
			for name, value in data.properties:
				prop[name] = value

		if Game.singleton.graphics_options['Fade in props']:
			tweener.singleton.add(prop, "color", "[*,*,*,1.0]", 2.0)
		else:
			prop.color = [1.0, 1.0, 1.0, 1.0]
		return prop

	def spawn_lamp(self, data):  # data is either a prop or entity
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

		lamp = scene.addObject(chosen, "CELL_MANAGER_HOOK")  # the main .blend should have light objects in another layer, the names should correspond to the type property
		lamp.position = data.co
		lamp.localOrientation = data.rotation
		lamp.distance = data.distance
		lamp.energy = data.energy

		if data.type == 'SPOT':
			lamp.type = 0
			lamp.spotsize = data.spot_size * 180 / 3.14
			lamp.spotblend = data.spot_blend

		tweener.singleton.add(lamp, "color", str(list(data.color)), 2.0)
		print ("LAMPSINGINGIN!!!!!!!!!!!!!!!!!!!!!!!!!!!")
		return lamp

	def load_model(self, model):

		if model in self.blend_dict:
			blend = self.blend_dict[model]

			if str(self.convert_lib_name(blend)) not in bge.logic.LibList():
				print("[loading] ", blend, "...")
				bge.logic.LibLoad(blend, "Scene", load_actions=1)

			else:
				print ("[loaded] Error: Blend already loaded")
		else:
			print ("[loaded] Error: Model not found in blend_dict")

	def update(self):
		if self.load_state == 0:
			# don't do anything while the cell is changing
			return

		# get a point to update everything by
		KX_player = sudo.world.KX_player
		#if self.next_destination is not None:
		#	position = mathutils.Vector(self.cell.destinations[self.next_destination].co)

		scene = bge.logic.getCurrentScene()

		if KX_player:
			position = KX_player.worldPosition
		else:
			position = mathutils.Vector([0, 0, 0])

		if 'outdoor_sun_shadow' in scene.objects:
			scene.objects['outdoor_sun_shadow'].position = position

		if Game.singleton.game_time > self.updatetime + 0.5:
			# update terrain
			if self.terrain:
				terrain.qt_singleton.update_terrain(position)
				terrain.cq_singleton.update()

			# update props
			for i, props in enumerate(self.prop_kdtrees):
				to_remove = self.props_in_game[i][:]
				found_props = []

				try:
					v = sudo.game.graphics_options['Prop distance']
					g = sudo.game.graphics_options['Grass distance']
				except:
					v = 5
					g = 2
				props.getVertsInRange(position, pow(2, i) * (v * 2) + i * 60 + 3 + g * 10, found_props)
				self.found_props = found_props
				for prop in found_props:
					if prop in to_remove:
						# keep prop in scene
						to_remove.remove(prop)
					else:
						# add the prop
						self.props_in_game[i].append(prop)
						prop.game_object = self.spawn_prop(prop)

				for prop in to_remove:
					if prop.name not in ["player_location", "Spaceship", "helicopter",
							'player', 'Vehicle', 'explorer', 'explorer2']:
						# remove prop
						if Game.singleton.graphics_options['Fade in props']:
							tweener.singleton.add(prop.game_object, "color", "[*,*,*,0.0]", 2.0, callback=prop.kill)
						else:
							prop.kill()

			# update lamps
			to_remove = self.lamps_in_game[:]
			found_lamps = []
			self.lamp_kdtree.getVertsInRange(position, 100, found_lamps)

			print (str(found_lamps )+ "blab lbalbalbalbalba")

			for lamp in found_lamps:
				print ("Found lamps! --------------------------------")
				if lamp in to_remove:
					# keep lamp in scene
					to_remove.remove(lamp)
				else:
					# add the lamp
					if (lamp.type == "POINT" and len(self.points) > 0) or (lamp.type == "SPOT" and len(self.spots) > 0):
						self.lamps_in_game.append(lamp)
						lamp.game_object = self.spawn_lamp(lamp)
						print ("spawned lamp ++++++++++++++++++")

			for lamp in to_remove:
				# remove the lamp
				lamp.kill()  # TODO - fade intensity?

			self.updatetime = Game.singleton.game_time

		sudo.entity_manager.update()
		for entity in self.entities_in_game:
			entity.main()
