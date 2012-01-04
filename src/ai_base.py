import math
import random
import sys
sys.path.append('./src/')
sys.path.append('./src/bgui/')

import aud
import bge
from mathutils import Vector, Matrix

import entities

import game
import ui
from entities import EntityBase
from finite_state_machine import FiniteStateMachine
from inventory import Inventory
from paths import PATH_SOUNDS, PATH_MUSIC
from sound_manager import SoundManager


### 
class AIBase(EntityBase):

	def __init__(self, object_name):

		### INIT ###
		print("AIBase.__init__()")
		entities.EntityBase.__init__(self, None)
		entities.EntityBase._wrap(self, object_name)

		# Stats
		self.health = 100
		self.speed = 100
		self.faction = -1

		# AI INFO
		self.reloading = False
		self.last_shot = 0.0
		self.cover_timer = 101
		self.in_cover = False

		# Need These?
		self.object_name = object_name


		# Entity Info
		self.allies = []
		self.enemies = []
		self.target = None
		self.target_last_pos = None
		self.target_in_sight = False


		### Alert Info ###
		self.alert_position = None
		self.alerted = 0

		# Self alert info
		self.alert = 0
		self.sighted = 0
		self.impatience = 0

		#
		self.animations= []
		self.ryn = random.randrange(-5,5)
		self.rxn = random.randrange(-5,5)

		# Inventory
		self.current_weapon= None
		self.current_weapon_clip = 50
		self.inventory = Inventory()

		# Pathfinding
		self.target_entity = None
		self.navmesh = None
		self.object = None
		
		# Children
		self.armature = [child for child in self.childrenRecursive if 'Armature' in child][0]
		self.target_obj = [child for child in self.childrenRecursive if 'target_obj' in child][0]
		self.target_obj.removeParent()

		self.aimer = [child for child in self.childrenRecursive if 'aimer' in child][0]
		self.bullet_spread = [child for child in self.childrenRecursive if 'spread' in child][0]
		self.weapon_pos = [child for child in self.childrenRecursive if 'weapon_pos' in child][0]



		### FSM ###
		self.ai_state_machine = FiniteStateMachine(self)
		self.ai_state_machine.add_state('handle_cover', self.handle_cover)
		self.ai_state_machine.add_state('handle_no_cover', self.handle_no_cover)
		self.ai_state_machine.add_state('dead', self.handle_dead)
		self.ai_state_machine.add_transition('handle_no_cover', 'handle_cover', self.is_in_cover)

		#self.ai_no_cover_state_machine = FiniteStateMachine(self)
		#self.ai_no_cover_state_machine.add_state('engage', self.handle_no_cover_engage)

		#self.ai_cover_state_machine = FiniteStateMachine(self)
		#self.ai_cover_state_machine.add_state('engage', self.handle_cover_engage)



		# Hacks...
		self.ai_state_machine.current_state = 'handle_no_cover'

		# Weapon
		temp_weap = __import__("weapon_pickup")
		temp_weap = temp_weap.WeaponPickup(None, 'INFO:NONE', "P90")
		temp_weap.on_interact(self)

	def _unwrap(self):
		EntityBase._unwrap(self)




	""" FSM States """

	### NO COVER ###
	def handle_no_cover(self, FSM):
		print("Out of Cover")
		ran = random.randrange(1,10)


		# Take Cover!!!
		if self.cover_timer > 100:
			self.cover = self.find_best_cover()
			self.cover_timer = 0

		# If Target Found
		if self.target != None:
			dist = self.getDistanceTo(self.target.position)

			# Sighted
			if self.is_in_sight(self.target._data.name) == True:
				self.target_last_pos = self.target._data.position.copy()
				self.target_in_sight = True

				if self.impatience > 0:
					self.impatience += -0.005

			else:
				self.target_in_sight = False
				self.impatience += 0.01

				### Move into Cover
				if ran > 3:
					#self.ai_state_machine.current_state = 'handle_cover'
					self.in_cover = 1
					print("MOVING TO COVER")

			if self.impatience > 100.0:
				self.target = None


			# If everything is Vaild.  I'll clean this up
			if self.target != None and self.target_last_pos != None:
			
				# Far away -> move closer
				if dist > 200:
					self.move_to(self.target_last_pos, offset = 1)


				# Close enough
				else:
					if self.is_in_sight(self.target._data.name) == True:
						self.attack()
						self['Steer'] = 0
						#self.sighted = 1
						self.target_in_sight = True

					# Search For Target
					else:
						self.move_to(self.target_last_pos, offset = 1)



	### IN COVER ###
	def handle_cover(self, FSM):
		print("In Cover")
		self.move_to(self.cover.position, offset = 0)
		self.cover_timer += 1

		# Sighted
		if self.is_in_sight(self.target._data.name) == True:
			self.target_last_pos = self.target._data.position.copy()
			self.target_in_sight = True

			if self.impatience > 0:
				self.impatience += -0.005

		else:
			self.target_in_sight = False
			self.impatience += 0.01
 

	### DEAD ###
	def handle_dead(self, FSM):
		print("Dead!!!")
		self['Steer'] = 0





	### DONT NEED!!!
	def handle_idle(self, FSM):
		self['Steer'] = 0
		self.armature.playAction("pistol_idle", 1, 32, layer=1, priority=0, blendin=0, play_mode=bge.logic.KX_ACTION_MODE_LOOP, speed=1.0)

	def handle_talk(self, FSM):
		self['Steer'] = 0
		self.armature.playAction("pistol_idle", 1, 32, layer=1, priority=0, blendin=0, play_mode=bge.logic.KX_ACTION_MODE_LOOP, speed=1.0)

	def handle_flee(self, FSM):
		self.move_to(behavior=1)
		self.armature.playAction("pistol_run", 1, 32, layer=1, priority=0, blendin=0, play_mode=bge.logic.KX_ACTION_MODE_LOOP, speed=1.0)


	""" Misc Functions """
	def move_to(self, target_pos, behavior=3, offset=0, speed=2):

		# Stuff
		st = self.controllers[0].actuators['Steering']
		st.behaviour = behavior

		# Speed
		st.velocity = speed
		st.acceleration = 0.5
		st.turnspeed = 10

		# Offset Target
		if offset == 1:
			ry = target_pos[0] + self.ryn
			rx = target_pos[1] + self.rxn
		else:
			ry = target_pos[0]#self.target.position[0] + self.ryn
			rx = target_pos[1]#self.target.position[1] + self.rxn

		self.target_obj.position = [ry, rx, target_pos[2]]
		st.target = self.target_obj

		st.navmesh = bge.logic.getCurrentScene().objects['Navmesh1']

		# Activate it
		self['Steer'] = 1
		self.armature.playAction("pistol_walk", 1, 33, layer=5, priority=1, blendin=5, play_mode=bge.logic.KX_ACTION_MODE_LOOP, speed=1.0)

		###
		dist = self.getDistanceTo(st.target)


		return bool(dist < 4)


	def defend(self):
		self.track()
		self.armature.playAction("crouch", 1, 33, layer=5, priority=1, blendin=5, play_mode=bge.logic.KX_ACTION_MODE_LOOP, speed=1.0)


	def attack(self):
		#vec = self.getVectTo(self.target_last_pos)
		#self.bullet_spread.alignAxisToVect(-vec[1], 1, 0.5)
		#self.bullet_spread.alignAxisToVect([0,0,1], 2, 1)



		ray = self.bullet_spread.controllers[0].sensors['weapon_ray']
		ray.range = 200#self.current_weapon.range
		hit = ray.hitObject

		# Look towards target
		self.track()


		# Reload
		if self.inventory.weapon_slot_1.clip == 0:
			self.reloading = True

		# Shoot
		else:
			if self.reloading == False:
				if (game.Game.singleton.game_time - self.last_shot) > self.inventory.weapon_slot_1.fire_speed:
					self.last_shot = game.Game.singleton.game_time

					self.inventory.weapon_slot_1.shoot(self.aimer, self.bullet_spread)
					#self.play_animation('shoot')

					self.target.alert_entity(self)

					if hit != None:
						new = bge.logic.getCurrentScene().addObject('B_Hole', self.aimer, 100)
						new.position = ray.hitPosition
						new.alignAxisToVect(ray.hitNormal, 2, 1.0)
						new.setParent(hit)

						if 'physics' in hit:
							hit['physics'] = 1

						if 'ai_controller' in hit:
							hit['ai_controller'].damage(10, self._data)


						if 'player' in hit:
							game.Game.singleton.world.player.damage(10)


	""" """
	def find_best_cover(self):
		#covers = self.find_covers()

		###
		scene = bge.logic.getCurrentScene()
		temp = []

		for obj in scene.objects:
			if 'cover' in obj:
				dist = self.getDistanceTo(obj)
				if self.target != None:
					dist2 = self.target.getDistanceTo(obj)
				else:
					dist2 = 0
				
				temp_d = {"ai_dist":dist, "object":obj, "player_dist":dist2}
				temp.append(temp_d)

		covers = sorted(temp, key=lambda k: k['ai_dist'])

		###
		best = covers[0]
		index = 0
		cover = None

		# Find Best Cover
		for cov in covers:

			# If Cover is in range
			if cov['ai_dist'] < 250:

				# If Cover is closer than prev best
				if cov['player_dist'] < best['player_dist']:

					# If cover isn't in sight of player
					ray_cover = self.rayCast(self.target.position, cov['object'].position, 0,'',0,0,0)

					if ray_cover[0].name != self.target.name:
						best = cov
			
			cover = best['object']

		return cover


	def find_target(self):
		if len(self.enemies) > 0:
			self.target = self.enemies[0][1]
		else:
			self.target = None

	def update_enitity_list(self):
		self.allies = []
		self.enemies = []
		entity_list = []
		entity_index = 0

		radar = self.aimer.controllers[0].sensors['Radar']

		# Loop through all objects in AI's FOV
		for hit_obj in radar.hitObjectList:
			temp_entity_list = [temp for temp in game.Game.singleton.world.entity_list if temp._data == hit_obj]
			if len(temp_entity_list) > 0:
				entity_list.append(temp_entity_list[0])

		# IF entity seen
		if len(entity_list) > 0:
			for obj in entity_list:

				# IF enemy
				if obj.faction != self.faction:

					ray = self.rayCast(obj.position, self.aimer.position, 0, '', 0, 0, 0)
					#print(ray[0])

					# If in sight
					if ray[0].name == obj._data.name:
						dist = self.getDistanceTo(obj.position)
						self.enemies.append([dist, obj])

						# Switch to Alert
						self.alert = 1

				# Good guy
				else:
					self.allies.append(obj)

		self.enemies.sort()

	def alert_entities(self):
		for temp in game.Game.singleton.world.entity_list:
			temp.alerted = 1
			temp.alert_position = self.position.copy()

	def track(self):
		vec = self.getVectTo(self.target_last_pos)
		self.alignAxisToVect(-vec[1], 1, 0.1)
		self.alignAxisToVect([0,0,1], 2, 0.1)

	def damage(self, damage_amount, object):
		print("HIT")
		self.target = object
		self.target_last_pos = self.target.position.copy()
		self.health += -damage_amount
		#self.track()
		self.ai_state_machine.current_state = 'handle_no_cover'

		# IF dead
		if self.health < 0:
			print("DEAD!!!")
			self.endObject()

	def alert_entity(self, object):
		self.target = object
		self.target_last_pos = self.target.position.copy()
		self.track()
		self.ai_state_machine.current_state = 'handle_no_cover'


	""" Checks """
	def is_scared():
		return False

	def is_in_cover(self, FSM):
		return bool(self.in_cover)

	def is_dead(self, FSM):
		if self['Health'] < 0:
			return True
		else:
			return False

	def is_enemy_near(self, FSM):
		enemies = self.detect_enemies()
		return bool(enemies != None)

	def is_fleeing(self, FSM):
		moral = 0
		moral += -len(self.enemies)
		moral += len(self.allies)
		moral += -(self.health - 100)*0.25
		return False

	def is_in_sight(self, target):
		sight = False
		radar = self.aimer.controllers[0].sensors['Radar']

		for hit_obj in radar.hitObjectList:
			if hit_obj.name == target:
				ray = self.rayCast(hit_obj.position, self.aimer.position, 0, '', 0, 0, 0)
				if ray[0].name == target:
					sight = True

		return sight


	""" Animation """
	def play_animation(self,name):
		if name == 'idle':
			self.armature.playAction(str(self.inventory.current_weapon.name) + "_idle", 1, 64, layer=4, priority=1, blendin=5, play_mode=bge.logic.KX_ACTION_MODE_LOOP, speed=1.0)
			self.armature.stopAction(5)
			self.armature.stopAction(6)

		if name == 'shoot':
			self.armature.playAction(str(self.inventory.current_weapon.name) + "_shoot", 1, 5, layer=1, priority=1, blendin=5, play_mode=bge.logic.KX_ACTION_MODE_LOOP, speed=1.0)
			self.armature.stopAction(4)
			self.armature.stopAction(5)
			self.armature.stopAction(6)

		if name == 'reload':
			self.armature.playAction(str(self.inventory.current_weapon.name) + "_reload", 1, 24, layer=2, priority=1, blendin=5, play_mode=bge.logic.KX_ACTION_MODE_LOOP, speed=1.0)
			self.armature.stopAction(5)

		if name == 'walk':
			self.armature.playAction("walk", 1, 32, layer=5, priority=1, blendin=5, play_mode=bge.logic.KX_ACTION_MODE_LOOP, speed=1.0)
			self.armature.stopAction(4)
			self.armature.stopAction(6)

		if name == 'run':
			self.armature.playAction(str(self.inventory.current_weapon.name) + "_run", 1, 64, layer=6, priority=1, blendin=5, play_mode=bge.logic.KX_ACTION_MODE_LOOP, speed=1.0)
			self.armature.stopAction(4)
			self.armature.stopAction(5)


	""" Main """
	def main(self):
		EntityBase.main(self)

		# Update target
		if self.target == None:

			# Update Enemy/Ally list
			self.update_enitity_list()

			# Update Target with the enemy with the highest threat level
			self.find_target()

		self.ai_state_machine.main() # Please turn back on


"""
def mulit_ray_collision_dectction(obj, distance, width):
    # cast 3 rays to preemptively detect collisions
    vecs = [Vector([-width/2, distance, 0]),
            Vector([0, distance, 0]),
            Vector([width/2, distance, 0])]

"""

"""
from mathutils import Vector
 
def limit_velocity(obj, limit):
    # Limit an objects velocity along the xy plane
    vel = obj.worldLinearVelocity
    z = vel.z
    vel.z = 0
    if vel.magnitude > limit:
        vel.magnitude = limit
        vel.z = z
        obj.worldLinearVelocity = vel
 
def within_range(obj, point, distance):
    # Return true when an object is less than distance units away from a point.
    return obj.getDistanceTo(point) < distance
 
def in_sight(obj, target, distance):
    # Return true when a target enters an objects sight cone.
    dis, gvec, lvec = obj.getVectTo(target)
    if not distance < dis:
        angle = lvec.angle(Vector([0,1,0]))
        return math.degrees(angle) < 40
 
def single_ray_collision_detection(obj, distance, width):
    # cast a single ray to preemptively detect collisions
    x = (bge.logic.getRandomFloat()*width) - (width/2)
    vec = Vector([x, distance, 0]) * obj.worldOrientation
    vec = vec + obj.worldPosition
   
    hit_obj, point, normal = obj.rayCast(vec, None, distance)
    return (hit_obj, point, normal)
 
def mulit_ray_collision_dectction(obj, distance, width):
    # cast 3 rays to preemptively detect collisions
    vecs = [Vector([-width/2, distance, 0]),
            Vector([0, distance, 0]),
            Vector([width/2, distance, 0])]
   
    for vec in vecs:
        vec = vec + obj.worldPosition
        vec = vec * obj.worldOrientation
        hit_obj, point, normal = obj.rayCast(vec, None, distance)
        if hit_obj:
            return (hit_obj, point, normal)"""