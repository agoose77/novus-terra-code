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
class AI_Manager():

	def __init__(self):
		self.nodes = Queue()
		self.index = 0
		self.debug = False

		for obj in bge.logic.getCurrentScene().objects:
			if 'spawn_point' in obj.name:
				temp = AIBase()
				temp.position= obj.position
				self.nodes.put(temp)


	###
	def main(self):
		object = self.nodes.get()
		AIBase.main(object)
		self.nodes.put(object)





