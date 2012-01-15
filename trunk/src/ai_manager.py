import math
import sys
sys.path.append('./src/')
sys.path.append('./src/entities/vehicle')
sys.path.append('./src/owyl/')

import bge

import cell
import game
import ui
from ai_base import AIBase
from vehicle_base import VehicleBase

from queue import Queue
from mathutils import Vector, Matrix

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
			
			# TEMP - For Vehicles
			if 'vehicle' in obj.name:
				obj['vehicle'] = 0


	###
	def main(self):
		"""

		# Spawn Points
		for obj in bge.logic.getCurrentScene().objects:
			if 'spawn_point' in obj.name:
				if obj['spawned'] == 0:

					#temp = AIBase()						
					new = bge.logic.getCurrentScene().addObject('ai_base', obj)#.objects['ai_base']
					temp = AIBase(new)

					#temp._wrap(new)
					new['ai_controller'] = temp # BAD!
					temp.position = obj.position
					temp.faction = obj['faction']

					game.Game.singleton.world.entity_list.append(temp)
					self.nodes.put(temp)

					obj['spawned'] = 1


			if 'vehicle' in obj:
				if obj['vehicle'] == 0:

					#temp = AIBase()						
					new = bge.logic.getCurrentScene().addObject('Vehicle.001', obj)#.objects['ai_base']
					temp = VehicleBase(new)

					#temp._wrap(new)
					new['vehicle'] = temp # BAD!
					temp.position = obj.position
					#temp.faction = obj['faction']

					#game.Game.singleton.world.entity_list.append(temp)
					self.nodes.put(temp)

					obj['vehicle'] = 1

		"""

				

		# Cycle
		if self.nodes.empty() == False:

			object1 = self.nodes.get()
			#AIBase.main(object1)
			VehicleBase.main(object1)
			self.nodes.put(object1)