import pickle
import os
import time

import tweener
import terrain
import cell
from entity.hash import *
import sudo
from math import *


try:
	import bge
	import ui
	import mathutils
	from paths import *
except:
	print("BGE imports failed, normal if you are running the cell editor")



class EntityManager:
	'''  future: handles reading entities from cells, loading entity sets for cells, entity spawning and neighbor lookups'''
	def __init__(self):
		print('EntityManager.__init__()')
		self.hash = Hash(30)
		self.in_play = []
		self.dist = 200
		self.old_found = []


	def update(self):
		if sudo.world.KX_player:
			found = self.hash.neighbors(sudo.world.KX_player.position, self.dist)

			for entity in found:
				if entity in self.old_found:
					self.old_found.remove(entity)
				else:
					if not entity._data:
						if entity.packet:
							ob = sudo.cell_manager.spawn_prop(entity.packet)
							entity._wrap( ob )
			for entity in self.old_found:
				entity._unwrap()
				
				
			self.old_found = found

			#if self.get_distance(sudo.world.KX_player.position, entity.location) < self.dist*.8:

	def get_distance( self, location1, location2 ):
		location1 = list(location1)
		location2 = list(location2)
		xx=location1[0]-location2[0]
		yy=location1[1]-location2[1]
		zz=location1[2]-location2[2]
		return sqrt(pow(xx,2)+pow(yy,2)+pow(zz,2))  #distance between two points