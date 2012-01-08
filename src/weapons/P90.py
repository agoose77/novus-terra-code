"""
P90 > Weapon > Ranged > Human
"""
import sys
sys.path.append('./src/')

import bge
from mathutils import Vector, Matrix
import random
import game

###
class weapon:
	def __init__(self):
		self.name = "P90"
		self.description = 'A Cool Looking Weapon'

		self.icon = 'cube.png'
		self.weapon_type = 'Pistol'
		self.cost = 0
		self.ran_flash = 1

		self.clip_size = 20
		self.clip = 100
		self.ammo_type = 1
		self.bullet_spread = 5
		self.fire_speed = 0.1
		self.reload_time = 1.0

		# Effects
		self.flash = ['muzzle_flash','muzzle_flash.001','muzzle_flash.002','muzzle_flash.003'] # Different flash effects to cycle
		self.bullet_line = 'bullet_line'
		self.smoke = 'smoke'

		# Sounds
		self.fire_sound = 'weapon_sound_m.ogg'
		self.empty_sound = ''
		self.reload_sound = ''
		self.equip_sound = ''

		# Objects
		self.object = None
		self.armature = None
		self.muzzle = None


	def on_interact(self, entity):
		#entity.inventory.replace_weapon(hit.parent['Weapon'])
		#new = entity.inventory.weapon_slot_1.equip()
		#hit.parent.endObject()
		print("WRONGE!!!!")


	def equip(self, entity):
		name = self.name
		self.entity = entity

		new = bge.logic.getCurrentScene().addObject(name,'CELL_MANAGER_HOOK')
		new.position = entity.weapon_pos.position
		new.orientation = entity.weapon_pos.orientation
		new.setParent(entity.weapon_pos)


		"""
		new = bge.logic.getCurrentScene().addObject(name,'weapon_position')
		new.position = bge.logic.getCurrentScene().objects['weapon_position'].position
		new.orientation = bge.logic.getCurrentScene().objects['weapon_position'].orientation
		new.setParent(bge.logic.getCurrentScene().objects['weapon_position'])
		"""

		# Set Objects
		self.object = new
		self.armature = [child for child in self.object.childrenRecursive if 'Armature' in child][0]
		self.muzzle = [child for child in self.object.childrenRecursive if 'Muzzle' in child][0]

    ###
	def reload(self):
		self.armature.playAction(self.name + "_reload", 1, 24, layer=2, priority=1, blendin=5, play_mode=bge.logic.KX_ACTION_MODE_LOOP, speed=1.0)

	def shoot(self, point, spread):
		self.clip += -1

		#game.Game.singleton.world.entity_list.append(self)
		game.Game.singleton.sound_manager.play_sound(self.fire_sound, self.object)

		### Bullet Spread
		spread['X'] = random.randrange(-self.bullet_spread,self.bullet_spread)
		spread['Z'] = random.randrange(-self.bullet_spread,self.bullet_spread)

		### Bullet Line
		line = bge.logic.getCurrentScene().addObject(self.bullet_line, point, 100)
		line.position = self.muzzle.position
		line.orientation = spread.orientation

		### Flash
		ran_flash = random.randrange(1,4)
		flash = bge.logic.getCurrentScene().addObject(self.flash[ran_flash], point, 5)
		flash.position = self.muzzle.position
		flash.setParent(self.muzzle)

		### Smoke
		smoke = bge.logic.getCurrentScene().addObject(self.smoke, point, 100)
		smoke.position = self.muzzle.position

		###
		#entity = self.entity
		#self.object.position = entity.weapon_pos.position
		#self.object.orientation = entity.weapon_pos.orientation

	###
	def main(self):
		pass