
from math import floor, sqrt, pow
from mathutils import Vector

import bge
scene = bge.logic.getCurrentScene()

camera = scene.objects['Camera']

"""
place objects in leaf untill > max
split leaf, sort into children
map nodes (used for entities to check their node and move self)


"""

BRANCH = 0
LEAF = 1

oct_map = [ [-1, -1, -1], [-1, -1, 1], [-1, 1, -1], [-1, 1, 1], 
			[1, -1, -1],  [1, -1, 1],  [1, 1, -1],  [1, 1, 1]]

class Octree(object):

	def __init__(self, size=10000, pos=[0,0,0], max=2, debug=0):
	
		self.root = Node(pos, size, max, debug)
		
		
	def add(self, object):
		self.root.add(object)
		
	
	
class Node(object):
	def __init__(self, pos, size, max, debug):
		self.pos = pos
		self.size = size
		self.data = []
		self.state = LEAF
		self.parent = 0
		self.debug = 0
		self.max = max

		if self.debug == 1:
			self.cube = self.spawnObject("Cube", self.pos)
			self.cube.localScale = [self.size]*3
			self.cube.color = [1.0,0,0,.5]
		
		self.address = []
		self.children = []
		
	def add(self, object):
		if self.state == LEAF:
			if len(self.data) < self.max:
				self.data.append(object)
				object._oct_node = self
			else:
				self.data.append(object)
				self.split()
		else:
			self.sort(object)
	
	def sort(self, object):
		index = 0
		loc = list(object.location)
		if loc[0] > self.pos[0]:
			index = 4
		if loc[1] > self.pos[1]:
			index += 2
		if loc[2] > self.pos[2]:	
			index += 1
		self.children[index].add(object)
		
	def split(self):
		self.state = BRANCH
		self.color = [0,0,0,0]
		for i in range(8):
			position = [self.pos[0] + oct_map[i][0]*self.size/2, self.pos[1] + oct_map[i][1]*self.size/2, self.pos[2] + oct_map[i][2]*self.size/2]
			self.children.append( Node(pos=position, size=self.size/2, max=self.max, debug=self.debug) )
			self.children[len(self.children)-1].parent = self
		for entry in self.data:
			self.sort(entry)
		self.data = []

		if self.debug == 1:
			print( "fishished split")
		
	####### DEBUG VISUALIZATION
	def spawnObject(self, objectName, worldPosition = [0.0, 0.0, 0.0]):
		newObject = scene.addObject(objectName, "Empty")
		newObject.worldPosition = worldPosition
		return newObject
		
		
	def dist(self, p1, p2):
		x = p1[0] - p2[0]
		y = p1[1] - p2[1]
		z = p1[2] - p2[2]
		d = sqrt(pow(x, 2) + pow(y,2) + pow(z,2))
		return d
	
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
			
	
	
	
	
	## Query functions
	
	def node_within_cube(self, pp, ps):
		# 0 outside, 1 intersect, 2 inside, 3 contains
		ns = self.size/2
		np = self.pos
		intersects = [0,0,0]
		
		for i in range(3):
			#print("=======")
			if  np[i]-ns <= pp[i]-ps and np[i]+ns >= pp[i]+ps:
				intersects[i] = 1
				#print("contains")
			elif ( np[i]+ns >= pp[i]-ps and np[i]-ns <= pp[i]-ps ) or ( np[i]-ns <= pp[i]+ps and np[i]+ns >= pp[i]+ps ): #it's intersecting
				intersects[i] = 1
				#print("intersects")
			elif (np[i]+ns <= pp[i]-ps) or (np[i]-ns >= pp[i]+ps): #it's completely outside
				intersects[i] = 0
				#print("outside")
			else:
				#print("inside")
				intersects[i] = 2
		k = 0
		for entry in intersects:
			if entry == 0:
				return 0
			elif entry == 1:
				k = 1
		if k == 1:
			return 1
		else:
			return 2
		
		
	def node_within_frustum(self, camera):
		box = []
		np = self.pos
		ns = self.size/2
		
		box = [ [np[0]-ns, np[1]-ns, np[2]-ns],
				[np[0]-ns, np[1]-ns, np[2]+ns],
				[np[0]-ns, np[1]+ns, np[2]-ns],
				[np[0]-ns, np[1]+ns, np[2]+ns],
				[np[0]+ns, np[1]-ns, np[2]-ns],
				[np[0]+ns, np[1]-ns, np[2]+ns],
				[np[0]+ns, np[1]+ns, np[2]-ns],
				[np[0]+ns, np[1]+ns, np[2]+ns] ]
				
		return camera.boxInsideFrustum(box)
	
	
	def pull(self, collection):
		#print("PULLED")
		if self.state == LEAF:
			collection += self.data
			if self.debug == 1:
				self.cube.color = [0,1,1,1]
		else:
			for entry in self.children:
				entry.pull(collection)
				
	def camera_pull_distance(self, camera, r, collection):
		#print("PULLED")
		
		if self.state == LEAF:
			self.cube.color = [1,0,0,.05]
			for entry in self.data:
				dist = camera.getDistanceTo( entry.location )
				if dist < r:
					collection[entry] = dist
		else:
			for entry in self.children:
				entry.camera_pull_distance(camera, r, collection)


		
	def get_within(self, point, r, set):
		#print( "?")
		if self.state == BRANCH:
			test = self.node_within_cube(point, r)
			
			
			if test == 2:
				self.pull(set)
			if test == 1:
				for entry in self.children:
					entry.get_within(point, r, set)
		else:
			#i'm a leaf, sort me
			self.data_in(point, r, set)
			
	def get_within_camera(self, camera, r, set):

		test = self.node_within_frustum(camera)
		if test == 1: #intersecting
			self.cube.color = [0,1.0,1.0,.05]
		elif test == 0: #inside
			self.cube.color = [1,0,0,.05]
		elif test == 2: #outside
			self.cube.color = [1,1,0,.05]
			
		if test == 0:
			self.camera_pull_distance(camera, r, set)
		if test == 1:
		
			if self.state == BRANCH:
				for entry in self.children:
					entry.get_within_camera(camera, r, set)
			else:
				for entry in self.data:
					if camera.pointInsideFrustum( entry.location ):
						dist = camera.getDistanceTo( entry.location )
						if dist < r:
							set[entry] = dist
							
	def point_within_frustum(self, camera, point):
		return camera.pointWithinFrustum( point )
	
	def data_in(self, point, r, set):
		for entry in self.data:
			dp = list(entry.location)
			if dp[0] > point[0]-r and dp[0] < point[0]+r:
				if dp[1] > point[1]-r and dp[1] < point[1]+r:
					if dp[1] > point[1]-r and dp[1] < point[1]+r:
						#print("INTERSECT AND WITHIN")
						set.append(entry)