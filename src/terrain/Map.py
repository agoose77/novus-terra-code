from array import array
import pickle, time
from math import pow
try:
	import bge
	scene = bge.logic.getCurrentScene()
	from paths import *
except: #running the addon
	def anon(filename, arg1):
		return open(filename, arg1)
	safeopen = anon

class Map:
	def __init__(self,width,height,scale):
		self.width = width
		self.height = height
		self.scale = scale
		#height
		self.buffer = array('h', [0]*self.width*self.height)
		#normals
		self.nx = array('b', [0]*self.width*self.height)
		self.ny = array('b', [0]*self.width*self.height)
		self.nz = array('b', [0]*self.width*self.height)
		
	
		
class Map_Manager:
	def __init__(self):
		self.filename = 'default.terrain'
		self.map = 0
		
	def new(self, width, height, filename="new.terrain", scale=.1):
		self.map = Map(width, height, scale)
		self.filename = filename
		self.save(filename)
		
	def load(self, filename):
		print(filename)
		fo = safeopen(filename, 'rb')
		self.map = pickle.load( fo )
		fo.close
		self.filename = filename
		print(filename, " loaded.")
		
	def save(self, filename):
		pickle.dump( self.map, open(filename, 'wb') )
		print(filename, " saved.")
		#data = [self.map.width, self.map.height, self.map.scale, list(self.map.buffer), list(self.map.nx), list(self.map.ny), list(self.map.nz)]
		#f = open(filename+'.rc', 'wb')
		#f.write( rencode.dumps(data) )
		
	def save_normal_list(self, filename):
		temp = []
		for i in range(self.map.width*self.map.height):
			temp.append( [self.map.nx[i],self.map.ny[i],self.map.nz[i] ] )
		new = open(filename, 'wb')
		print("FUCK YEAH")
		for i in range(self.map.height):
			new.write(bytes(str(temp[self.map.width*i:self.map.width*i + (self.map.width)])+'\n', 'UTF-8')) #have to seperate into lines for memory concerns
		
		new.close()
		
	def reset_norms(self):
		array_len = self.map.width*self.map.height
		self.map.nx = array('b', [0]*array_len)
		self.map.ny = array('b', [0]*array_len)
		self.map.nz = array('b', [0]*array_len)
		
	def readRect_addon(self, x1,y1,x2,y2, sample=1):
		#this returns a 2D list array
		
		xy = self.translate_xy_terrain( [x1,y1] )
		x1, y1 = xy[0], xy[1]
		xy = self.translate_xy_terrain( [x2,y2] )
		x2, y2 = xy[0], xy[1]
		#now we are working in .terrain coordinates
		
		#make sure the points are top left / bottom right
		if x2<x1:
			temp = x1
			x1 = x2
			x2 = temp
		if y2<y1:
			temp = y1
			y1 = y2
			y2 = temp
		
		offset = [0,0]
		
		if x1 < 0: 
			offset[0] = abs(x1)
			x1 = 0
		if y1 < 0: 
			offset[1] = abs(y1)
			y1 = 0
		if x2 > self.map.width: x2 = self.map.width
		if y2 > self.map.height: y2 = self.map.height
		width = abs(x2 - x1)
		height = abs(y2 - y1)
		print( 'popcop:',x1,y1)
		xy = self.translate_xy_terrain_back( [x1,y1] )
		offset += [width,height,xy[0],xy[1]] #really funky order
		l = []
		
		#also needs to return the size and top left
		
		for i in range(height):
			temp = []

			for j in range(width):
				c = x1 + (y1+(i*sample))*self.map.width + (j*sample) 
				try:
					temp.append( self.map.buffer[ c ] )
				except:
					pass
			
			
			
			l.append(temp)
		
			
		return [l, offset]
		
	def writeRect(self, data, x1,y1,x2,y2, sample=1):
		#data is [height, normals]
		xy = self.translate_xy_terrain( [x1,y1] )
		x1, y1 = xy[0], xy[1]
		xy = self.translate_xy_terrain( [x2,y2] )
		x2, y2 = xy[0], xy[1]
		#now we are working in .terrain coordinates
		
		#make sure the points are top left / bottom right
		if x2<x1:
			temp = x1
			x1 = x2
			x2 = temp
		if y2<y1:
			temp = y1
			y1 = y2
			y2 = temp
			
		width = abs(x2 - x1)
		height = abs(y2 - y1)
		t = 0
		
		for i in range(height):
			for j in range(width):
				c = x1 + (y1+(i*sample))*self.map.width + (j*sample) 
				if data[0][t] < -32766: data[0][t] = -32766
				if data[0][t] > 32766: data[0][t] = 32766
				self.map.buffer[ c ] = data[0][t]
				self.map.nx[ c ] = data[1][t][0]
				self.map.ny[ c ] = data[1][t][1]
				self.map.nz[ c ] = data[1][t][2]
				t += 1
		self.save(self.filename)
		self.load(self.filename)
			
		
	def readChunk(self, x,y, depth, node):
		trans = self.translate_xy_terrain([x,y])
		x,y = trans[0],trans[1] 
		#chunks will always be 33^2, and are centered on the x,y

		depth = 7-depth #1 most detail, 0 lowest
		dinc = int(pow(2,depth))
		x1, y1 = int(x-(dinc/2)*32), int(y-(dinc/2)*32)
		x2, y2 = int(x+(dinc/2)*32), int(y+(dinc/2)*32)
		
		self.readRect(x1,y1,x2,y2,dinc, node)
	
	
	def translate_xy_terrain(self, xy):
		#blender coo are +x-y centered on 0,0
		#map coo are +x+y
		w = self.map.width
		h = self.map.height
		
		xy[0] = xy[0]+int(w/2)
		xy[1] = -xy[1]+int(h/2)
		return xy
		
	def translate_xy_terrain_back(self, xy):
		#blender coo are +x-y centered on 0,0
		#map coo are +x+y
		w = self.map.width	
		h = self.map.height
		
		xy[0] = xy[0]-int(w/2)
		xy[1] = -xy[1]+int(h/2)
		return xy
		
	def translate_vertex_order(self,v):
		#translates 33^2 array to vertex order of a subdivided 33^2 plane.
		if v > 64:
			return v
		elif v in [0,1,33,34, 35]:
			if v == 0:
				return 1
			if v == 1:
				return 0
			if v == 33:
				return 2
			if v == 34:
				return 3
			if v == 35:
				return 5
		else:
			if v > 1 and v < 33:
				return v*2
			elif v > 34 and v < 65:
				return  ((v-33) * 2) + 1 
		print("translate_vertex_order error")
		
	########## CONSTRUCTION	ZONE
	# idea is to alter the mesh directly in the readRect function
		
	def alter_chunk(self, x,y, node=0):
		if node == 0:
			print("error: pass a node to Map.map_manager.readRect")
			return
		#### this used to be read_chunk
		trans = self.translate_xy_terrain([x,y])
		x,y = trans[0],trans[1]
		
		#chunks are always be 32^2, and are centered on the x,y
		depth = node.max_depth-node.depth #1 most detail, 0 lowest
		sample = int(pow(2,depth))
		x1, y1 = int(x-(sample/2)*32), int(y-(sample/2)*32)
		x2, y2 = int(x+(sample/2)*32), int(y+(sample/2)*32)
		#######		
		
		mesh = node.cube.meshes[0]
		width = abs(x2 - x1)
		height = abs(y2 - y1)
		l = []
		data_norm = []
		
		#we're saving some data to make the skirts
		top_cache, bottom_cache, left_cache, right_cache = [],[],[],[]
		
		########## Main Loop ########
		# need to save index of left and top sides in node
		# node.left_ind and node.top_ind
		t = 0
		for i in range(33):
			temp = []
			temp_norm = []
			
			for j in range(33):
				c = x1 + (y1+(i*sample))*self.map.width + (j*sample) 
				
				try:
					v = mesh.getVertex(0, self.translate_vertex_order(t))
				except:
					print( ":(  ", t, self.translate_vertex_order(t) )
				try:
					v.setXYZ([v.getXYZ()[0],v.getXYZ()[1],self.map.buffer[ c ]* node.scale *.01]) #?

				except:
					v.setXYZ([v.getXYZ()[0],v.getXYZ()[1],-500])
				
				
				
				t += 1
				if c >= self.map.width*self.map.height:
					c = 0
				skirt_offset = self.map.buffer[ c ]* node.scale *.01 - .1*node.scale*node.scale*node.scale
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
		
		for i in range(136):
			v = mesh.getVertex(0, 1089+i)
			v.setXYZ([v.getXYZ()[0],v.getXYZ()[1],total[i]])
			if 1089+i > 1161 and 1089+i < 1194:
				#v.setRGBA([0,0,0,1])
				pass
				
			v = mesh.getVertex(0, 1160)
			v.setRGBA([1,0,0,1])
		if node.depth == node.max_depth: 
			node.cube.reinstancePhysicsMesh()
		