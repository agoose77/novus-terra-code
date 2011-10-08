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

#import game
#from game import Game
import session

###
class AI_Manager:

	def __init__(self):
		self.nodes = Queue()
		self.index = 0
		self.debug = False

		# Hack
		for obj in bge.logic.getCurrentScene().objects:
			if 'spawn_point' in obj.name:
				obj['spawned'] = 0


	###
	def main(self):

		# Spawn Points
		for obj in bge.logic.getCurrentScene().objects:
			if 'spawn_point' in obj.name:
				if obj['spawned'] == 0:
					temp = AIBase()
					temp._wrap(bge.logic.getCurrentScene().objects['ai_base'])
					temp.position = obj.position

					session.game.world.entity_list.append(temp)
					self.nodes.put(temp)

					obj['spawned'] = 1

		# Cycle
		if self.nodes.empty() == False:

			object1 = self.nodes.get()
			AIBase.main(object1)
			self.nodes.put(object1)