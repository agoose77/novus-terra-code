import bpy, math

from bpy_extras.io_utils import ImportHelper


import sys

# So we can find the bgui module
sys.path.append('./src/')
sys.path.append('./data/terrains/')

import terrain





terrain.tr_singleton = terrain.Map_Manager()




### Properties

args1 = {
	
		'filename':'new.terrain',
		'width':4096,
		'height':4096,
		'scale':1.0
	}

args2 = {
		'x':0,
		'y':0,
		'size':256 
	}
	
args3 = {
		'xyscale':1.0,
		'zscale':1.0
	}

arg_com = [args1, args2, args3]

class PropertyGroup(bpy.types.PropertyGroup):
	pass
bpy.utils.register_class(PropertyGroup)


###
bpy.types.Scene.terrain_props = bpy.props.CollectionProperty(type = PropertyGroup)
bpy.types.Scene.terrain_props_index = bpy.props.IntProperty(min = -1, default = -1)

##
PropertyGroup.int = bpy.props.IntProperty()
PropertyGroup.float = bpy.props.FloatProperty()
PropertyGroup.bool = bpy.props.BoolProperty(default = False)
PropertyGroup.string = bpy.props.StringProperty()


###############################
### Create all variables - Operator
def create_vars():

	### Reset the property
	for each in bpy.context.scene.terrain_props:
		bpy.context.scene.terrain_props.remove(0)


	for args in arg_com:
		for a in args:
	
			add = bpy.props.StringProperty(default = 'Default')
			bpy.context.scene.terrain_props.add()
	
			### Float
			if isinstance(args[a], float) == True:
				bpy.context.scene.terrain_props[len(bpy.context.scene.terrain_props)-1].name = str(a)
				bpy.context.scene.terrain_props[len(bpy.context.scene.terrain_props)-1].float = args[a]
	
			### Int
			if isinstance(args[a], int) == True:
				bpy.context.scene.terrain_props[len(bpy.context.scene.terrain_props)-1].name = str(a)
				bpy.context.scene.terrain_props[len(bpy.context.scene.terrain_props)-1].int = args[a]
	
			### String
			if isinstance(args[a], str) == True:
				bpy.context.scene.terrain_props[len(bpy.context.scene.terrain_props)-1].name = str(a)
				bpy.context.scene.terrain_props[len(bpy.context.scene.terrain_props)-1].string = args[a]
	
			### Bool
			if isinstance(args[a], bool) == True:
				bpy.context.scene.terrain_props[len(bpy.context.scene.terrain_props)-1].name = str(a)
				bpy.context.scene.terrain_props[len(bpy.context.scene.terrain_props)-1].bool = args[a]
	





	

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
	name = 'TERRAIN'
	mesh = bpy.data.meshes.new(name)
	mesh.from_pydata(Verts, [], Faces)



	mesh.update()

	print(dir(mesh.vertices[0]))
	# create an object from this mesh
	new_object = bpy.data.objects.new(name, mesh)
	new_object.data = mesh

	d = terrain.true_focus
	x,y = d[0], d[1]
	new_object.location = [x*terrain.tr_singleton.map.scale, y*terrain.tr_singleton.map.scale,0]


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
			w = terrain.tr_singleton.map.width
			h = terrain.tr_singleton.map.height
			ms = terrain.tr_singleton.map.scale
			# apply the location of the vertex as a UV
			sc = 1/float(w*ms)
			sc2 = 1/float(w)

			x = terrain.true_focus[0]*sc2 + .5
			y = terrain.true_focus[1]*sc2 + .5

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
			t_vertice = (xy_val[xVal]*terrain.tr_singleton.map.scale, 
						-xy_val[yVal]*terrain.tr_singleton.map.scale, 
						heightMatrix[yVal][xVal]*(.01)*terrain.tr_singleton.map.scale)
			rawVertCollection.append(t_vertice)

			vertRow.append(vertNum)
			xVal+=1
			vertNum+=1
		yVal+=1
		VertIndices.append(vertRow)

	# done here, lets make a mesh!
	print( terrain.tr_singleton.map.scale)
	CreateMeshUsingMatrix(VertIndices, rawVertCollection)

###############################
### Operator
def display_section():


	loc = [bpy.context.scene.terrain_props['x'].int,bpy.context.scene.terrain_props['y'].int]
	size = bpy.context.scene.terrain_props['size'].int
	#now organize this so it's giving top left and bottom right corners
	focus = []

	focus.append(loc[0]-int(size/2))
	focus.append(loc[1]+int(size/2))
	focus.append(loc[0]+int(size/2))
	focus.append(loc[1]-int(size/2))
	terrain.focus = focus
	p = focus

	returned = terrain.tr_singleton.readRect_addon(p[0],p[1],p[2],p[3])
	
	data = returned[0]
	offset = returned[1]
	#keeping the section in the right place if it was requesting out of map info
	terrain.true_focus = [ terrain.focus[0],terrain.focus[1] ]
	terrain.focus[0] += offset[0]
	terrain.focus[1] -= offset[1]
	terrain.focus[2] = terrain.focus[0]+offset[2]
	terrain.focus[3] = terrain.focus[1]-offset[3]
	terrain.true_focus = [ offset[4],offset[5] ]
	print( offset, "!!!!!!!" )
	
	width = len(data[0])
	height = len(data)
	

	startASCIIimport(data)


	print ('Section created.')

def display_section_selected():
	scene = bpy.context.scene
	if scene.objects.active:
		print (scene.objects.active)
		loc = scene.objects.active.location / terrain.tr_singleton.map.scale
		size = bpy.context.scene.terrain_props['size'].int
		#now organize this so it's giving top left and bottom right corners
		focus = []

		focus.append(int(loc[0])-int(size/2))
		focus.append(int(loc[1])+int(size/2))
		focus.append(int(loc[0])+int(size/2))
		focus.append(int(loc[1])-int(size/2))
		terrain.focus = focus
		p = focus

		returned = terrain.tr_singleton.readRect_addon(p[0],p[1],p[2],p[3])
		
		data = returned[0]
		offset = returned[1]
		#keeping the section in the right place if it was requesting out of map info
		terrain.true_focus = [ terrain.focus[0],terrain.focus[1] ]
		terrain.focus[0] += offset[0]
		terrain.focus[1] -= offset[1]
		terrain.focus[2] = terrain.focus[0]+offset[2]
		terrain.focus[3] = terrain.focus[1]-offset[3]
		terrain.true_focus = [ offset[4],offset[5] ]

		
		width = len(data[0])
		height = len(data)
	

		startASCIIimport(data)


		print ('Section created.')
	else:
		print('no object selected')

###############################
def new_terrain():
	name=bpy.context.scene.terrain_props['filename'].string
	width=bpy.context.scene.terrain_props['width'].int
	height=bpy.context.scene.terrain_props['height'].int
	scale=bpy.context.scene.terrain_props['scale'].float
	terrain.tr_singleton.new(width,height, "./data/terrains/"+name, scale)

def load_terrain(filename):
	terrain.tr_singleton.load(filename)

	
	
def load_png(filepathr):
	print(filepathr)
	bpy.ops.image.open('INVOKE_DEFAULT', filepath=filepathr) 
	img =  bpy.data.images[ filepathr.split('\\')[-1:][0] ] 
	print(dir(img), img, img.size[0], img.size[1])
	terrain.tr_singleton.new(img.size[0], img.size[1], "./data/terrains/"+img.name.split('.')[0]+'.terrain', 1.0)
	print("DEPTH: ", img.depth)
	pix = list(img.pixels)
	pix.reverse()
	print(pix[0:20])
	for i in range( img.size[0] * img.size[1] ):
		#if i%10000 == 0: print(i)
		try:
			terrain.tr_singleton.map.buffer[i] = int( (pix[i*4+3]-.5)* 32760 )
		except:
			print("!!!!!!!!!", (pix[i*4+3]*2-1), (pix[i*4+3]-.5)* 32760 )
	
def apply_scale():
	terrain.tr_singleton.map.scale = bpy.context.scene.terrain_props['xyscale'].float
	for i in range(len(terrain.tr_singleton.map.buffer)):
		new = int(float(terrain.tr_singleton.map.buffer[i])* bpy.context.scene.terrain_props['zscale'].float)
		if new < -32767: 
			new = -32767
		if new > 32767: 
			new = 32767
		terrain.tr_singleton.map.buffer[i] = new
		
	#terrain.tr_singleton.save(terrain.tr_singleton.filename)
	#terrain.tr_singleton.load(terrain.tr_singleton.filename)
	print('finished scaling..')

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
	
def compile_terrain():
	print ("Compiling Terrain..")
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
	#injecting the quadtree into the map instance
	terrain.tr_singleton.map.quadtree = terrain.qt_singleton
	# strip off unneeded data
	# we don't need the normals
	terrain.tr_singleton.map.nx = False	
	terrain.tr_singleton.map.ny = False
	terrain.tr_singleton.map.nz = False

	print('Saving: ', terrain.tr_singleton.filename)
	terrain.tr_singleton.save(terrain.tr_singleton.filename)
	print ("Finished!")

###############################
### Main World Baker here - Operator
def bake_world():
	d = terrain.current.data

	d.vertices[0].select = True


	height = []
	normals = []
	for v in d.vertices:
		height.append( int(v.co[2]*100/terrain.tr_singleton.map.scale) )

		tt = []
		for i in range(3):
			tt.append( int(v.normal[i]*127) )
		normals.append( tt )
	
	# sometimes normals are missing (like in a published map )
	terrain.tr_singleton.reset_norms()
		

	data = [height, normals]
	x1 = terrain.true_focus[0] #-int(terrain.tr_singleton.map.width/2)
	y1 = terrain.true_focus[1] #-int(terrain.tr_singleton.map.height/2)
	terrain.tr_singleton.writeRect(data, x1,y1,
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

# Create an area of terrain around a selected object
class te_3(bpy.types.Operator):

	'''enter the coordinates of the terrain section you would like to edit. (uses size)'''

	bl_idname = "scene.display_section_selected"
	bl_label = "Display at Selection"

	def execute(self, context):
		display_section_selected()
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

	'''Compiles the terrain [warning! save as]'''

	bl_idname = "scene.compile_terrain"
	bl_label = "Compile Terrain"

	def execute(self, context):
		compile_terrain()
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

class te_3(bpy.types.Operator):

	'''Changes the scale of the current .terrain'''

	bl_idname = "scene.applyscale"
	bl_label = "Apply Scale"

	def execute(self, context):
		apply_scale()
		return {'FINISHED'}

def register():
	bpy.utils.register_class(te_3)

def unregister():
	bpy.utils.unregister_class(te_3)

register()

###### SAVE

class terrain_save(bpy.types.Operator):
	bl_idname = "scene.terrain_save"
	bl_label = "Save Terrain"
	bl_description = "Saves the terrain.."
	filepath = bpy.props.StringProperty(subtype='FILENAME')
	filepath_ext = ".terrain"
	
	@classmethod
	def poll(cls, context):
		return True
	
	def invoke(self, context, event):
		context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}
	
	def execute(self, context):
		print( self.properties.filepath )
		terrain.tr_singleton.save( self.properties.filepath )
		return {'FINISHED'}

def register():
	bpy.utils.register_class(terrain_save)

def unregister():
	bpy.utils.unregister_class(terrain_save)

register()



### LOAD

class terrain_open(bpy.types.Operator, ImportHelper):
	
	'''Open an existing .terrain file.'''
	
	bl_idname = "scene.testopen"
	bl_label = "Load .terrain file"

	# From ImportHelper. Filter filenames.
	filename_ext = ".terrain"
	filter_glob = bpy.props.StringProperty(default="*.terrain", options={'HIDDEN'})

	filepath = bpy.props.StringProperty(name="File Path", 
		maxlen=1024, default="")

	def execute(self, context):
		import bpy, os
		load_terrain( self.properties.filepath ) ### 
		return{'FINISHED'}  

	def invoke(self, context, event):
		context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}  
	
def register():
	bpy.utils.register_class(terrain_open)

def unregister():
	bpy.utils.unregister_class(terrain_open)

register()

### LOAD PNG

class png_open(bpy.types.Operator):
	
	'''Open a 32bit .tif file as a new .terrain'''
	
	bl_idname = "scene.pngopen"
	bl_label = "Load .tif file"

	# From ImportHelper. Filter filenames.

	filename_ext = ".tif"
	filter_glob = bpy.props.StringProperty(default="*.tif", options={'HIDDEN'})

	filepath = bpy.props.StringProperty(name="File Path", 
		maxlen=1024, default="")

	def execute(self, context):
		import bpy, os
		load_png( self.properties.filepath ) ### 
		return{'FINISHED'}  

	def invoke(self, context, event):
		context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}  
	
def register():
	bpy.utils.register_class(png_open)

def unregister():
	bpy.utils.unregister_class(png_open)

register()





### Panel
class OBJECT_PT_terrain_editor(bpy.types.Panel):
	bl_label = "NT - Terrain Editor - v0.2"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "scene"

	def draw(self, context):
		layout = self.layout

		obj = context.object

		row = layout.row()

		###
		box = layout.box()
		row = box.row()
		split = row.split(percentage=0.4)
		colL = split.column()
		colR = split.column()

		colR.operator("scene.new_terrain", icon='NEW')
		colL.operator("scene.testopen", icon='FILE_FOLDER')
		colL.operator("scene.pngopen", icon='FILE_FOLDER')
		colL.operator("scene.terrain_save", icon='FILE_FOLDER')
		
		row = colR.row()
		colR.prop

		###

		

		split = colR.split(percentage=0.4)
		colL = split.column()
		colR = split.column()
		for arg in arg_com[0]:

			try:
				prop = bpy.context.scene.terrain_props[arg]
			except:
				print('can"t create ',arg)
			row = box.row()

			
			

			colL.label(str(arg)+':')

			if isinstance(args1[arg], float) == True:
				colR.prop(prop, "float", text='')

			elif isinstance(args1[arg], bool) == True:
				colR.prop(prop, "bool", text='')

			elif isinstance(args1[arg], int) == True:
				colR.prop(prop, "int", text='')

			elif isinstance(args1[arg], str) == True:
				colR.prop(prop, "string", text='')



		###
		box = layout.box()
		row = box.row()
		split = row.split(percentage=0.4)
		colL = split.column()
		colR = split.column()

		colL.label('Display Section:')
		colR.operator("scene.display_section")

		colL.label('Display at Selected:')
		colR.operator("scene.display_section_selected")


		for arg in arg_com[1]:
			prop = bpy.context.scene.terrain_props[arg]

			row = box.row()

			split = row.split(percentage=0.4)
			colL = split.column()
			colR = split.column()

			colL.label(str(arg)+':')

			if isinstance(args2[arg], float) == True:
				colR.prop(prop, "float", text='')

			elif isinstance(args2[arg], bool) == True:
				colR.prop(prop, "bool", text='')

			elif isinstance(args2[arg], int) == True:
				colR.prop(prop, "int", text='')

			elif isinstance(args2[arg], str) == True:
				colR.prop(prop, "string", text='')
		
		
				
		### ALTER SCALE
		box = layout.box()
		row = box.row()
		split = row.split(percentage=0.4)
		colL = split.column()
		colR = split.column()




		for arg in arg_com[2]:
			prop = bpy.context.scene.terrain_props[arg]

			row = box.row()

			split = row.split(percentage=0.4)
			colL = split.column()
			colR = split.column()

			colL.label(str(arg)+':')

			if isinstance(args3[arg], float) == True:
				colR.prop(prop, "float", text='')

			elif isinstance(args3[arg], bool) == True:
				colR.prop(prop, "bool", text='')

			elif isinstance(args3[arg], int) == True:
				colR.prop(prop, "int", text='')

			elif isinstance(args3[arg], str) == True:
				colR.prop(prop, "string", text='')
				
		colL.label('Change scale:')
		colR.operator("scene.applyscale")


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
		box = layout.box()
		row = box.row()
		split = row.split(percentage=0.4)
		colL = split.column()
		colR = split.column()

		colL.label('New Texture:')
		colR.operator("scene.newtexture")
		
		colL.label('Compile for game:')
		colR.operator("scene.compile_terrain")

		###




def register():
	bpy.utils.register_class(OBJECT_PT_terrain_editor)


def unregister():
	bpy.utils.unregister_class(OBJECT_PT_terrain_editor)



create_vars()
register()