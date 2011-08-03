#Written by B. Campbell posted on blenderartist.org

#Vert entries must have a .co

#======================================================== 
# SPACIAL TREE - Seperate Class - use if you want to
# USed for getting vert is a proximity
LEAF_SIZE = 128
# 0.4

import mathutils

class kdNode(object):
	__slots__ = 'verts', 'children', 'minx','miny','minz', 'maxx','maxy','maxz',  'medx','medy','medz'
	def __init__(self, verts):
		
		# Assunme we are a leaf node, until split is run.
		self.verts = verts 
		self.children = []
		
		#if not verts:
		#	return
		
		# BOUNDS
		v= verts[0]
		maxx,maxy,maxz= v.co
		minx,miny,minz= maxx,maxy,maxz
		len_verts = len(verts)
		medx= medy= medz= 0.0
		
		for v in verts:
			x,y,z= v.co
			if x>maxx: maxx= x
			if y>maxy: maxy= y
			if z>maxz: maxz= z
			
			if x<minx: minx= x
			if y<miny: miny= y
			if z<minz: minz= z
			
			medx += x/len_verts
			medy += y/len_verts
			medz += z/len_verts
		
		self.minx= minx
		self.miny= miny
		self.minz= minz
		
		self.maxx= maxx
		self.maxy= maxy
		self.maxz= maxz
		
		self.medx= medx
		self.medy= medy
		self.medz= medz
		
		#self.setCornerPoints()
		self.splitNode()
			
	def splitNode(self):
		if len(self.verts) > LEAF_SIZE:
			self.makeChildren() # 2 new children,
			self.verts = None
		# Alredy assumed a leaf not so dont do anything here.
		
	def makeChildren(self):
		verts= self.verts
		# Devide into 2 children.
		axisDividedVerts = [[],[]] # Verts Only
		
		xlen = self.maxx - self.minx
		ylen = self.maxy - self.miny
		zlen = self.maxz - self.minz
		
		axis = 0
		if ylen>xlen: axis = 1
		if zlen>ylen and zlen>xlen: axis = 2
		
		'''
		divx = (self.maxx + self.minx) / 2
		divy = (self.maxy + self.miny) / 2
		divz = (self.maxz + self.minz) / 2
		'''
		
		if 0:# median point
			
			div = (self.medx, self.medy, self.medz)[axis]
			
			# Sort into 2 along long axis
			for v in verts:
				axisDividedVerts[ (v.co[axis]>div) ].append(v)
			
			# populate self.children
			for i in xrange(2):
				if axisDividedVerts[i]:
					
					octNode = kdNode(axisDividedVerts[i])
					self.children.append(octNode)
		else:
			# Halve allong the axis
			verts.sort(key = lambda v: v.co[axis])
			div_index = int(round(len(verts)/2.0))
			
			self.children.extend([ \
				kdNode(verts[:div_index]),\
				kdNode(verts[div_index:]),\
			] )
			
	
	
	def getNearVert(self, loc, range_val, DEBUG_DEPTH=0, DBG_VCMP=0):
		
		best_v = None
		xloc,yloc,zloc= loc
	
		# Check if the bounds are in range_val,
		for childNode in self.children:
			# First test if we are surrounding the point.
			if\
			childNode.minx - range_val < xloc and\
			childNode.maxx + range_val > xloc and\
			childNode.miny - range_val < yloc and\
			childNode.maxy + range_val > yloc and\
			childNode.minz - range_val < zloc and\
			childNode.maxz + range_val > zloc:
				# Recurse down or get virts.
				v, length = childNode.getNearVert(loc, range_val, DEBUG_DEPTH+1)
				
				if v and length < range_val:
					best_v = v
					range_val= length # Shink the length so we only get verts from their.
		
		if self.verts: # we are a leaf node. Test vert locations.
			# Length only check
			for v in self.verts:
				length = (loc - v.co).length
				if length < range_val:
					# Just update the 1 vert
					best_v = v
					range_val= length # Shink the length so we only get verts from their.
					
		return best_v, range_val
	
	
	# GETS VERTS IN A Distance RANGE-
	def getVertsInRange(self, loc, range_val, vertList):
		#loc= Mathutils.Vector(loc)			# MUST BE VECTORS
		#normal= Mathutils.Vector(normal)	

		'''
		loc: Vector of the location to search from
		normal: None or Vector - if a vector- will only get verts on this side of the vector
		range_val: maximum distance. A negative value will fill the list with teh closest vert only.
		vertList: starts as an empty list
		list that this function fills with verts that match
		'''
		xloc,yloc,zloc= loc
		
		if self.children:
			# Check if the bounds are in range_val,
			for childNode in self.children:
				# First test if we are surrounding the point.
				if\
				childNode.minx - range_val < xloc and\
				childNode.maxx + range_val > xloc and\
				childNode.miny - range_val < yloc and\
				childNode.maxy + range_val > yloc and\
				childNode.minz - range_val < zloc and\
				childNode.maxz + range_val > zloc:
					# Recurse down or get virts.
					childNode.getVertsInRange(loc, range_val, vertList)
					#continue # Next please
		
		else: # we are a leaf node. Test vert locations.
			# Length only check
			for v in self.verts:
				vectco = mathutils.Vector(v.co) #convert the entry position to a vector
				length = (loc - vectco).length
				if length < range_val:
					vertList.append(v) #vertList.append((v, length))
					
	# JPLUR ADD NODE
	def insertNode(self, node):
		#loc= Mathutils.Vector(loc)			# MUST BE VECTORS
		#normal= Mathutils.Vector(normal)	
		
		'''
		loc: Vector of the location to search from
		normal: None or Vector - if a vector- will only get verts on this side of the vector
		range_val: maximum distance. A negative value will fill the list with teh closest vert only.
		vertList: starts as an empty list
		list that this function fills with verts that match
		'''
		loc = node.co
		xloc,yloc,zloc= loc
		
		if self.children:
			# Check if the bounds are in range_val,
			for childNode in self.children:
				# First test if we are surrounding the point.
				if\
				childNode.minx < xloc and\
				childNode.maxx > xloc and\
				childNode.miny < yloc and\
				childNode.maxy > yloc and\
				childNode.minz < zloc and\
				childNode.maxz > zloc:
					# Recurse down or get virts.
					childNode.insertNode(node)
					break
					#continue # Next please
				
# END GENERIC KD-TREE CODE








