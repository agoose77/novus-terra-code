bl_info = {
	"name": "Novus Terra - Item Editor",
	"author": "Andrew Bentley",
	"version": (0, 5, 0),
	"blender": (2, 6, 0.1),
	"api": 41226,
	"location": "Scene Panel",
	"description": "Create items for use in Novus Terra",
	"catergory": "Game Engine"}

import pickle

import bpy


def init():
	bpy.types.Scene.ie_items_path = bpy.props.StringProperty(name='Path to item.data', default='./data/items.data')

	bpy.types.Scene.ie_items = bpy.props.CollectionProperty(type=IE_Item)
	bpy.types.Scene.ie_item_index = bpy.props.IntProperty()


class IE_Property(bpy.types.PropertyGroup):
	name = bpy.props.StringProperty(name='Name', default='')
	value = bpy.props.StringProperty(name='Value', default='')


class IE_Item(bpy.types.PropertyGroup):
	name = bpy.props.StringProperty(name='ID',
		description='Unique identifer for referring back to the item',
		default='new_item')  # ID
	name2 = bpy.props.StringProperty(name='Name')  # Name
	type = bpy.props.EnumProperty(name='Type',
		items=(
			('consumeables', 'Consumeable', ''),
			('weapons', 'Weapon', ''),
			('ammo', 'Ammo', ''),
			('misc', 'Misc', '')
		),
		default='consumeables')

	description = bpy.props.StringProperty(name='Description')

	cost = bpy.props.IntProperty(name='Cost', min=0)
	size = bpy.props.IntVectorProperty(name='Size', default=(1, 1), min=1, size=2)
	stack = bpy.props.IntProperty(name='Stack Size', min=0)
	icon = bpy.props.StringProperty(name='Icon')

	properties = bpy.props.CollectionProperty(type=IE_Property)


class IE_open_db(bpy.types.Operator):
	bl_idname = 'scene.ie_open_db'
	bl_label = 'Open Items'

	def execute(self, context):
		# remove all items
		for i in range(len(context.scene.ie_items)):
			context.scene.ie_items.remove(-1)

		# load items in alphebetical order
		file = open(context.scene.ie_items_path, 'rb')
		items = pickle.load(file)
		file.close()

		items = sorted(items, key=lambda item: item[0].lower())

		for item_data in items:
			item = context.scene.ie_items.add()
			item.name = item_data[0]
			item.name2 = item_data[1]
			item.type = item_data[2]
			item.description = item_data[3]
			item.icon = item_data[4]
			item.cost = item_data[5]
			item.size = item_data[6]
			item.stack = item_data[7]

			for name, value in item_data[8].items():
				prop = item.properties.add()
				prop.name = name
				prop.value = value

		return {'FINISHED'}


class IE_save_db(bpy.types.Operator):
	bl_idname = 'scene.ie_save_db'
	bl_label = 'Save Items'

	def execute(self, context):
		items = []
		for item in context.scene.ie_items:
			properties = {}
			for prop in item.properties:
				properties[prop.name] = prop.value

			items.append((item.name, item.name2, item.type,
						item.description, item.icon, item.cost,
						item.size[:], item.stack, properties))

		file = open('./data/items.data', 'wb')
		pickle.dump(items, file)
		file.close()

		return {'FINISHED'}


class IE_add_item(bpy.types.Operator):
	bl_idname = 'scene.ie_add_item'
	bl_label = 'Add Item'

	def execute(self, context):
		item = context.scene.ie_items.add()
		item.name = 'New Item'
		context.scene.ie_item_index = len(context.scene.ie_items) - 1

		return {'FINISHED'}


class IE_del_item(bpy.types.Operator):
	bl_idname = 'scene.ie_del_item'
	bl_label = 'Delete Item'

	def execute(self, context):
		context.scene.ie_items.remove(context.scene.ie_item_index)
		context.scene.ie_item_index = max(0, context.scene.ie_item_index - 1)
		return {'FINISHED'}


class IE_icon_select(bpy.types.Operator):
	bl_idname = "scene.ie_icon_select"
	bl_label = "Select Icon"
	bl_description = "Select icon file"
	filepath = bpy.props.StringProperty(subtype='FILENAME')

	@classmethod
	def poll(cls, context):
		return True

	def invoke(self, context, event):
		context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}

	def execute(self, context):
		context.scene.ie_items[context.scene.ie_item_index].icon = self.filepath.split("\\")[-1]
		return {'FINISHED'}


class a(bpy.types.Operator):
	bl_idname = "scene.ie_add_prop"
	bl_label = "Add Property"

	def execute(self, context):
		context.scene.ie_items[context.scene.ie_item_index].properties.add()
		return {'FINISHED'}


class IE_del_prop(bpy.types.Operator):
	bl_idname = 'scene.ie_del_prop'
	bl_label = 'Delete Property'
	index = bpy.props.IntProperty()

	def execute(self, context):
		context.scene.ie_items[context.scene.ie_item_index].properties.remove(self.index)
		return {'FINISHED'}


class SCENE_PT_item_editor(bpy.types.Panel):
	bl_label = "NT - Item Editor"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "scene"

	def draw(self, context):
		layout = self.layout

		box = layout.box()
		row = box.row(align=True)
		row.prop(context.scene, 'ie_items_path')
		row.operator('scene.ie_open_db', text='', icon='FILE_REFRESH')
		box.row().operator('scene.ie_save_db', text='Bake', icon='DISK_DRIVE')

		row = box.row()
		row.template_list(context.scene, 'ie_items', context.scene, 'ie_item_index', rows=5, maxrows=5)
		col = row.column(align=True)
		col.operator('scene.ie_add_item', icon='ZOOMIN', text='')
		col.operator('scene.ie_del_item', icon='ZOOMOUT', text='')

		if 0 <= context.scene.ie_item_index < len(context.scene.ie_items):
			item = context.scene.ie_items[context.scene.ie_item_index]
			box.prop(item, 'name')
			box.prop(item, 'name2')
			box.prop(item, 'type')
			box.prop(item, 'description')
			row = box.row(align=True)
			row.prop(item, 'icon')
			row.operator('scene.ie_icon_select', icon='FILESEL', text='')
			box.prop(item, 'size')
			box.prop(item, 'cost')
			box.prop(item, 'stack')

			for i, prop in enumerate(item.properties):
				row = box.row()
				row.prop(prop, 'name', text='')
				row.prop(prop, 'value', text='')
				row.operator('scene.ie_del_prop', text='', icon='X').index = i

			box.operator('scene.ie_add_prop', icon='ZOOMIN')


def register():
	bpy.utils.register_module(__name__)
	init()


def unregister():
	bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
	register()
