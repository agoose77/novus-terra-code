import sys
sys.path.append('./src/')
sys.path.append('./src/owyl/')

import math
import bge
import cell
from queue import Queue
from mathutils import Vector, Matrix
from ai_base import AIBase
import ui

###
class AI_Manager:

	def __init__(self):
		self.nodes = Queue()
		self.index = 0
		self.debug = False

		for obj in bge.logic.getCurrentScene().objects:
			if 'spawn_point' in obj.name:
				temp = AIBase()
				temp.position= obj.position
				#game.world.entity_list.append(temp)
				self.nodes.put(temp)


	###
	def main(self):
		print("YP")
		if self.nodes.empty() == False:

			object1 = self.nodes.get()
			AIBase.main(object1)
			self.nodes.put(object1)