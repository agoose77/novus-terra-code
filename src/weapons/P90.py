"""
P90 > Weapon > Ranged > Human
"""
import sys
sys.path.append('./src/')

import bge
from mathutils import Vector, Matrix
import session

###
class weapon:

	def __init__(self):
		self.name = "P90"
		self.description = 'Bla Bla'

		self.icon = 'cube.png'
		self.weapon_type = 'Pistol'
		self.cost = 0

		self.clip_size = 20
		self.clip = 100
		self.ammo_type = 1
		self.bullet_spread = 5

		# Effects
		self.flash = 'muzzle_flash'
		self.bullet_line = 'bullet_line'

		# Sounds
		self.fire_sound = 'shoot_temp.ogg'
		self.empty_sound = ''
		self.reload_sound = ''
		self.equip_sound = ''

	def finish(self, obj):
		self.object = obj
		self.armature = [child for child in self.object.childrenRecursive if 'Armature' in child][0]
		self.muzzle = [child for child in self.object.childrenRecursive if 'Muzzle' in child][0]

	def equip(self):
		name = self.name

		new = bge.logic.getCurrentScene().addObject(name,'weapon_position')
		new.position = bge.logic.getCurrentScene().objects['weapon_position'].position
		new.orientation = bge.logic.getCurrentScene().objects['weapon_position'].orientation
		new.setParent(bge.logic.getCurrentScene().objects['weapon_position'])

		#
		self.finish(new)

		# Finished
		print ('Equiped')
		return new

    ###
	def reload(self):
		pass

	def shoot(self):
		self.clip += -1
		session.game.sound_manager.play_sound(self.fire_sound, self.object)

	###
	def main(self):
		pass