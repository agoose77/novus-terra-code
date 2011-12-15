import bpy

import bpy


import sys

# So we can find the bgui module
sys.path.append('./src/')
sys.path.append('./data/terrains/')

import bpy as bpy
import terrain





terrain.tr_singleton = terrain.Map_Manager()



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

# Old still need?
bpy.types.Scene.mychosenScene = bpy.props.StringProperty()
bpy.types.Scene.mychosenScene = bpy.props.StringProperty()

bpy.types.Scene.mychosenScene2 = bpy.props.StringProperty()
bpy.types.Scene.mychosenScene3 = bpy.props.StringProperty()


###############################
### Create all variables - Operator
def create_vars():

	import variables
	args1 = variables.creater_vars()
	args2 = variables.world_vars()
	args3 = variables.bake_vars()

	com = [args1, args2, args3]

	### Reset the property
	for each in bpy.context.scene.myCollection:
		bpy.context.scene.myCollection.remove(0)

	###
	for args in com:
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

			print (a)
			print (args[a])



class te_3(bpy.types.Operator):

	'''Tooltip'''

	bl_idname = "scene.createvars"
	bl_label = "INIT Vars"

	def execute(self, context):
		create_vars()
		return {'FINISHED'}

def register():
	bpy.utils.register_class(te_3)

def unregister():
	bpy.utils.unregister_class(te_3)

register()


###############################
def CreateMeshUsingMatrix(VertIndices, Verts):

	Faces = []
	dims = len(VertIndices)

	# going to use current row and next row all the way down
	for row in range(dims-1):
		#now take row and row+1
		for col in range(dims-1):
			#we generate faces clockwise from 4 Verts
			val1 = VertIndices[row][col]
			val2 = VertIndices[row][col+1]
			val3 = VertIndices[row+1][col+1]
			val4 = VertIndices[row+1][col]
			face = [val1, val2, val3, val4]
			Faces.append(face)


	## TAKEN FROM USER  ValterVB
	# create new mesh structure
	name = str(terrain.focus)[1:]
	mesh = bpy.data.meshes.new(name)
	mesh.from_pydata(Verts, [], Faces)



	mesh.update()

	print(dir(mesh.vertices[0]))
	# create an object from this mesh
	new_object = bpy.data.objects.new(name, mesh)
	new_object.data = mesh

	d = terrain.focus
	x,y = d[0], d[1]
	new_object.location = [x, y,0]


	terrain.current = new_object
	# adding object called "Ascii Data" to the scene
	scene = bpy.context.scene
	scene.objects.link(new_object)
	# deals with selecting
	scene.objects.active = new_object

	new_object.select = True

	bpy.ops.uv.follow_active_quads(  mode='EVEN')
	print(dir(bpy.data.meshes[0]))
	edit_mode = True
	bpy.ops.object.editmode_toggle()
	bpy.ops.mesh.faces_shade_smooth()
	bpy.ops.mesh.flip_normals()


	obj = new_object
	mesh = obj.data

	is_editmode = (obj.mode == 'EDIT')
	if is_editmode:
		bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

	if not mesh.uv_textures:
		uvtex = bpy.ops.mesh.uv_texture_add()
	else:
		uvtex = mesh.uv_textures.active

	# adjust UVs
	for i, uv in enumerate(uvtex.data):
		uvs = uv.uv1, uv.uv2, uv.uv3, uv.uv4
		for j, v_idx in enumerate(mesh.faces[i].vertices):

			# apply the location of the vertex as a UV
			sc = 1/float(terrain.tr_singleton.map.width)
			x = terrain.focus[0]*sc+.5
			y = terrain.focus[1]*sc+.5
			v = mesh.vertices[v_idx].co.xy
			v = v * sc
			v[0] += x
			v[1] += y
			uvs[j][:] = v

	bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

	#bpy.ops.uv.select_all('SELECT')
	## / TAKEN FROM USER

##############################
def startASCIIimport(data):

	VertIndices = []
	heightMatrix = []

	#needs to pull data from readRect

	for i in range(len(data)):
		heightMatrix.append(data[i])


	# this supposes that X, Y separation are going to be the same.
	xy_val = []
	for i in range(len(data)):
		xy_val.append(i)

	# Generates the (x,y,height) matrix, no need for Vector(...)
	yVal = 0
	vertNum = 0
	rawVertCollection = []
	for height_x in heightMatrix:
		xVal = 0
		vertRow = []
		for item in height_x:
			t_vertice = (xy_val[xVal], -xy_val[yVal], heightMatrix[yVal][xVal]*.1)
			rawVertCollection.append(t_vertice)

			vertRow.append(vertNum)
			xVal+=1
			vertNum+=1
		yVal+=1
		VertIndices.append(vertRow)

	# done here, lets make a mesh!
	CreateMeshUsingMatrix(VertIndices, rawVertCollection)

###############################
### Operator
def display_section():


	loc = [bpy.context.scene.myCollection2['x'].int,bpy.context.scene.myCollection2['y'].int]
	size = bpy.context.scene.myCollection2['size'].int
	#now organize this so it's giving top left and bottom right corners
	focus = []

	focus.append(loc[0]-int(size/2))
	focus.append(loc[1]+int(size/2))
	focus.append(loc[0]+int(size/2))
	focus.append(loc[1]-int(size/2))
	terrain.focus = focus
	p = focus

	data = terrain.tr_singleton.readRect_addon(p[0],p[1],p[2],p[3])


	startASCIIimport(data)


	print ('Section created.')

###############################
def new_terrain():
	name=bpy.context.scene.myCollection2['filename'].string
	width=bpy.context.scene.myCollection2['width'].int
	height=bpy.context.scene.myCollection2['height'].int
	terrain.tr_singleton.new(width,height, "./data/terrains/"+name, .1)

def load_terrain():
	name=bpy.context.scene.myCollection2['filename'].string
	terrain.tr_singleton.load("./data/terrains/"+name)

def create_texture():
	if 'Terrain' not in bpy.data.materials.keys():
		bpy.data.materials.new('Terrain')
	mat = bpy.data.materials['Terrain']
	bpy.context.active_object.active_material = bpy.data.materials['Terrain']
	newtex = bpy.data.textures.new('terrain_image','IMAGE')


	mtex = mat.texture_slots.add()
	mtex.texture = newtex
	mtex.texture_coords = 'UV'
	print(dir(mtex))

###############################
### Main World Baker here - Operator
def bake_world():
	d = terrain.current.data

	d.vertices[0].select = True


	height = []
	normals = []
	for v in d.vertices:
		height.append( int(v.co[2]*(1/terrain.tr_singleton.map.scale)) )

		tt = []
		for i in range(3):
			tt.append( int(v.normal[i]*127) )
		normals.append( tt )


	data = [height, normals]
	terrain.tr_singleton.writeRect(data, terrain.focus[0],terrain.focus[1],
									terrain.focus[2],terrain.focus[3] )

def save_normals():
	terrain.tr_singleton.save_normal_list( terrain.tr_singleton.filename[:-8]+"_norms.txt")

###############################

class te_3(bpy.types.Operator):

	'''Creates a blank terrain object.'''

	bl_idname = "scene.new_terrain"
	bl_label = "New Terrain"

	def execute(self, context):
		new_terrain()
		return {'FINISHED'}

def register():
	bpy.utils.register_class(te_3)

def unregister():
	bpy.utils.unregister_class(te_3)

register()

class te_3(bpy.types.Operator):

	'''Loads a terrain from ./data/terrains/'''

	bl_idname = "scene.load_terrain"
	bl_label = "Load Terrain"

	def execute(self, context):
		load_terrain()
		return {'FINISHED'}

def register():
	bpy.utils.register_class(te_3)

def unregister():
	bpy.utils.unregister_class(te_3)

register()


class te_3(bpy.types.Operator):

	'''enter the coordinates of the terrain section you would like to edit.'''

	bl_idname = "scene.display_section"
	bl_label = "Display Section"

	def execute(self, context):
		display_section()
		return {'FINISHED'}

def register():
	bpy.utils.register_class(te_3)

def unregister():
	bpy.utils.unregister_class(te_3)

register()



class te_3(bpy.types.Operator):

	'''Saves changes to the current displayed section.'''

	bl_idname = "scene.bakeworld"
	bl_label = "Bake World"

	def execute(self, context):
		bake_world()
		return {'FINISHED'}

def register():
	bpy.utils.register_class(te_3)

def unregister():
	bpy.utils.unregister_class(te_3)

register()


class te_3(bpy.types.Operator):

	'''Save a text file, used with seperate script to create normal map image.'''

	bl_idname = "scene.save_norms"
	bl_label = "Save Normals"

	def execute(self, context):
		save_normals()
		return {'FINISHED'}

def register():
	bpy.utils.register_class(te_3)

def unregister():
	bpy.utils.unregister_class(te_3)

register()


class te_3(bpy.types.Operator):

	'''Creates a texture for the active object's first material.'''

	bl_idname = "scene.newtexture"
	bl_label = "New Texture"

	def execute(self, context):
		create_texture()
		return {'FINISHED'}

def register():
	bpy.utils.register_class(te_3)

def unregister():
	bpy.utils.unregister_class(te_3)

register()


### Panel
class OBJECT_PT_terrain_editor(bpy.types.Panel):
	bl_label = "World Manager - v0.0"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "scene"

	def draw(self, context):
		layout = self.layout

		obj = context.object

		row = layout.row()
		row.operator("scene.createvars")

		###
		box = layout.box()
		row = box.row()
		split = row.split(percentage=0.4)
		colL = split.column()
		colR = split.column()

		colL.label('Create New Terrain:')
		colR.operator("scene.new_terrain")

		colL.label('Load Terrain:')
		colR.operator("scene.load_terrain")

		row = box.row()
		row.prop

		###
		import variables
		args = variables.creater_vars()


		for arg in args:
			prop = bpy.context.scene.myCollection2[arg]

			row = box.row()

			split = row.split(percentage=0.4)
			colL = split.column()
			colR = split.column()

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

		colL.label('Display Section:')
		colR.operator("scene.display_section")

		###
		import variables
		args = variables.world_vars()


		for arg in args:
			prop = bpy.context.scene.myCollection2[arg]

			row = box.row()

			split = row.split(percentage=0.4)
			colL = split.column()
			colR = split.column()

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

		colL.label('Bake World:')
		colR.operator("scene.bakeworld")

		colL.label('Save Normals as text:')
		colR.operator("scene.save_norms")

		###
		import variables
		args = variables.bake_vars()


		for arg in args:
			prop = bpy.context.scene.myCollection2[arg]

			row = box.row()

			split = row.split(percentage=0.4)
			colL = split.column()
			colR = split.column()

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

		colL.label('New Texture:')
		colR.operator("scene.newtexture")

		###




def register():
	bpy.utils.register_class(OBJECT_PT_terrain_editor)


def unregister():
	bpy.utils.unregister_class(OBJECT_PT_terrain_editor)


if __name__ == "__main__":
	register()