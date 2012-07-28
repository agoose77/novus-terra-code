try:
	import bge
	import game
except ImportError:
	print('Unable to import bge, normal if running editor')

import mathutils
from mathutils import *
import random

import sudo
import weapons



class Gun(weapons.WeaponBase):
	""" Base class for conventional guns """
	def __init__(self, grid_id, name, gun_name, attack_sound, damage=1.0, 
				rate_of_fire=10.0,range=200, zoom_lens=16.0, clip_size=10, reload_time=2.0, 
				burst=0, ammo_id='', animations={}):
		super().__init__(grid_id)

		self.name = name  # The name (label) of the gun
		self.gun_name = gun_name  # The name of the bge object to add
		self.damage = damage
		self.zoom_lens = zoom_lens # The camera lens value when zooming
		self.rate_of_fire = rate_of_fire  # Bullets per second
		self.clip_size = clip_size # Weapon clip size
		self.range = range  # Distance that bullets do damage within
		self.reload_time = reload_time
		self.burst = burst  # number of bullets to fire in each burst
		self.ammo_id = ammo_id  # the id of the item to use for ammo
		self.recoil_min_x = -0.05
		self.recoil_max_x = -0.01
		self.recoil_min_y = -0.005
		self.recoil_max_y = 0.005

		self.fired_in_burst = 0  # number of bullets fired in current burst sofar
		self.reload_start_time = 0.0  # the time that the reload was started
		self.in_clip = clip_size  # number of bullets in the current clip
		self.last_fire = 0.0  # The time when the gun was last fired

		self.entity = None  # The entity which the weapon is equipped to

		self.gun_ob = None  # The actual bge object of the gun
		self.gun_muzzle = None  # The bge object to create muzzle flashes at
		self.gun_arm = None  # The bge armature attached to the gun

		self.components = {} # Weapon customizations
		self.attack_sound = attack_sound
		self.reloading = False

		self.animations = animations

	def check_fire(self):
		""" Check all conditions for firing the gun are met """
		if ((self.fired_in_burst <= self.burst or self.burst == 0) and
				self.in_clip > 0 and
				not self.reloading and
				self.last_fire + (1 / self.rate_of_fire) < sudo.game.game_time):
			return True

		return False

	def reload(self):
		""" Reload the gun """
		if self.reload_start_time == 0.0:
			self.reload_start_time = sudo.game.game_time
			self.entity.play_animation('reload')
			self.gun_arm.playAction(self.name + "_reload", 1, 60, layer=2, priority=1, blendin=1, play_mode=bge.logic.KX_ACTION_MODE_LOOP, speed=1.0)
			self.reloading = True

		elif self.reload_start_time + self.reload_time < sudo.game.game_time:
			self.reload_start_time = 0.0
			self.in_clip = self.clip_size
			self.reloading = False

		self.entity.play_animation('reload')

	def fire(self, point1, point2):
		""" Fire the weapon,

		point1 and point2 are points that the bullet passes through """
		print ("FIre!")
		self.last_fire = sudo.game.game_time
		self.fired_in_burst += 1
		self.in_clip -= 1

		# Light Flash
		fp = bge.logic.getCurrentScene().objects['flashpoint']
		fp.position = self.gun_muzzle.position + (Vector([10.0,0.0,0.0])*self.gun_muzzle.worldOrientation)
		fp['prop'] = 3.4

		# Cast the ray
		hit_ob, hit_pos, hit_norm = self.gun_muzzle.rayCast(point2, point1, self.range)

		scn = bge.logic.getCurrentScene()

		# Add muzzle flash
		flash = scn.addObject('muzzle_flash', self.gun_muzzle, 5)
		flash.position = self.gun_muzzle.position
		flash.setParent(self.gun_muzzle)

		# Add the bullet trail
		trail = scn.addObject('bullet_line', 'CELL_MANAGER_HOOK', 150)
		trail.worldPosition = self.gun_muzzle.worldPosition
		trail.alignAxisToVect(point2 - point1, 1, 1)

		# Add the bullet hole
		if hit_ob:
			for material in hit_ob.meshes[0].materials:
				material = str(material)

				if "dust" in material:
					hole = bge.logic.getCurrentScene().addObject('B_Hole', 'CELL_MANAGER_HOOK', 750)
				if "flesh" in material:
					hole = bge.logic.getCurrentScene().addObject('B_Hole', 'CELL_MANAGER_HOOK', 750)
				else:
					hole = bge.logic.getCurrentScene().addObject('B_Hole', 'CELL_MANAGER_HOOK', 750)

		else:
			hole = bge.logic.getCurrentScene().addObject('B_Hole', 'CELL_MANAGER_HOOK', 750)

		
		hole.position = hit_pos
		hole.alignAxisToVect(hit_norm, 2, 1.0)

		ran_size = random.randrange(10,30)
		ran_size = ran_size/10
		hole.localScale = [ran_size,ran_size,ran_size]


		# Deal damanage to hit object
		if hit_ob:
			if 'entity_base' in hit_ob:
				hit_ob['entity_base'].damage(self.damage, self.entity)
			if 'physics' in hit_ob:
				hit_ob['physics'] = 1

	def equip(self, entity, weapon_type="1st"):
		self.entity = entity

		# Add the gun model
		self.gun_ob = bge.logic.getCurrentScene().addObject(self.gun_name, 'CELL_MANAGER_HOOK')

		if weapon_type == "3rd":
			self.gun_ob.localScale = [1.5,1.5,1.5]

		self.gun_ob.worldPosition = self.entity.weapon_pos.worldPosition
		self.gun_ob.worldOrientation = self.entity.weapon_pos.worldOrientation
		self.gun_ob.setParent(self.entity.weapon_pos)

		# Grab some references to different parts of the gun
		self.gun_arm = [child for child in self.gun_ob.childrenRecursive if 'Armature' in child][0]
		self.gun_muzzle = [child for child in self.gun_ob.childrenRecursive if 'Muzzle' in child][0]

	def unequip(self, entity):
		self.entity = None

		self.gun_ob.endObject()

		self.gun_ob = None
		self.gun_muzzle = None
		self.gun_arm = None

	def play_anim(self, anim):
		""" Override this method to play the right animation """
		pass

	def update_(self):
		pass

	def main(self):
		mouse = bge.logic.mouse
		if mouse.events[bge.events.LEFTMOUSE] == bge.logic.KX_INPUT_JUST_RELEASED:
			self.fired_in_burst = 0

		if (mouse.events[bge.events.LEFTMOUSE] == bge.logic.KX_INPUT_ACTIVE and
			self.check_fire()):
				self.entity.recoil_time = sudo.world.world_time
				self.entity.play_animation('shoot')
				self.entity.recoiled = False

				bullet_spread = sudo.player.bullet_spread
				ray = bullet_spread.controllers[0].sensors['weapon_ray']
				ray.range = self.range

				self.fire(bullet_spread.worldPosition,
						bullet_spread.worldPosition + mathutils.Vector(ray.rayDirection))

		if self.reloading or bge.logic.keyboard.events[bge.events.RKEY] == bge.logic.KX_INPUT_JUST_ACTIVATED:
			self.reload()
