### Weapon Pickup
import sys
import random
sys.path.append('./src/')

import bge
from mathutils import Vector, Matrix

import entities

###
class WeaponPickup(entities.EntityBase):

	def __init__(self, object, info, name, packet=None):
		print ("WeaponPickup.__init__()")
		if object != None:
			entities.EntityBase.__init__(self, packet)

		self.iteract_label = 'pickup'
		self.interact_info = info
		self.weapon_name = name

	def on_interact(self, entity):
		entity.inventory.replace_weapon(self.weapon_name)
		entity.inventory.weapon_slot_1.equip(entity)
		#self.remove()