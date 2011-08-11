
from math import floor, sqrt, pow
from mathutils import Vector


import bge, terrain
scene = bge.logic.getCurrentScene()



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
		while len(self.need_update) > 0:
			chosen = self.need_update.pop(0)
			chosen.alter_height()
			

class Quadtree(object):

	def __init__(self, size=2056, pos=[0,0], debug=1, max_depth=7):
	
		self.root = Node(pos, size, debug, max_depth=max_depth)
		
		
		max_size = terrain.tr_singleton.map.width
		if terrain.tr_singleton.map.height > max_size: max_size = terrain.tr_singleton.map.height
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
		
	
	
class Node(object):
	def __init__(self, pos, size, debug, depth=0, max_depth=7):

		self.pos = pos
		self.size = size
		self.data = []
		self.state = LEAF
		self.parent = 0
		self.debug = debug
		self.depth = depth
		self.max_depth = max_depth


		self.add_chunk()
		
		self.address = []
		self.children = []
		
		#buffer for edge height values
		self.top_index = []
		self.left_index = []
	
	def split(self):
		self.state = BRANCH
		
		
		self.remove_chunk(self)
			

		for i in range(4):
			position = [self.pos[0] + oct_map[i][0]*self.size/2, self.pos[1] + oct_map[i][1]*self.size/2]
			self.children.append( Node(pos=position, size=self.size/2, debug=self.debug, depth=self.depth+1, max_depth=self.max_depth) )
			child = self.children[len(self.children)-1]
			child.parent = self
			child.spot = i #let me know my order of creation ergo placement in parent

	def update_terrain(self, focalpoint):
		#print(self.dist(focalpoint,self.pos))
		if self.dist(focalpoint):
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
		terrain.cq_singleton.available.append( node.cube.name )
		if node in terrain.cq_singleton.need_update:
			terrain.cq_singleton.need_update.remove(node)
		node.cube.endObject()
		node.cube = 0
	
	def add_chunk(self):
		chunkname = terrain.cq_singleton.get_chunk()
		self.cube = self.spawnObject(chunkname, [self.pos[0],self.pos[1],0] )
		self.cube.localScale = [self.size, self.size, 200]
		#add to que to wait for vertex adjustment
		terrain.cq_singleton.need_update.append( self )
	
	
	def alter_height(self):
		terrain.tr_singleton.alter_chunk(self.pos[0], self.pos[1], self)
	

	
	####### DEBUG VISUALIZATION
	def spawnObject(self, objectName, worldPosition = [0.0, 0.0, 0.0]):
		newObject = scene.addObject(objectName, "Empty")
		newObject.worldPosition = worldPosition
		return newObject
		
	
	def dist2(self, point):
		x1, y1 = self.pos[0], self.pos[1]
		x2, y2 = point[0], point[1]
		range = 2*self.size+self.size*.3
		
		if abs(x1-x2) < range and abs(y1-y2) < range:
			return True
	
	def dist(self, p1):
		p2 = [self.pos[0], self.pos[1]]
		x = p1[0] - p2[0]
		y = p1[1] - p2[1]

		d = sqrt(pow(x, 2) + pow(y,2))
		
		
		if d < self.size*1.6:
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
			
			
	def get_node_from_point(self, point, depth=-1):
		if abs(point[0]-self.centre[0]) > self.radius or abs(point[1]-self.centre[1]) > self.radius:
			return None
		
		if len(self.children) == 0 or depth == 0:
			return self
		else:
			if point[0] > self.centre[0]:
				if point[1] > self.centre[1]:
					return self.children[0].get_node_from_point(point, depth-1)
				else:
					return self.children[1].get_node_from_point(point, depth-1)
			else:
				if point[1] < self.centre[1]:
					return self.children[2].get_node_from_point(point, depth-1)
				else:
					return self.children[3].get_node_from_point(point, depth-1)
				
	def get_neighbours(self, root_node):
		cx = self.centre[0]
		cy = self.centre[1]
		r = self.radius
		
		n1 = root_node.get_node_from_point([cx+2*r, cy], self.depth)
		n2 = root_node.get_node_from_point([cx-2*r, cy], self.depth)
		n3 = root_node.get_node_from_point([cx, cy+2*r], self.depth)
		n4 = root_node.get_node_from_point([cx, cy-2*r], self.depth)
		n5 = root_node.get_node_from_point([cx+2*r, cy+2*r], self.depth)
		n6 = root_node.get_node_from_point([cx+2*r, cy-2*r], self.depth)
		n7 = root_node.get_node_from_point([cx-2*r, cy+2*r], self.depth)
		n8 = root_node.get_node_from_point([cx-2*r, cy-2*r], self.depth)
		
		neighbours = []
		if n1:
			neighbours.append(n1)
		if n2:
			neighbours.append(n2)
		if n3:
			neighbours.append(n3)
		if n4:
			neighbours.append(n4)
		if n5:
			neighbours.append(n5)
		if n6:
			neighbours.append(n6)
		if n7:
			neighbours.append(n7)
		if n8:
			neighbours.append(n8)
		
		return neighbours
		
	def vis_neighbors(self, object):
		if self.state == LEAF:
			
			if object == self.cube:
				print(self)
				self.cube.color = [0.0,0.0,1.0,1.0]
				mesh = self.cube.meshes[0]
				for i in range(1089):
					v = mesh.getVertex(0, i)
				v.setRGBA([0.0,1.0,1.0,1.0])
				self.handle_stitch()
			
		else:
			for entry in self.children:
				entry.vis_neighbors(object)
	
	
	lookup = { 0:[3], 1:[0,2], 2:[3], 3:[] }
	
	def handle_stitch(self):
	
		class side:
			def __init__(self):
				self.node = 0
		
		spot = self.spot
		
		bottom, right = side(), side()
		if spot == 0:
			right.node = self.parent.children[2]
			right.depth_dif = 0
		elif spot == 1:
			right.node = self.parent.children[3]
			right.depth_dif = 0
			bottom.node = self.parent.children[0]
			right.depth_dif = 0
		elif spot == 3:
			bottom.node = self.parent.children[2]
			bottom.depth_dif = 0
		
		if bottom.node:
			bottom.node.cube.color = [1.0,0.0,1.0,1.0]
		if right.node:
			right.node.cube.color = [1.0,0.0,1.0,1.0]
			
		# From here, we route these found sides off to match siblings
		# Now we check if there are any unmatched
		# 
		# go up to the branch
		# 	if a side is touching a sibling of the branch:
		# 		if it is a leaf: 
		#			match to the node -1 diff of depth using my spot
		#		if it is a branch:
		#			get node corresponding to my spot:
		#				if it is a leaf:
		#					match to it!
		#				if it is a branch:
		#					recurse it's side, gather the nodes, depths, and positions to match to me.
		# 	unmatched sides still?:
		#
		#     
		# Or, i could try to simplify it by checking points in the quadtree.
		# It's simpler to find nodes, still have the mess at the end where you have to gather and sort. (and interpolate)
		#
		# check point slightly outside of bottom, right at the 0:
		#	if node is my depth, stitch to it.
		#	if node is higher depth: (bigger, less detail)
		#		stitch to it based on depth and our positions
		#	if node is lower depth:
		#		somehow pull all the nodes and assign them to me