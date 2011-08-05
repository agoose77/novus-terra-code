bl_info = {
	"name": "cell editor",
	"author": "joe@designisgood.com",
	"version": (1, 0),
	"blender": (2, 5, 5),
	"api": 33333,
	"location": "Properties > Scene > Cell Editor",
	"description": "Tool to bake .cell files for Novus Terra",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"category": "Add Mesh"}

import sys
sys.path.append('./src/')

import bpy
import cell
from cell.cell_manager import Prop, Lamp, Cell

def bake_cell():
	
	props, lamps = [], []
	print(bpy.data.objects)
	print(bpy.context.scene.objects)
	for object in bpy.data.objects:
		split_name = object.name.split(".")[0]
		if object.type in ["MESH", "EMPTY"]:
			props.append( Prop( split_name, list(object.location), list(object.scale), 
									list(object.dimensions), list(object.rotation_euler)) )
		elif object.type in ["LAMP"]:
			
			lamp = bpy.data.lamps[object.name]
			lamps.append( Lamp(split_name, list(object.location), list(object.rotation_euler), 
								lamp.type, list(lamp.color), lamp.distance, lamp.energy) )
	newcell = Cell()
	newcell.props = props
	newcell.lamps = lamps
	filename=bpy.context.scene.myCollection2['filename'].string
	newcell.save(filename)
### Arguments
args = {
	
		'filename':'new.cell',
	}


### Operator

class te_3(bpy.types.Operator):
	
	'''Bake a .cell file from scene.'''
	
	bl_idname = "scene.bakecell"
	bl_label = "Bake Cell"

	def execute(self, context):
		bake_cell()   
		return {'FINISHED'}

def register():
	bpy.utils.register_class(te_3)

def unregister():
	bpy.utils.unregister_class(te_3)

register()

### Panel

class OBJECT_PT_hello(bpy.types.Panel):
	bl_label = "Cell Editor - v0.1"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "scene"

	def draw(self, context):
		layout = self.layout

		obj = context.object
		
		###
		box = layout.box()
		row = box.row()
		split = row.split(percentage=0.4)
		colL = split.column()
		colR = split.column()

		row.operator("scene.bakecell")

		for arg in args:
			prop = bpy.context.scene.myCollection2[arg]
				   
			
			colL.label(str(arg)+':')
		
			if isinstance(args[arg], float) == True:
				colR.prop(prop, "float", text='')
								
			elif isinstance(args[arg], bool) == True:
				colR.prop(prop, "bool", text='')
				
			elif isinstance(args[arg], int) == True:
				colR.prop(prop, "int", text='')
				
			elif isinstance(args[arg], str) == True:
				colR.prop(prop, "string", text='')

def register():
	bpy.utils.register_class(OBJECT_PT_hello)


def unregister():
	bpy.utils.unregister_class(OBJECT_PT_hello)

### Property group

### Properties
class PropertyGroup(bpy.types.PropertyGroup):
	pass
bpy.utils.register_class(PropertyGroup)


###
bpy.types.Scene.myCollection = bpy.props.CollectionProperty(type = PropertyGroup)
bpy.types.Scene.myCollection_index = bpy.props.IntProperty(min = -1, default = -1)

bpy.types.Scene.myCollection2 = bpy.props.CollectionProperty(type = PropertyGroup)
bpy.types.Scene.myCollection2_index = bpy.props.IntProperty(min = -1, default = -1)

##
PropertyGroup.int = bpy.props.IntProperty()
PropertyGroup.float = bpy.props.FloatProperty()
PropertyGroup.bool = bpy.props.BoolProperty(default = False)
PropertyGroup.string = bpy.props.StringProperty()


###############################
### Create all variables - Operator
def create_vars():
	
	### Reset the property
	for each in bpy.context.scene.myCollection:
		bpy.context.scene.myCollection.remove(0)	
	
			
	for a in args:
			
		add = bpy.props.StringProperty(default = 'Default')		 
		bpy.context.scene.myCollection2.add()		   
			
		### Float
		if isinstance(args[a], float) == True:
			bpy.context.scene.myCollection2[len(bpy.context.scene.myCollection2)-1].name = str(a)
			bpy.context.scene.myCollection2[len(bpy.context.scene.myCollection2)-1].float = args[a]
			
		### Int
		if isinstance(args[a], int) == True:
			bpy.context.scene.myCollection2[len(bpy.context.scene.myCollection2)-1].name = str(a)
			bpy.context.scene.myCollection2[len(bpy.context.scene.myCollection2)-1].int = args[a]
				
		### String
		if isinstance(args[a], str) == True:
			bpy.context.scene.myCollection2[len(bpy.context.scene.myCollection2)-1].name = str(a)
			bpy.context.scene.myCollection2[len(bpy.context.scene.myCollection2)-1].string = args[a]
				
		### Bool
		if isinstance(args[a], bool) == True:
			bpy.context.scene.myCollection2[len(bpy.context.scene.myCollection2)-1].name = str(a)
			bpy.context.scene.myCollection2[len(bpy.context.scene.myCollection2)-1].bool = args[a]
				


if __name__ == "__main__":
	create_vars()
	register()