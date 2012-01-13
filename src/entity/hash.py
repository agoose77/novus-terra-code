
from math import floor, sqrt, pow

class Hash(object):

	def __init__(self, cell_size):
		self.cell_size = cell_size
		self.grid = {}
		
	def key(self, point):
		cell_size = self.cell_size
		return (
			int((floor(point[0]/cell_size))),
			int((floor(point[1]/cell_size))),
			int((floor(point[2]/cell_size)))
		)
		
	def insert(self, object):
		location = list(object.location)
		self.grid.setdefault(self.key(object.location), []).append(object)

	def remove(self, object):
		#all starfield objects should have a location property
		location = list(object.location)
		self.grid.setdefault(self.key(object.location), []).remove(object)

   
	def query(self, location):
		"""
		Return all objects in the cell specified by point.
		"""
		
		#tuple used as key to hash

		return self.grid.setdefault(self.key(location), [])
		
	def update(self, object, new_location):
		location = list(object.location)
		new_location = list(new_location)
		#this is called before the object has its location changed

		if self.key(location) != self.key(new_location):
			# print('move ',self.key(location), ' to ', self.key(new_location))

			self.grid[ self.key(location) ].remove(object)
			self.grid.setdefault(self.key(new_location), []).append(object)

			return True

			
			
	def neighbors(self, location, distance):
		#gauge the range of cells that could contain the distance
		#not going to worry about checking the actual distance at this point, that can be another function if it's necessary
		#collect the entries and return a list
		
		#templating patterns for ranges would be a lot faster, this has too many distance lookups
		#it's filling the hash with empty lists as well, i could just check if the key is there
		
		location = list(location)
		origin = self.key(location)
		max = int(distance/self.cell_size) + 1 
		found = []
						
		for x in range(3):
			for y in range(3):
				for z in range(3):
						found += self.grid.setdefault( ( origin[0] + x-1, origin[1] + y-1, origin[2] + z-1), [])
						
		return found
						
		
	def get_distance( self, location1, location2 ):
		location1 = list(location1)
		location2 = list(location2)
		xx=location1[0]-location2[0]
		yy=location1[1]-location2[1]
		zz=location1[2]-location2[2]
		return sqrt(pow(xx,2)+pow(yy,2)+pow(zz,2))  #distance between two points