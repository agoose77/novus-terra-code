"""
NPC:  A generic NPC (non player character) class.
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
class NPC2(entities.AIBase):
	def __init__(self, packet, name="AI_Default"):
		super().__init__(packet)

		self.factions = {"Enemies": [2], "Allies": [0, 1, 3]} # Player faction = 0, Human faction = 1, Rebel Faction = 2, Kree Faction = 3

		# UI
		self.interact_label = "NPC"
		self.interact_icon = None


	def _wrap(self, object):
		entities.EntityBase._wrap(self, object)

		# Spread
		self.ryn = random.randrange(-5,5)
		self.rxn = random.randrange(-5,5)

		# Children
		self.armature = [child for child in self.childrenRecursive if 'Armature' in child][0]
		self.aimer = [child for child in self.childrenRecursive if 'aimer' in child][0]
		self.bullet_spread = [child for child in self.childrenRecursive if 'spread' in child][0]
		self.weapon_pos = [child for child in self.childrenRecursive if 'weapon_pos' in child][0] 
		self.head_track = [child for child in self.childrenRecursive if 'head_track' in child][0]

		# Inventory
		self.inventory = Inventory()
		self.inventory.replace_weapon("F2000") # Starting weapon
		self.inventory.primary_weapon.equip(self, weapon_type="3rd")

		# FSM
		self.ai_state_machine = FiniteStateMachine(self)

		self.ai_state_machine.add_state('idle', self.handle_idle)
		self.ai_state_machine.add_state('dead', self.handle_dead)
		self.ai_state_machine.add_state('attack', self.handle_attack)
		self.ai_state_machine.add_state('talk', self.handle_talk)
		#self.ai_state_machine.add_state('move', self.handle_move)

		#self.movement_state_machine.add_transition('attack', self.transition_to_attack)

		self.ai_state_machine.current_state = "idle"

		###
		self._data['entity_base'] = self


	def _unwrap(self):
		EntityBase._unwrap(self)

	def on_interact(self, player):
		#self.ai_state_machine.current_state = "talk" # Disabled
		sudo.world.dialogue_manager.display_dialogue('./data/dialogue/' + 'test' + '.xml')


	""" FSM Transitions """
	def transition_to_attack(self, FSM):
		return self.target_in_sight

	def is_dead(self, FSM):
		if self['Health'] < 0:
			return True
		else:
			return False

	def is_fleeing(self, FSM):
		moral = 0
		moral += -len(self.enemies)
		moral += len(self.allies)
		moral += -(self.health - 100)*0.25
		return False


	""" FSM States """
	def handle_idle(self, FSM):
		self['Steer'] = 0
		self.play_animation("idle")
		
		# Head tracking
		self.track(sudo.player.position, tracker=self.head_track, speed=0.8, track_3d=True)

	def handle_talk(self, FSM):
		self['Steer'] = 0
		self.play_animation("idle")
		sudo.world.dialogue_manager.display_dialogue('./data/dialogue/' + 'test' + '.xml')

	def handle_flee(self, FSM):
		self.move_to(self.target.position)

	def handle_attack(self, FSM):
		# If Target Found
		if self.target:
			self.track(self.target.position, tracker=self.head_track, speed=0.8, track_3d=True)
			dist = self.getDistanceTo(self.target.position)

			# Check if target is in sight
			if self.is_in_sight(self.target.name):
				self.target_last_pos = self.target._data.position.copy()
				self.target_in_sight = True
			else:
				self.target_in_sight = False

			# If everything is Vaild
			if self.target and self.target_last_pos:
			
				# Far away -> move closer
				if dist > 60:
					self.move_to(self.target_last_pos)

				# Close enough to attack
				else:
					self.localLinearVelocity = [0.0,0.0,0.0] # Stop moving

					if self.is_in_sight(self.target.name):
						self.track(self.target.position, speed = 0.25)
						self.track(self.target.position, tracker=self.aimer, speed = 0.85, track_3d=True)
						self.inventory.primary_weapon.ai_fire(self)
						self.target_in_sight = True
						print ("FIRE!!!")

					else:
						self.move_to(self.target_last_pos)


	def handle_dead(self, FSM):
		print("Dead")
		self['Steer'] = 0
		self.remove()

	def find_target(self):
		if self.enemies:
			self.target = self.enemies[0][1]
		else:
			self.target = None

	def alert_entities(self):
		for temp in game.Game.singleton.world.entity_list:
			temp.alerted = 1
			temp.alert_position = self.position.copy()


	def damage(self, damage_amount=1, object=None):
		print("HIT")
		self.target = object
		self.target_last_pos = self.target.position.copy()
		self.health += -damage_amount
		
		if object.faction in self.factions['Allies']:
			index = self.factions['Allies'].index(object.faction)
			self.factions['Allies'].remove(index)


		if not object.faction in self.factions['Enemies']:
			self.factions["Enemies"].append(object.faction)

		# IF dead
		if self.health < 0:
			self.ai_state_machine.current_state = 'dead'

		self.ai_state_machine.current_state = 'attack'

	def alert_entity(self, object):
		self.target = object
		self.target_last_pos = self.target.position.copy()
		self.track(self.target_last_pos)
		self.ai_state_machine.current_state = 'handle_no_cover'


	""" 'Checks' """
	def is_scared():
		return False

	def is_in_cover(self, FSM):
		return bool(self.in_cover)

	def is_enemy_near(self, FSM):
		enemies = self.detect_enemies()
		return bool(enemies != None)

	def is_in_sight(self, target):
		sight = False
		radar = self.aimer.controllers[0].sensors['Radar']

		for hit_obj in radar.hitObjectList:
			if hit_obj.name == target:
				ray = self.rayCast(hit_obj.position, self.aimer.position, 0, '', 0, 0, 0)
				if (ray[0]) and ray[0].name == target:
					sight = True

		return sight


	""" ANIMATIONS """
	def play_animation(self,name):
		self.animations[name] = 1

	def stop_animation(self, layer):
		for n in range(0,7):
			if n != layer:
				self.armature.stopAction(n)

	def handle_animations(self):
		weapon = self.inventory.primary_weapon

		if self.animations['reload'] == 1:
			self.armature.playAction(weapon.name + "_reload_3rd", 1, 64, layer=4, priority=2, blendin=5, play_mode=bge.logic.KX_ACTION_MODE_PLAY, speed=1.0)
			self.stop_animation(4)

		elif self.animations['attack'] == 1:
			self.armature.playAction(weapon.name + "_attack_3rd", 1, 5, layer=3, priority=3, blendin=5, play_mode=bge.logic.KX_ACTION_MODE_PLAY, speed=1.0)
			self.stop_animation(3)

		elif self.animations['walk'] == 1:
			self.armature.playAction(weapon.name + "_walk_3rd", 1, 32, layer=2, priority=2, blendin=5, play_mode=bge.logic.KX_ACTION_MODE_LOOP, speed=1.0)
			self.stop_animation(2)
		
		elif self.animations['run'] == 1:
			self.armature.playAction(weapon.name + "_run_3rd", 1, 20, layer=1, priority=3, blendin=5, play_mode=bge.logic.KX_ACTION_MODE_LOOP, speed=1.0)
			self.stop_animation(1)

		else:
			self.stop_animation(0)
			self.armature.playAction(weapon.name +"_idle_3rd", 1, 64, layer=0, priority=5, blendin=5, play_mode=bge.logic.KX_ACTION_MODE_LOOP, speed=1.0)

		for name in self.animations:
			self.animations[name] = 0


	""" 'Main' """
	def update(self):

		if self._data:
			self.handle_animations()

			# Update target
			if self.target == None:
				self.update_enitity_list() # Update Enemy/Ally list
				self.find_target() # Update Target with the enemy with the highest threat level

			self.ai_state_machine.main()

		else:
			print("NO DATA")