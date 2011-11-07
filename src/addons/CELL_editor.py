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

import sys, os, pickle
sys.path.append('./src/')

import bpy
import cell
from cell.cell_manager import Prop, Lamp, Cell, Entity

def index_blends(dir, output):
		file_dict = {}
		gen = os.walk(dir)
		for each_tuple in gen:
			if each_tuple[2] != []:

				for filename in each_tuple[2]:
					if filename.endswith('.blend'):
						if each_tuple[0][-2:] != ".\\":
							filename = "/"+filename
						name = each_tuple[0]+filename

						name2 = name.replace("\\", "/")
						name2 = name2.replace("//", "/") #really no clue how this works anymore, it's also slow as shit
						#file_dict[ name2 ] = []
						fo = open(name2, 'rb')
						fd = str(fo.read())
						print("NAME2::",name2)
						while 1:
							if 'OB' in fd:
								derived = ""
								t = 0

								#make sure it's a valid name
								if fd[ fd.index("OB")-2: fd.index("OB")] == "00":
									#print( fd[ fd.index("OB")-4: fd.index("OB")+12 ])
									if fd[ fd.index("OB"): fd.index("OB")+6] != "OBJECT":
										if fd[ fd.index("OB")+2+t ] not in ["\\", " ","?",".",")","("]:

											#it's a valid name, so get it
											while 1:
												if fd[ fd.index("OB")+2+t ] not in ["\\", " "]:


													derived += fd[ fd.index("OB")+2+t ]
												else:
													break
												t += 1
								fd = fd.replace("OB", "$$", 1)
								if derived != "":
									print(derived)
									file_dict[derived] = name2
							else:
								break


		fo = open(output, 'wb')
		pickle.dump(file_dict,fo)
		fo.close()
		return file_dict

def read_model_dict():
	fo = open("./data/model_dict.data", 'rb')
	file_dict = pickle.load(fo)
	fo.close()
	return file_dict

def update_model_dict():
	index_blends("./data/models/", "./data/model_dict.data")

def bake_cell():
	print("## Indexing ./data/models")
	blends = read_model_dict()
	known_objects = []

	###
	for entry in blends:
		if entry not in known_objects:
			known_objects.append(entry)

	"""  OLD -- Model_Dict.data -- Stuff

	for blend in blends:
		for entry in blends[blend]:
			if entry not in known_objects:
				known_objects.append(entry)
				"""

	# sort props for 15 kd-trees for different scales
	props = []
	for i in range(15):
		props.append([])
	lamps = []
	entities = []

	for object in bpy.data.objects:
		split_name = object.name.split(".")[0]
		if object.type in ["MESH", "EMPTY", "ARMATURE"] and not object.parent:

			#check dimesions and sort
			dimensions = object.dimensions
			best = 0
			for entry in dimensions:
				if entry > best:
					best = entry
			if object.type in ["EMPTY","ARMATURE"]: #give these zero size things a dimension
				best = 10

			#sort entities
			if object.game.physics_type in ['RIGID_BODY', 'DYNAMIC']:
				properties = []
				for p in object.game.properties:
					properties.append([p.name, p.value])
				entities.append( Entity( split_name, list(object.location), list(object.scale),
											list(object.dimensions), list(object.rotation_euler), properties) )

			else: #add to props
				for i in range( len(props) ):
					if pow(2, i) > best:
						print("best:",pow(2,i))
						properties = []
						print(object.game.physics_type)

						for p in object.game.properties:
							#properties.append({p.name:p.value})
							properties.append([p.name, p.value])

						if split_name not in known_objects:
							split_name = 'WTF!!' + split_name#"WTF" #yes this is actually important
							print("---------------------" + split_name)
						print(split_name)
						props[i].append( Prop( split_name, list(object.location), list(object.scale),
												list(object.dimensions), list(object.rotation_euler), properties) )
						break


		elif object.type in ["LAMP"]:

			lamp = bpy.data.lamps[object.name]
			if lamp.type == 'SPOT':
				lamps.append( Lamp(split_name, list(object.location), list(object.rotation_euler),
									lamp.type, list(lamp.color), lamp.distance, lamp.energy, spot_size=lamp.spot_size, spot_blend=lamp.spot_blend, spot_bias=lamp.shadow_buffer_bias) )

			elif lamp.type == 'POINT':
				lamps.append( Lamp(split_name, list(object.location), list(object.rotation_euler),
									lamp.type, list(lamp.color), lamp.distance, lamp.energy) )


	### Cell FX Settings
	FX = {}

	FX['Bloom'] = bpy.context.scene.cell_props['Bloom'].float
	FX['HDR'] = bpy.context.scene.cell_props['HDR'].float
	FX['CC'] = bpy.context.scene.cell_props['Color Tint'].float

	FX['Color R'] = bpy.context.scene.cell_props['Color R'].float
	FX['Color B'] = bpy.context.scene.cell_props['Color B'].float
	FX['Color G'] = bpy.context.scene.cell_props['Color G'].float

	newcell = Cell()
	newcell.props = props
	newcell.lamps = lamps
	newcell.fx = FX
	newcell.entities = entities
	print( entities )
	if bpy.context.scene.cell_props['terrain'].bool:
		newcell.terrain = bpy.context.scene.cell_props['terrain file path'].string
	filename=bpy.context.scene.cell_props['cell_filename'].string


	newcell.save(filename)


### Arguments
args = {


		'terrain file path':'./data/terrains/crosscrater.terrain',

		'terrain':False,
		'cell_filename':'./data/cells/new.cell'
	}

fx_args = {

		'HDR':False,
		'Bloom': True,

		'Color Tint':True,
		'Color R': 1.0,
		'Color B': 1.0,
		'Color G': 1.0,
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

class te_3(bpy.types.Operator):

	'''Recreate model_dict.data (Use after you've made changes to .data/models/) *! takes a long time !*'''

	bl_idname = "scene.modeldict"
	bl_label = "Update model_dict"

	def execute(self, context):
		update_model_dict()
		return {'FINISHED'}

def register():
	bpy.utils.register_class(te_3)

def unregister():
	bpy.utils.unregister_class(te_3)

register()


### Panel
class OBJECT_PT_cell_editor(bpy.types.Panel):
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

		box.operator("scene.bakecell")
		box.operator("scene.modeldict")

		for arg in args:
			prop = bpy.context.scene.cell_props[arg]


			colL.label(str(arg)+':')

			if isinstance(args[arg], float) == True:
				colR.prop(prop, "float", text='')

			elif isinstance(args[arg], bool) == True:
				colR.prop(prop, "bool", text='')

			elif isinstance(args[arg], int) == True:
				colR.prop(prop, "int", text='')

			elif isinstance(args[arg], str) == True:
				colR.prop(prop, "string", text='')


		###
		box = layout.box()
		row = box.row()
		split = row.split(percentage=0.4)
		colL = split.column()
		colR = split.column()

		for arg in fx_args:
			prop = bpy.context.scene.cell_props[arg]

			colL.label(str(arg)+':')

			if isinstance(fx_args[arg], float) == True:
				colR.prop(prop, "float", text='')

			elif isinstance(fx_args[arg], bool) == True:
				colR.prop(prop, "bool", text='')

			elif isinstance(fx_args[arg], int) == True:
				colR.prop(prop, "int", text='')

			elif isinstance(fx_args[arg], str) == True:
				colR.prop(prop, "string", text='')


def register():
	bpy.utils.register_class(OBJECT_PT_cell_editor)
def unregister():
	bpy.utils.unregister_class(OBJECT_PT_cell_editor)

### Property group

### Properties
class PropertyGroup(bpy.types.PropertyGroup):
	pass
bpy.utils.register_class(PropertyGroup)


###
#bpy.types.Scene.myCollection = bpy.props.CollectionProperty(type = PropertyGroup)
#bpy.types.Scene.myCollection_index = bpy.props.IntProperty(min = -1, default = -1)

bpy.types.Scene.cell_props = bpy.props.CollectionProperty(type = PropertyGroup)
bpy.types.Scene.cell_props_index = bpy.props.IntProperty(min = -1, default = -1)

###
bpy.types.Scene.cell_FX_props = bpy.props.CollectionProperty(type = PropertyGroup)
bpy.types.Scene.cell_FX_props = bpy.props.IntProperty(min = -1, default = -1)

##
PropertyGroup.int = bpy.props.IntProperty()
PropertyGroup.float = bpy.props.FloatProperty()
PropertyGroup.bool = bpy.props.BoolProperty(default = False)
PropertyGroup.string = bpy.props.StringProperty()


###############################
### Create all variables - Operator
def create_vars():

	### Reset the property
	for each in bpy.context.scene.cell_props:
		bpy.context.scene.cell_props.remove(0)

	arg_list = []
	arg_list.append(args)
	arg_list.append(fx_args)

	for arg in arg_list:
		for a in arg:

			add = bpy.props.StringProperty(default = 'Default')
			bpy.context.scene.cell_props.add()

			### Float
			if isinstance(arg[a], float) == True:
				bpy.context.scene.cell_props[len(bpy.context.scene.cell_props)-1].name = str(a)
				bpy.context.scene.cell_props[len(bpy.context.scene.cell_props)-1].float = arg[a]

			### Int
			if isinstance(arg[a], int) == True:
				bpy.context.scene.cell_props[len(bpy.context.scene.cell_props)-1].name = str(a)
				bpy.context.scene.cell_props[len(bpy.context.scene.cell_props)-1].int = arg[a]

			### String
			if isinstance(arg[a], str) == True:
				bpy.context.scene.cell_props[len(bpy.context.scene.cell_props)-1].name = str(a)
				bpy.context.scene.cell_props[len(bpy.context.scene.cell_props)-1].string = arg[a]

			### Bool
			if isinstance(arg[a], bool) == True:
				bpy.context.scene.cell_props[len(bpy.context.scene.cell_props)-1].name = str(a)
				bpy.context.scene.cell_props[len(bpy.context.scene.cell_props)-1].bool = arg[a]



if __name__ == "__main__":
	create_vars()
	register()