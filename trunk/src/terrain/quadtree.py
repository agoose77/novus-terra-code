from array import array
from math import floor, sqrt, pow
from mathutils import Vector




import terrain
try:
	import bge
	scene = bge.logic.getCurrentScene()
	from paths import *
except: #running the addon
	def anon(filename, arg1):
		return open(filename, arg1)
	safeopen = anon




"""
current task: have the tree check the map file to determine an appropriate size and depth level.

"""

BRANCH = 0
LEAF = 1

oct_map = [ [-1, -1], [-1, 1], [1, -1], [1, 1] ]

class Chunk_Que:
	def __init__(self):
		self.available = []
		for entry in scene.objectsInactive:
			print( 'chunk que init:::')
			if "Chunk" in entry.name:
				self.available.append( entry.name )

		self.need_update = []

	def get_chunk(self):

		if len(self.available) > 0:

			return self.available.pop(0)
		else:
			print("ERROR, no chunks left in que!")
			return "Chunk.000"

	def update(self):
		if len(self.need_update) > 0:
			chosen = self.need_update.pop(0)
			chosen.alter_height()


class Quadtree(object):

	def __init__(self, size=2048, pos=[0,0], debug=1, max_depth=7, scale=1.0):
		print("MY SCALE: ", scale)
		self.root = Node(pos, size, debug, max_depth=max_depth, scale=scale)
		

		max_size = terrain.tr_singleton.map.width
		if terrain.tr_singleton.map.height > max_size: max_size = terrain.tr_singleton.map.height
		
		self.root.make_all()
		"""
		solution = 0
		while solution == 0:
			if max_size > size*2:
				size = int(size/2)
				max_depth -= 1
		"""
	def add(self, object):
		self.root.add(object)

	def update_terrain(self, focalpoint):
		self.root.update_terrain(focalpoint)

	def vis_neighbors(self, object):
		self.root.vis_neighbors(object)
		
	def make_all(self):
		self.root.make_all()



class Node(object):
	def __init__(self, pos, size, debug, depth=0, max_depth=7, scale=1.0, nochunk = 0):
		self.scale = scale
		self.pos = pos
		self.size = size
		self.data = []
		self.state = LEAF
		self.parent = 0
		self.debug = debug
		self.depth = depth
		self.max_depth = max_depth

		self.v_array = array('f', [0]*1225)


		self.address = []
		self.children = []
		
		self.test_children = []

		#buffer for edge height values
		self.top_index = []
		self.left_index = []
		
	def make_all(self):
		if self.depth < self.max_depth:
			for i in range(4):
				position = [self.pos[0] + oct_map[i][0]*self.size/2, self.pos[1] + oct_map[i][1]*self.size/2]
				self.test_children.append( Node(pos=position, size=self.size/2, debug=self.debug, depth=self.depth+1, max_depth=self.max_depth, scale = self.scale, nochunk = 1) )
				child = self.test_children[len(self.test_children)-1]
				child.parent = self
				child.spot = i #let me know my order of creation ergo placement in parent
				child.precompute_chunk()
				child.make_all()

	def split(self):
		self.state = BRANCH


		try:
			self.remove_chunk(self)
		except:
			pass

		for i in range(4):
			position = [self.pos[0] + oct_map[i][0]*self.size/2, self.pos[1] + oct_map[i][1]*self.size/2]
			self.children.append( self.test_children[i] )
			child = self.children[len(self.children)-1]
			child.parent = self
			child.spot = i #let me know my order of creation ergo placement in parent
			child.add_chunk()

	def update_terrain(self, focalpoint):
		#scale hacks
		focalpoint2 = [ focalpoint[0], focalpoint[1] ]
		#print(self.dist(focalpoint,self.pos))
		if self.dist(focalpoint2):
			#if I'm a leaf, split and check children
			if self.state == LEAF:
				if self.depth < self.max_depth:
					self.split()
					for node in self.children:
						node.update_terrain(focalpoint)
			else:
				for node in self.children:
					node.update_terrain(focalpoint)

		else:
			#if I'm a branch
			if self.state == BRANCH:

				for node in self.children:
					self.remove_chunk(node)
					del(node)
				self.children = []
				self.state = LEAF
				self.add_chunk()


	def remove_chunk(self, node):
		if type(node.cube) != int:
			terrain.cq_singleton.available.append( node.cube.name )
			if node in terrain.cq_singleton.need_update:
				terrain.cq_singleton.need_update.remove(node)
			node.cube.endObject()
			node.cube = 0

	def add_chunk(self):
		chunkname = terrain.cq_singleton.get_chunk()
		
		self.cube = self.spawnObject(chunkname, [self.pos[0]*self.scale,self.pos[1]*self.scale,0] )
		self.cube.localScale = [self.size*self.scale, self.size*self.scale, 1] #?
		#add to que to wait for vertex adjustment
		#terrain.cq_singleton.need_update.append( self )
		mesh = self.cube.meshes[0]
		for i in range(len(self.v_array)):
			try:
				v = mesh.getVertex(0, i)
				v.setXYZ([v.getXYZ()[0],v.getXYZ()[1],self.v_array[i] ])
			except:
				print(i)
		if self.depth == self.max_depth:
			self.cube.reinstancePhysicsMesh()
			self.cube.color = [1,0,0,1]
		else:
			self.cube.color = [1,1,1,1]


	def alter_height(self):
		game.Game.singleton.profiler.start_timer('chunk update')
		terrain.tr_singleton.alter_chunk(self.pos[0], self.pos[1], self)
		game.Game.singleton.profiler.stop_timer('chunk update')


	####### DEBUG VISUALIZATION
	def spawnObject(self, objectName, worldPosition = [0.0, 0.0, 0.0]):
		newObject = scene.addObject(objectName, "CELL_MANAGER_HOOK")
		newObject.worldPosition = worldPosition
		return newObject


	def dist2(self, point):
		x1, y1 = self.pos[0]*self.scale, self.pos[1]*self.scale
		x2, y2 = point[0], point[1]
		range = 2*self.size+self.size*.3*self.scale

		if abs(x1-x2) < range and abs(y1-y2) < range:
			return True

	def dist(self, p1):
		p2 = [self.pos[0]*self.scale, self.pos[1]*self.scale]
		x = p1[0] - p2[0]
		y = p1[1] - p2[1]

		d = sqrt(pow(x, 2) + pow(y,2))


		if d < self.size*2*self.scale:
			return True

	def remove(self, object):
		try:
			object._oct_node
		except:
			print(object, " has no property _oct_node")

		object._oct_node.children.remove(object)

		total_objects = []
		for entry in self.parent.children:
			total_objects += entry.data
		if len(total_children) > self.max:
			self.parent.state = LEAF
			for thing in total_objects:
				self.parent.add(thing)

			if self.debug == 1:
				for entry in self.parent.children:
					entry.cube.endObject()

			self.parent.children = []

	def precompute_chunk(self ):
		"""
		create a list of vertex ready heights, corresponding to the vertex order of the chunk
		"""
		map = terrain.tr_singleton.map
		x = self.pos[0]
		y = self.pos[1]
		
		trans = terrain.tr_singleton.translate_xy_terrain([x,y])
		x,y = trans[0],trans[1]
		
		#chunks are always be 32^2, and are centered on the x,y
		depth = self.max_depth-self.depth #1 most detail, 0 lowest
		sample = int(pow(2,depth))
		x1, y1 = int(x-(sample/2)*32), int(y-(sample/2)*32)
		x2, y2 = int(x+(sample/2)*32), int(y+(sample/2)*32)
		#######		
		width = abs(x2 - x1)
		height = abs(y2 - y1)
		l = []

		
		#we're saving some data to make the skirts
		top_cache, bottom_cache, left_cache, right_cache = [],[],[],[]

		t = 0
		for i in range(33):
			temp = []
			temp_norm = []
			
			for j in range(33):
				c = x1 + (y1+(i*sample))*map.width + (j*sample) 
				
				try:
					self.v_array[terrain.tr_singleton.translate_vertex_order(t)] = ( map.buffer[ c ]* self.scale *.01 )
				except:
					self.v_array.append( -500 )
				t += 1
				if c >= map.width*map.height:
					c = 0
				skirt_offset = map.buffer[ c ]* self.scale *.01 - .1*self.scale*self.scale*self.scale
				if i == 0:
					top_cache.append(skirt_offset)
				elif i == 32:
					bottom_cache.append(skirt_offset)
				if j == 0:
					left_cache.append(skirt_offset)
				elif j == 32:
					right_cache.append(skirt_offset)
				
		#Now lets set the skirt
		#1089 - left - top - right - bottom
		right_cache.reverse()
		right_cache = right_cache[1:]+[right_cache[0]] #offsetting this seems to help?
		left_cache.insert( 0, left_cache[0] ) #one of the first ones needs better data
		left_cache.pop(32)
		total = top_cache + bottom_cache + [bottom_cache[32]]*2 + [bottom_cache[0]]*2 + [top_cache[32]]*2 + left_cache + right_cache 
		
		self.v_array = self.v_array[:1089]+array('f', total)




