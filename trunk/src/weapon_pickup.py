### Weapon Pickup
import sys
sys.path.append('./src/')

import bge
from mathutils import Vector, Matrix
import random
import session
from entity_base import EntityBase

###
class WeaponPickup(EntityBase):

	def __init__(self, packet=None):
		print ("WeaponPickup.__init__()")
		EntityBase.__init__(self, packet)

		self.iteract_label = 'pickup'
		self.interact_info = "P90 - Weapon"
		self.weapon_name = "P90"

	def on_interact(self, player):
		player.inventory.replace_weapon(self.weapon_name)
		player.inventory.weapon_slot_1.equip()
		self.remove()