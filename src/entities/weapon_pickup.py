### Weapon Pickup
import sys
import random
sys.path.append('./src/')

import bge
from mathutils import Vector, Matrix

import entities

###
class WeaponPickup(entities.EntityBase):

	def __init__(self, packet=None):
		print ("WeaponPickup.__init__()")
		entities.EntityBase.__init__(self, packet)

		self.iteract_label = 'pickup'
		self.interact_info = "P90 - Weapon"
		self.weapon_name = "P90"

	def on_interact(self, player):
		player.inventory.replace_weapon(self.weapon_name)
		player.inventory.weapon_slot_1.equip()
		self.remove()