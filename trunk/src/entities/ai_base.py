"""
AIBase:  A generic AI class.
"""

import bge
import sys
import random
from mathutils import Vector, Matrix


import sudo
import game
import entities
from entities import EntityBase
from inventory import Inventory
from finite_state_machine import FiniteStateMachine

### Paths
sys.path.append('./src/')
sys.path.append('./src/bgui/')

### 
class AIBase(entities.Actor):
	def __init__(self, packet, name="AI_Default", health=100, walk_speed=4,run_speed=7,faction=1):
		super().__init__(packet)

		# Stats
		self.health = health
		self.walk_speed = walk_speed
		self.run_speed = run_speed

		self.faction = faction
		#self.factions = {"Enemies": [2], "Allies": [0, 1, 3]} # Player faction = 0, Human faction = 1, Rebel Faction = 2, Kree Faction = 3

		# Situation info
		self.allies = []
		self.enemies = []
		self.target = None
		self.target_last_pos = None
		self.target_in_sight = False

		# Alert info
		self.alert_position = None
		self.alerted = 0
		self.alert = 0
		self.impatience = 0

		# Pathfinding
		self.navmesh = None
		self.node_position = None

		# Animations
		self.animations = {
			'walk':0,
			'run':0,
			'attack':0,
			'reload':0,
			'idle':1,
			'cround':0
			}


	def on_interact(self, player):
		""" Override this method """
		pass

	def update_enitity_list(self):
		self.allies = []
		self.enemies = []
		entity_list = []

		radar = self.aimer.controllers[0].sensors['Radar']

		# Loop through all objects in AI's FOV
		for hit_obj in radar.hitObjectList:
			temp_entity_list = [temp for temp in game.Game.singleton.world.entity_list if temp._data == hit_obj]
			if len(temp_entity_list) > 0:
				entity_list.append(temp_entity_list[0])

		# If entity seen
		if entity_list:
			for obj in entity_list:

				# if faction is in enemy 
				if obj.faction != self.faction:

					ray = self.rayCast(obj.position, self.aimer.position, 0, '', 0, 0, 0)

					#
					if ray[0].name == obj._data.name:
						dist = self.getDistanceTo(obj.position)
						self.enemies.append([dist, obj])

						# Alerted
						self.alert = 1

				# Same faction
				else:
					self.allies.append(obj)

		self.enemies.sort()

	def track(self, target, tracker=None,speed=0.1, track_3d=False):		
		if not tracker:
			tracker = self

		vec = tracker.getVectTo(target)

		if track_3d:
			tracker.alignAxisToVect(vec[1], 1, speed)

		else:
			tracker.alignAxisToVect(vec[1], 1, speed)
			tracker.alignAxisToVect([0,0,1], 2, speed)

	def damage(self, damage_amount=1, object=None):
		""" Override this method """
		pass


	""" ANIMATIONS """
	def play_animation(self,name):
		self.animations[name] = 1

	def stop_animation(self, layer):
		for n in range(0,7):
			if n != layer:
				self.armature.stopAction(n)

	def handle_animations(self):
		""" Override this method """
		pass

	def main(self):
		super().main()