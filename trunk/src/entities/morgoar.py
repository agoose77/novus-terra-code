import entities
import sudo
import bge, random
import tweener
import time
import game
from finite_state_machine import FiniteStateMachine
from mathutils import *
""" editor properties:
 - dialogue - a string of the dialogue file, minus the path and file extension
 """


class Morgoar(entities.EntityBase):
	""" A simple entity for talking to """
	def __init__(self, packet=None):
		super().__init__(packet)
		
		self.interact_label = 'Talk'
		self.health = 80
		self.faction = -841
		#self.localScale = self.localScale * (1+random.random*.3)
		self.update_time = time.time() + random.random()
		self.ticker = 1.0
		self.ai_state = None
		self.alert_radius = 80
		self.target_enemy = None 
		self.alerted = False

		self.path = 0.0
		self.speed = 5

		# Animations
		self.animations = {
			'walk':0,
			'run':0,
			'attack':0,
			'reload':0,
			'idle':1,
			'cround':0
			}

		# FSM States
		self.movement_state_machine = FiniteStateMachine(self)
		self.movement_state_machine.add_state('idle', self.handle_idle_state)
		self.movement_state_machine.add_state('walk', self.handle_walk_state)
		self.movement_state_machine.add_state('attack', self.handle_attack_state)
		self.movement_state_machine.add_state('dead', self.handle_dead_state)
		self.movement_state_machine.current_state = "idle"

		# FSM Transitions
		self.movement_state_machine.add_transition('idle', 'walk', self.is_alerted)
		self.movement_state_machine.add_transition_c('attack', 'walk', self.is_close)
		self.movement_state_machine.add_transition_u('dead', self.is_dead)

		#
		self.interact_label = "Morgoar"
		self.interact_icon = None

	def _wrap(self, object1):
		entities.EntityBase._wrap(self, object1)
		self.armature = [child for child in self._data.childrenRecursive if 'Armature' in child][0]
		self.ray_b = [child for child in self._data.childrenRecursive if 'ray_bottom' in child][0]
		self.ray_top = [child for child in self._data.childrenRecursive if 'ray_top' in child][0]

		self._data['entity_base'] = self
		sudo.world.entity_list.append(self)
		print ('ghost init')

	def is_alerted(self, FSM):
		if self.target_enemy != None:
			return True
		else:
			return False

	def is_close(self, FSM):
		dist = self._data.getDistanceTo(self.target_enemy.position)
		if dist < 2.0:
			return True
		else:
			return False

	def is_dead(self, FSM):
		if self.health < 0.0:
			return True
		else:
			return False

	def alert_entity(self, object1):
		self.target_enemy = object1

	def on_interact(self, player):
		pass


	### ANIMATIONS ###
	def play_animation(self,name):
		self.animations[name] = 1

	def stop_animation(self, layer):
		for n in range(0,7):
			if n != layer:
				self.armature.stopAction(n)

	def handle_animations(self):
		if self.animations['attack'] == 1:
			self.armature.playAction("m_attack", 1, 32, layer=2, priority=2, blendin=5, play_mode=bge.logic.KX_ACTION_MODE_LOOP, speed=1.0)
			self.stop_animation(2)

		elif self.animations['walk'] == 1:
			self.armature.playAction("m_walk", 1, 30, layer=1, priority=2, blendin=5, play_mode=bge.logic.KX_ACTION_MODE_LOOP, speed=1.0)
			self.stop_animation(1)

		else:
			self.armature.playAction("m_idle", 1, 30, layer=0, priority=2, blendin=5, play_mode=bge.logic.KX_ACTION_MODE_LOOP, speed=1.0)
			self.stop_animation(0)

		for name in self.animations:
			self.animations[name] = 0


	def handle_dead_state(self, FSM):
		pass

	def handle_attack_state(self, FSM):
		st = self.controllers[0].actuators['Steering']
		st.velocity = 0.0
		target = self.target_enemy
		self.track(target.position)
		target.damage(10)
		self.play_animation("attack")

	def handle_walk_state(self, FSM, behavior=3, offset=0, speed='walk'):
		if speed == 'walk':
			speed = self.speed
		elif speed == 'run':
			speed = self.speed*2
		
		self.navmesh = bge.logic.getCurrentScene().objects['Navmesh_box']
		self.path = self.navmesh.findPath(self.position, self.target_enemy.position)
		self.path_index = 0
		
		if len(self.path) > 0:
			current_node = self.path[self.path_index]
			dist = self._data.getDistanceTo(current_node)

			if dist < 1.0:
				self.path_index += 1

			self.track(self.path[self.path_index])
			self.localLinearVelocity = [0.0,speed,0.0]
			self.play_animation("walk")

	def handle_idle_state(self, FSM):
		self.play_animation("idle")
		entities = sudo.world.entity_list

		enemy_list = []
		"""

		for entity in entities:
			try:
				faction = entity.faction
			except:
				faction = self.faction
			
			if faction != self.faction:
				dist = self._data.getDistanceTo(entity._data)

				if dist < 35:
					ray = self._data.rayCast(entity.position, self.position, 0,'',0,0,0)

					if ray[0] == entity._data:
						enemy_list.append([dist, entity])

		enemy_list.sort()

		if len(enemy_list) > 0:
			self.target_enemy = enemy_list[0][1]
		else:
			self.target_enemy = None
			"""

		self.target_enemy = sudo.player

	def track(self, target, speed=1.0):
		vec = self.getVectTo(target)
		self.alignAxisToVect(vec[1], 1, speed)
		self.alignAxisToVect([0,0,1], 2, speed)

	def damage(self, amount, obj):
		self.health = self.health - amount

		### Mist
		#new = bge.logic.getCurrentScene().addObject("blood_mist",'CELL_MANAGER_HOOK',5)
		#new.position = self._data.position
		

		### Splatter
		ray = self._data.rayCast(self.ray_b, self.ray_top, 0, 'Ground',0,1,0)
		#index = random.randrange(0,len(blood_textures))

		#if ray[0] != None:
		#	blood_textures = ["Blood", "Blood_2"]
		#	index = random.randrange(0,len(blood_textures))

		"""
			new = bge.logic.getCurrentScene().addObject(blood_textures[index],'CELL_MANAGER_HOOK',2500)
			new.position = ray[1]+Vector([0.0,0.0,0.05])

			ran = random.randrange(0.0,10.0)
			new.orientation = new.orientation*Vector([0.0,0.0,ran])
			"""


		if self.health < 0.0:
			chunks = ["morgoar_chunk","morgoar_chunk.001","morgoar_chunk.002","morgoar_chunk.003","morgoar_chunk.004","morgoar_chunk.005","morgoar_chunk.006","morgoar_chunk.007","morgoar_chunk.008","morgoar_chunk.009"]
			
			md = bge.logic.getCurrentScene().addObject("morgaor_death",'CELL_MANAGER_HOOK',50)
			md.position = self._data.position

			for chunk in chunks:
				c = bge.logic.getCurrentScene().addObject(chunk,'CELL_MANAGER_HOOK',2500)
				c.position = self._data.position
				
				for child in md.children:
					if "prop" in child:
						if child['prop'] == chunks[chunks.index(chunk)]:
							c.position = child.position
							c.orientation = child.orientation

			if ray[0] != None:
				new = bge.logic.getCurrentScene().addObject("Blood_floor",'CELL_MANAGER_HOOK')
				new.position = ray[1]+Vector([0.0,0.0,0.05])

				ran = random.randrange(0.0,100.0)
				new.orientation = new.orientation*Vector([0.0,0.0,ran])

			self.remove()

	def update(self):
		self.movement_state_machine.main()
		self.handle_animations()
