"""
Novus Terra - Cell Editor

This addon is for use with populating areas for the Novus Terra game.

CE: Cell Editor
IE: Inventory Editor
"""

bl_info = {
	"name": "Novus Terra - Cell Editor",
	"author": "joe@designisgood.com, andrew-101",
	"version": (1,1,0),
	"blender" : (2,6,0.1),
	"api": 41226,
	"location": "Scene Panel",
	"description": "Edit interior and exterior cells",
	"catergory": "Game Engine"}

import math
import os
import pickle
import re
import sys

import bpy
from bpy_extras.io_utils import ImportHelper, ExportHelper

sys.path.append('./src/')
from cell import Prop, Lamp, Cell, Entity, Destination
from inventory import Inventory

CELL_NONE = ""
CELL_INTERIOR = 'Interior'
CELL_EXTERIOR = 'Exterior'
MODE_EDIT = 'edit'
MODE_MANAGE = 'manage'
MODE_HELP = 'help'
MODE_IE = 'inv_edit'

blend_dict = {}
model_dict = {}

map = None # Terrain file

def construct_blend_dict(assets):
	""" Open a list of .blends and find out what objects are within it

	assets: a list of blend filepaths
	"""
	blend_dict = {}
	for blend in assets:
		blend_dict[blend] = []
		
		file = open(blend, 'rb')
		data = str(file.read())
		file.close()
		
		parts = data.split("OB")
		for n in range(len(parts)):
			obj_name = ""
			t = 0
			
			if n != 0 and parts[n-1][-2:] == "00":
				if parts[n][:4] != "JECT":
					if parts[n][t] not in ["\\", " ","?",".",")","("]:
						while (parts[n][t] not in ["\\", " "]):
							obj_name += parts[n][t]
							t += 1
							
			if obj_name:
				#blend_dict[obj_name] = blend
				blend_dict[blend].append(obj_name)
				
	return blend_dict
				
def walk_dir(path):
	""" Recursively walk a directory and find all the .blends within it """
	assets = []
			
	for file in os.listdir(path):
		if os.path.isdir(path + "/" + file):
			if not file.startswith("."):
				# Ignore . dirs (e.g .svn)
				assets.extend(walk_dir(path + "/" + file))
		elif file.endswith('.blend'):
			assets.append(path + "/" + file)
	
	return assets
	
def init():
	""" Setup all the properties """
	# Cell editor props
	bpy.types.Scene.ce_asset_dir = bpy.props.StringProperty(name='Asset Directory', default='./data/models', description='Filepath to asset folder')
	bpy.types.Scene.ce_assets = bpy.props.CollectionProperty(type=CE_asset_properties)
	bpy.types.Scene.ce_name = bpy.props.StringProperty(name='Cell Name', default='')
	bpy.types.Scene.ce_type = bpy.props.StringProperty(default=CELL_NONE)
	bpy.types.Scene.ce_mode = bpy.props.EnumProperty(
		name = "Mode",
		items = (
			(MODE_EDIT, ' Edit Cell', ''),
			(MODE_MANAGE, 'Manage Assets', ''),
			(MODE_IE, 'Edit Inventories', ''),
			(MODE_HELP, 'Help', '')
		),
		default = 'edit')
	
	# cell options
	bpy.types.Scene.ce_terrain = bpy.props.BoolProperty(name='Terrain', default=False, description='Attach a terrain file to this cell')
	bpy.types.Scene.ce_terrain_detail = bpy.props.IntProperty(name='Terrain Detail', default=0, description='Detail level of terrain preview')
	bpy.types.Scene.ce_terrain_file = bpy.props.StringProperty(name='Terrain File', default='', description='Path to terrain file')
	bpy.types.Scene.ce_hdr = bpy.props.BoolProperty(name='HDR', default=False, description='Enable HDR in this cell')
	bpy.types.Scene.ce_bloom = bpy.props.BoolProperty(name='Bloom', default=False, description='Enable bloom in this cell')
	bpy.types.Scene.ce_tint = bpy.props.BoolProperty(name='Tint', default=False, description='Enable color tinting in this cell')
	bpy.types.Scene.ce_tint_color = bpy.props.FloatVectorProperty(name='Tint Color', default=[1.0, 1.0, 1.0], max=1.0, min=0.0, subtype='COLOR', description='Select color tint')
	
	# Inventory editor props
	bpy.types.Scene.ie_inventories = bpy.props.CollectionProperty(type=IE_Inventory, name='Inventories')
	bpy.types.Scene.ie_inventory_index = bpy.props.IntProperty()

class IE_Item(bpy.types.PropertyGroup):
	""" Property group for items """
	name = bpy.props.StringProperty(name='Item ID') # Item ID
	amount = bpy.props.IntProperty(name='Amount', default=1)

class IE_Inventory(bpy.types.PropertyGroup):
	""" Property group for inventories """
	name = bpy.props.StringProperty(name='Inventory ID') # Inventory ID
	label = bpy.props.StringProperty(name='Inventory Label')
	items = bpy.props.CollectionProperty(type=IE_Item, name='Items')
		
class CE_asset_properties(bpy.types.PropertyGroup):
	""" Properyt group for assets """
	label = bpy.props.StringProperty(default='')
	filepath = bpy.props.StringProperty(default='')
	loaded = bpy.props.BoolProperty(default=False)
	
class CE_interior(bpy.types.Operator):
	""" Creates a new interior cell """
	bl_idname = "scene.ce_interior"
	bl_label = "Interior"
	
	def execute(self, context):
		context.scene.ce_name = 'Untitled Cell'
		context.scene.ce_type = CELL_INTERIOR
		bpy.ops.scene.ce_load_model_dict()
		context.scene.ce_terrain_detail = 0
		
		return {'FINISHED'}

# Not in use
class CE_exterior(bpy.types.Operator):
	""" Creates a new exterior cell """
	bl_idname = "scene.ce_exterior"
	bl_label = "Exterior"
	
	def execute(self, context):
		
		return {'FINISHED'}
	
class CE_load(bpy.types.Operator):
	""" Load an existing cell """
	bl_idname = "scene.ce_load"
	bl_label = "Open"
	bl_description = "Open an existing cell"
	filepath = bpy.props.StringProperty(subtype='FILENAME')
	filepath_ext = ".cell"
	
	@classmethod
	def poll(cls, context):
		return True
		
	def invoke(self, context, event):
		context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}
	
	def execute(self, context):
		global blend_dict, model_dict
		
		bpy.ops.scene.ce_load_model_dict()
		
		# attempt to open .cell file
		try:
			file = open(self.filepath, 'rb')
			cell = pickle.load(file)
			file.close()
		except IOError:
			self.report({'ERROR'}, 'Unable to open file')
			return {'CANCELLED'}
		except (pickle.UnpicklingError, EOFError):
			self.report({'ERROR'}, 'Unable to unpickle .cell file')
			return {'CANCELLED'}
			
		# load props
		for prop_group in cell.props: # props are stored in a 2D array
			for prop in prop_group:
				blend = model_dict[prop.name]
				directory = blend + "/Object/"
				bpy.ops.wm.link_append(directory=directory, filename=prop.name, link=False, instance_groups=False, autoselect=True)
				bpy.ops.object.make_local() # Appending doesn't seem to work, this makes linked objects local
				
				obj = bpy.context.selected_objects[0]
				bpy.ops.object.select_name(name=obj.name) # Make the selected object the active objected
				obj.location = prop.co
				obj.rotation_euler = prop.rotation
				obj.scale = prop.scale
				
				for name, value in prop.properties:
					if name in obj.game.properties:
						# Property exists on object - edit it
						obj.game.properties[name].value = value
					else:
						# Property doesn't exist on object - add it
						bpy.ops.object.game_property_new()
						obj.game.properties[len(obj.game.properties)-1].name = name
						if isinstance(value, float):
							obj.game.properties[name].type = 'FLOAT'
						elif isinstance(value, int):
							obj.game.properties[name].type = 'INT'
						elif isinstance(value, str):
							obj.game.properties[name].type = 'STRING'
						obj.game.properties[name].value = value
						
		# load entities
		for entity in cell.entities:
			blend = model_dict[entity.name]
			directory = blend + "/Object/"
			bpy.ops.wm.link_append(directory=directory, filename=entity.name, link=False, instance_groups=False, autoselect=True)
			bpy.ops.object.make_local() # Make object local
			
			obj = bpy.context.selected_objects[0]
			bpy.ops.object.select_name(name=obj.name) # Make object active
			obj.location = entity.co
			obj.rotation_euler = entity.rotation
			obj.scale = entity.scale
			
			for name, value in entity.properties:
				if name in obj.game.properties:
					# Property exists on object - edit it
					if name == 'inventory':
						# property is an inventory - add the inventory
						# and set the property value to the inventory id
						obj.game.properties[name].value = value.name
						context.scene.ie_inventories.add()
						inventory = context.scene.ie_inventories[-1]
						inventory.name = value.id
						inventory.label = value.name
						for id, stacks in value.items:
							inventory.items.add()
							inventory.items[-1].name = id
							inventory.items[-1].count = stack
					
					else:
						obj.game.properties[name].value = value
				else:
					# Property doesn't exist on object - add it
					bpy.ops.object.game_property_new()
					obj.game.properties[len(obj.game.properties)-1].name = name
					if name == 'inventory':
						# inventories need to be handled seperately
						obj.game.properties[name].type = 'STRING'
						obj.game.properties[name].value = value.name
						context.scene.ie_inventories.add()
						inventory = context.scene.ie_inventories[-1]
						inventory.name = value.id
						inventoy.label = value.name
						for id, stacks in value.items.items():
							count = sum(stacks)
							inventory.items.add()
							inventory.items[-1].name = id
							inventory.items[-1].amount = count
					else:
						if isinstance(value, float):
							obj.game.properties[name].type = 'FLOAT'
						elif isinstance(value, int):
							obj.game.properties[name].type = 'INT'
						elif isinstance(value, str):
							obj.game.properties[name].type = 'STRING'
						obj.game.properties[name].value = value
				
		# load destinations
		for destination in cell.destinations.values():
			blend = model_dict['destination']
			directory = blend + "/Object/"
			bpy.ops.wm.link_append(directory=directory, filename='destination', link=False, instance_groups=False, autoselect=True)
			bpy.ops.object.make_local()
			
			obj = bpy.context.selected_objects[0]
			obj.location = destination.co
			obj.rotation_mode = 'QUATERNION'
			obj.rotation_quaternion = destination.rotation
			obj.game.properties['id'].value = destination.id
		
		# TODO - load lights
		
		# load cell properties
		context.scene.ce_name = cell.name
		context.scene.ce_type = CELL_INTERIOR
		context.scene.ce_bloom = cell.fx['Bloom']
		context.scene.ce_hdr = cell.fx['HDR']
		context.scene.ce_tint = cell.fx['CC']
		context.scene.ce_tint_color = [cell.fx['Color R'],
										cell.fx['Color G'],
										cell.fx['Color B']]
		context.scene.ce_terrain = cell.terrain is not None
		if context.scene.ce_terrain:
			context.scene.ce_terrain_file = cell.terrain
			
		context.scene.ce_terrain_detail = 0
		
		return {'FINISHED'}
	
class CE_close(bpy.types.Operator):
	bl_idname = "scene.ce_close"
	bl_label = "Close"
	
	def execute(self, context):
		context.scene.ce_type = CELL_NONE
		context.scene.ce_name = 'Untitled Cell'
		context.scene.ce_terrain = False
		context.scene.ce_hdr = False
		context.scene.ce_bloom = False
		context.scene.ce_tint = False
		context.scene.ce_terrain_file = ''
		return {'FINISHED'}
	
class CE_bake(bpy.types.Operator):
	bl_idname = "scene.ce_bake"
	bl_label = "Bake"
	bl_description = "Bake the selected objects to the cell"
	filepath = bpy.props.StringProperty(subtype='FILENAME')
	filepath_ext = ".cell"
	
	@classmethod
	def poll(cls, context):
		return True
	
	def invoke(self, context, event):
		context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}
	
	def execute(self, context):
		global blend_dict, inventory
		known_models = []
		for assets in blend_dict.values():
			known_models.extend(assets)
		
		lamps = []
		entities = []
		props = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
		destinations = {}
		
		for obj in bpy.data.objects:
			if obj.name == 'CE_terrain':
				continue
			
			if obj.type in ['MESH', 'EMPTY', 'ARMATURE'] and not obj.parent:
				name = re.sub("(\\.)(\\d){3,100}($)", "", obj.name) # remove .001 from name

				size = max(*obj.dimensions[:])
				if size == 0:
					# Give objects with no size a default value
					size = 10
					
				properties = {}
				for property in obj.game.properties:
					properties[property.name] = property.value
				
				if name == 'destination':
					print('[destination]', name)
					# object is a destination
					old_rot = obj.rotation_mode
					obj.rotation_mode = 'QUATERNION'
					destinations[properties['id']] = Destination(properties['id'], obj.location[:], obj.rotation_quaternion[:])
					obj.rotation_mode = old_rot
					
				elif obj.game.physics_type in ['RIGID_BODY', 'DYNAMIC'] or 'entity' in properties:
					# object is an entity
					print('[entity]', name)
					class_ = 'EntityBase'
					if 'entity' in properties:
						class_ = properties['entity']
						
					if 'inventory' in properties:
						# Switch the iventory id to an inventory object
						inv = Inventory()
						id = properties['inventory']
						
						for inventory in context.scene.ie_inventories:
							if inventory.name == id:
								inv.id = id
								inv.name = inventory.label
								for item in inventory.items:
									inv.add_item(item.name, item.amount)
								break
						
						properties['inventory'] = inv
						
					entities.append(Entity(name, obj.location[:], obj.scale[:], obj.dimensions[:], obj.rotation_euler[:], list(properties.items()), class_))
					
				else:
					# object is a prop
					print('[prop]', name)
					i = math.floor(math.log(size, 2))
					if i < 0: #JP safeguard, small objects were ending up in the [-1] slot
						i = 0
					if name not in known_models:
						print(['wtf'], name)
						name = "WTF" # yes this is actually important
					
					props[i].append(Prop(name, obj.location[:], obj.scale[:], obj.dimensions[:], obj.rotation_euler[:], i, list(properties.items())))
				
			elif obj.type == 'LAMP':
				# object is a light
				print('[lamp]', name)
				lamp = bpy.data.lamps[obj.name]
				if lamp.type == 'SPOT':
					lamps.append(Lamp(name, obj.location[:], obj.rotation_euler[:], lamp.type, lamp.color[:], lamp.distance, \
						lamp.energy, spot_size=lamp.spot_size, spot_blend=lamp.spot_blend, spot_bias=lamp.shadow_buffer_bias) )
					
				elif lamp.type == 'POINT':
					lamps.append(Lamp(name, obj.location[:], obj.rotation_euler[:], lamp.type, lamp.color[:], lamp.distance, lamp.energy))
		for l in props:
			print("### "+str(len(l)))
		
		# FX settings
		FX = {}
		FX['Bloom'] = bpy.context.scene.ce_bloom
		FX['HDR'] = bpy.context.scene.ce_hdr
		FX['CC'] = bpy.context.scene.ce_tint

		FX['Color R'] = bpy.context.scene.ce_tint_color[0]
		FX['Color B'] = bpy.context.scene.ce_tint_color[1]
		FX['Color G'] = bpy.context.scene.ce_tint_color[2]
		
		newcell = Cell()
		newcell.name = bpy.context.scene.ce_name
		newcell.filename = self.filepath
		newcell.props = props
		newcell.lamps = lamps
		newcell.destinations = destinations
		newcell.fx = FX
		newcell.entities = entities
		if bpy.context.scene.ce_terrain:
			newcell.terrain = bpy.context.scene.ce_terrain_file

		newcell.save()
		return {'FINISHED'}

class CE_index_blends(bpy.types.Operator):
	""" Index .blends in the models dict and bake a model_dict.data """
	bl_idname = "scene.ce_index_blends"
	bl_label = "Index .blends"
	bl_description = "Crawl the model directory and index the .blends"
	
	def execute(self, context):
		global blend_dict, model_dict
		assets = walk_dir(context.scene.ce_asset_dir)
		
		for asset in assets:
			asset = asset.replace("//", "/")
		
		# bake a model dict
		blend_dict = construct_blend_dict(assets)
		model_dict = {}
		for blend, models in blend_dict.items():
			for model in models:
				model_dict[model] = blend
		file = open('./data/model_dict.data', 'wb')
		pickle.dump(model_dict, file)
		file.close()
		
		return {'FINISHED'}
		
class CE_load_model_dict(bpy.types.Operator):
	""" Load model_dict.data """
	bl_idname = "scene.ce_load_model_dict"
	bl_label = "Load Model Dict"
	bl_description = "Refresh the asset list based on the model dict"
	
	def execute(self, context):
		global blend_dict, model_dict
		
		file = open('./data/model_dict.data', 'rb')
		model_dict = pickle.load(file)
		file.close()
		
		blend_dict = {}
		for model, blend in model_dict.items():
			if blend not in blend_dict:
				blend_dict[blend] = []
				
			blend_dict[blend].append(model)
		
		ce_assets = context.scene.ce_assets
		for i in range(len(ce_assets)):
			ce_assets.remove(0)
			
		for file in sorted(blend_dict.keys(), key = lambda s: s[s.rindex('/'):].lower()):
			if file.endswith('.blend'):
				ce_assets.add()
				ce_assets[-1].label = file[file.rindex('/')+1:]
				ce_assets[-1].filepath = file
				ce_assets[-1].loaded = False
		
		return {'FINISHED'}
	
class CE_load_lib(bpy.types.Operator):
	""" Link a .blend into the editor """
	bl_idname = "scene.ce_load_lib"
	bl_label = "Load Library"
	bl_description = "Load the current libraries contents"
	
	asset = bpy.props.IntProperty()
	
	def invoke(self, context, event):
		filepath = context.scene.ce_assets[self.asset].filepath
		directory = context.scene.ce_assets[self.asset].filepath + "/Object/"
		
		for asset in blend_dict[filepath]:
			bpy.ops.wm.link_append(directory=directory, filename=asset, link=False, instance_groups=False, autoselect=True)
			bpy.ops.object.make_local()
			
		context.scene.ce_assets[self.asset].loaded = True
		return {'FINISHED'}

# Doesn't really do anything
class CE_free_lib(bpy.types.Operator):
	""" Remove a .blend from the editor """
	bl_idname = "scene.ce_free_lib"
	bl_label = "Load Library"
	bl_description = "Load the current libraries contents"
	
	asset = bpy.props.IntProperty()
	
	def invoke(self, context, event):
		context.scene.ce_assets[self.asset].loaded = False
		return {'FINISHED'}   
	
class CE_terrain_select(bpy.types.Operator):
	""" Open a file dialogue and choose a .terrain file """
	bl_idname = "scene.ce_terrain_select"
	bl_label = "Select Terrain"
	bl_description = "Select terrain file"
	filepath = bpy.props.StringProperty(subtype='FILENAME')
	filepath_ext = ".terrain"
	
	@classmethod
	def poll(cls, context):
		return True
	
	def invoke(self, context, event):
		context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}
	
	def execute(self, context):
		global map
		context.scene.ce_terrain_file = self.filepath.split('\\')[-1] #JP keeping this just the file name not the local path
		
		file = open(self.filepath, 'rb')
		map = pickle.load(file)
		file.close()
		
		if 'CE_terrain' in context.scene.objects:
			pass
		else:
			mesh = bpy.data.meshes.new('CE_terrain')
			obj = bpy.data.objects.new('CE_terrain', mesh)
			
			verts = []
			x = 0
			y = 0
			while (x < map.width):
				while (y < map.height):
					verts.append([x, y, map.buffer[x*map.height + y]])
					y += 16
				y = 0
				x += 16
				
			obj.data.from_pydata(verts, [], [])
			obj.data.update()
			context.scene.objects.link(obj)
			
		print(map.width, map.height, len(map.buffer))
		return {'FINISHED'}
	
class CE_terrain_increase(bpy.types.Operator):
	""" Increase the level of detail for the terrain perview """
	bl_idname = 'scene.ce_terrain_increase'
	bl_label = 'Increase detail'
	bl_description = 'Increase terrain detail level'
	
	@classmethod
	def poll(cls, context):
		return context.scene.ce_terrain and context.scene.ce_terrain_detail < 3
		
	def execute(self, context):
		context.scene.ce_terrain_detail += 1
		return{'FINISHED'}
		
class CE_terrain_decrease(bpy.types.Operator):
	""" Decrease the level of detail for the terrain perview """
	bl_idname = 'scene.ce_terrain_decrease'
	bl_label = 'Decrease detail'
	bl_description = 'Decrease terrain detail level'
	
	@classmethod
	def poll(cls, context):
		return context.scene.ce_terrain and context.scene.ce_terrain_detail > 0
		
	def execute(self, context):
		context.scene.ce_terrain_detail -= 1
		return{'FINISHED'}

class CE_type_menu(bpy.types.Menu):
	""" Menu for selecting whether to create an interior or exterior cell """
	bl_label = "Cell Type"
	
	def draw(self, context):
		layout = self.layout
		
		layout.operator("scene.ce_interior")
		layout.operator("scene.ce_exterior")
	
class IE_inv_add(bpy.types.Operator):
	""" Add a new inventory """
	bl_idname = "scene.ie_inv_add"
	bl_label = "New"
	bl_description = "Add a new inventory"
	
	def execute(self, context):
		context.scene.ie_inventories.add()
		context.scene.ie_inventories[-1].name = 'Inventory'
		context.scene.ie_inventory_index = len(context.scene.ie_inventories)-2
		
		return {'FINISHED'}

class IE_inv_del(bpy.types.Operator):
	""" Delete the current inventory """
	bl_idname = "scene.ie_inv_del"
	bl_label = "Delete"
	bl_description = "Delete the selected inventory"
	
	def execute(self, context):
		context.scene.ie_inventories.remove(context.scene.ie_inventory_index)
		
		return {'FINISHED'}
		
class IE_item_add(bpy.types.Operator):
	""" Add a new item to the current inventory """
	bl_idname = "scene.ie_item_add"
	bl_label = "Add item"
	bl_description = "Add a new item"
	
	def execute(self, context):
		inventory = context.scene.ie_inventories[context.scene.ie_inventory_index]
		inventory.items.add()
		inventory.items[-1].name = ''
		
		return {'FINISHED'}

class IE_item_del(bpy.types.Operator):
	""" Delete an item """
	bl_idname = "scene.ie_item_del"
	bl_label = "Delete"
	bl_description = "Delete the selected item"
	index = bpy.props.IntProperty()
	
	def execute(self, context):
		inventory = context.scene.ie_inventories[context.scene.ie_inventory_index]
		inventory.items.remove(self.index)
		
		return {'FINISHED'}

class SCENE_PT_cell_editor(bpy.types.Panel):
	bl_label = "Cell Editor"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "scene"
	
	def draw(self, context):
		layout = self.layout
		#row = layout.row(align=True)
		#row.prop(context.scene, "ce_nt_root")
		#row.operator('scene.ce_root_select', icon='FILESEL')
		
		if context.scene.ce_type == CELL_NONE:
			row = layout.row()
			
			row.menu("CE_type_menu", text="New Cell")
			row.operator("scene.ce_load", icon="FILESEL")
		else:
			layout.row(align=True).prop(context.scene, "ce_mode", expand=True)
			if context.scene.ce_type == CELL_INTERIOR:
				if context.scene.ce_mode == MODE_EDIT:
					box = layout.box()
					
					box.row().prop(context.scene, "ce_name")
					
					row = box.row()
					row.prop(context.scene, 'ce_terrain')
					row.prop(context.scene, 'ce_hdr')
					row.prop(context.scene, 'ce_bloom')
					row.prop(context.scene, 'ce_tint')
					if bpy.context.scene.ce_terrain:
						row = box.row(align=True)
						row.prop(context.scene, 'ce_terrain_file')
						row.operator('scene.ce_terrain_select', icon='FILESEL', text="")
						row.operator('scene.ce_terrain_decrease', icon='BACK', text='')
						row.operator('scene.ce_terrain_increase', icon='FORWARD', text='')
					if bpy.context.scene.ce_tint:
						box.row().prop(context.scene, 'ce_tint_color')
					
					row = box.row()
					row.operator("scene.ce_bake", icon="DISK_DRIVE")
					row.operator("scene.ce_close", icon="PANEL_CLOSE")
					
					
					
				elif context.scene.ce_mode == MODE_MANAGE:
					box = layout.box()
					row = box.row(align=True)
					row.prop(context.scene, 'ce_asset_dir')
					row.operator("scene.ce_index_blends", text='', icon='FILE_REFRESH')
					
					row = box.row()
					split = row.split(percentage=0.5)
					colA = split.column()
					colB = split.column()
					for id, asset in enumerate(context.scene.ce_assets):
						
						if asset.loaded:
							row = colB.row()
							row.operator("scene.ce_free_lib", text='', icon='LINKED').asset = id
							row.label(asset.label)
						else:
							row = colA.row()
							row.label(asset.label)
							row.operator("scene.ce_load_lib", text='', icon='UNLINKED').asset = id
				
				elif context.scene.ce_mode == MODE_IE:
					box = layout.box()
					row = box.row()
					row.template_list(context.scene, 'ie_inventories', context.scene, 'ie_inventory_index', rows=3, maxrows=3)
					col = row.column(align=True)
					col.operator('scene.ie_inv_add', icon='ZOOMIN', text='')
					col.operator('scene.ie_inv_del', icon='ZOOMOUT', text='')
					
					if len(context.scene.ie_inventories) != 0:
						inventory = context.scene.ie_inventories[context.scene.ie_inventory_index]
						
						box.row().prop(inventory, 'name', text='ID')
						box.row().prop(inventory, 'label', text='Name')
						box.row().separator()
						box.row().operator('scene.ie_item_add', icon='ZOOMIN')
						for n in range(len(inventory.items)):
							item = inventory.items[n]
							box2 = box.box()
							row = box2.row()
							row.prop(item, 'name', text='')
							row.prop(item, 'amount', text='')
							row.operator('scene.ie_item_del', icon='X', text='', emboss=False).index = n
						
				
				elif context.scene.ce_mode == MODE_HELP:
					box = layout.box()
					
					box.row().label("Refresh assets on opening of cell editor")
				
			elif cell_type == CELL_EXTERIOR:
				layout.label("TODO")
		
def register():
	bpy.utils.register_module(__name__)
	init()
	
	
def unregister():
	bpy.utils.unregister_module(__name__)
	
if __name__ == "__main__":
	register()