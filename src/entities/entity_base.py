import inspect

import mathutils
import sudo
import sys
import tweener

try:
	import bge
	import cell
	import game
	import session
except:
	print('bge import failed, normal if you are running an editor')

def to_entity_base(val):
	if isinstance(val, list):
		for n in range(len(val)):
			if isinstance(val[n], bge.types.KX_GameObject):
				if 'entity_base' in val[n]:
					val[n] = val[n]['entity_base']
	elif isinstance(val, bge.types.KX_GameObject):
		if 'entity_base' in val:
			val = val['entity_base']
	return val

def from_entity_base(val):
	if isinstance(val, list):
		for n in range(len(val)):
			if isinstance(val[n], EntityBase):
				val[n] = val[n]._data
	elif isinstance(val, EntityBase):
		val = val._data
	return val

class method_wrapper:
	def __init__(self, f):
		self.f = f

	def __call__(self, *args, **kwargs):
		return to_entity_base(self.f(*args, **kwargs))

class EntityBase:
	""" Base object for classes representing game objects.

	Maps KX_GameObject functions to the inheriting class."""

	_kx_game_object_descriptors = []
	_kx_game_object_methods = []

	for name_, value_ in inspect.getmembers(bge.types.KX_GameObject):
		# is property
		if inspect.isdatadescriptor(value_):
			_kx_game_object_descriptors.append(name_)

		# is method
		elif inspect.isroutine(value_) and not name_.startswith('__'):
		   _kx_game_object_methods.append(name_)

	def __init__(self, packet=0):
		#packet is the Entity instance from the cell
		self.packet = packet
		self._data = None

		self.stored_linear_velocity = [0,0,0]
		self.stored_angular_velocity = [0,0,0]
		self.stored_position = [0,0,0]
		self.stored_rotation = [[1,0,0], [0,1,0], [0,0,1]]
		self.frozen = False

		self.iteract_icon = None
		self.iteract_label = None

		self.in_hash = False
		self.old_location = False
		if type(self.packet) != int:
			self.location = self.packet.co
		else:
			self.location = False

		try:
			sudo.entity_manager.insert(self)
			self.in_hash = True
		except:
			print(sys.exc_info()[0])

	def update(self):
		''' meant to be overidden '''
		pass

	def damage(self, damage_amount=1, object=None):
		''' meant to be overidden '''
		pass

	def main(self):
		if self._data:
			if not self.frozen:
				self.applyForce(self.mass * game.Game.singleton.world.gravity)
				self.update()


				#this rebalances a sparse hash
				#print(type(self), self.location, self.in_hash)
				if self.location and self.in_hash:
					if self.location != self._data.position:
						sudo.entity_manager.check_move(self, self._data.position)
					self.location = list(self._data.position)

			else:
				self.worldPosition = self.stored_position
				self.worldOrientation = self.stored_rotation

	def on_interact(self, instance):
		if self.frozen:
			self.unfreeze()
		else:
			self.freeze()

	def freeze(self):
		if not self.frozen and self._data:
			self.stored_linear_velocity = self.worldLinearVelocity[:]
			self.stored_angular_velocity = self.worldAngularVelocity[:]
			self.stored_position = self.worldPosition[:]
			self.stored_rotation = self.worldOrientation.copy()

			self.worldLinearVelocity = [0,0,0]
			self.worldAngularVelocity = [0.0001,0.0001,0.0001]

			self.frozen = True

	def unfreeze(self):
		if self.frozen:
			self.worldLinearVelocity = self.stored_linear_velocity
			self.worldAngularVelocity = self.stored_angular_velocity
			self.worldPosition = self.stored_position
			self.worldOrientation = self.stored_rotation

			self.stored_linear_velocity = [0,0,0]
			self.stored_angular_velocity = [0,0,0]
			self.stored_position = [0,0,0]
			self.stored_rotation = [[1,0,0], [0,1,0], [0,0,1]]

			self.frozen = False

	def remove(self):
		""" Removes any references of the entity in the cell and removes the object """
		
		cell.CellManager.singleton.entities_in_game.remove(self)
		cell.CellManager.singleton.cell.entities.remove(self.packet)
		cell.CellManager.singleton.cell.modified = True
		if self.in_hash:
			sudo.entity_manager.remove(self)
		self.packet.game_object = None
		self.endObject()

	def find_navmesh(self):
		""" Returns the closest navmesh or None """
		found_nav = []
		for entry in reversed(sudo.cell_manager.props_in_game):
			for prop in entry:
				print
				if 'navmesh' in prop.game_object:
					found_nav.append(prop.game_object)

		best = False
		if len(found_nav) == 1:
			best = found_nav[0]
		else:
			for entry in found_nav:
				if not best:
					best = sudo.entity_manager.get_distance(list(self.position), list(entry.position))
				elif sudo.entity_manager.get_distance(list(self.position), list(entry.position)) < best:
					best = sudo.entity_manager.get_distance(list(self.position), list(entry.position))
		return best

	def _wrap(self, obj):
		self._data = obj
		c = self._data.color
		self._data.color = [c[0],c[1],c[2],0.0]
		tweener.singleton.add(self._data, "color", "[*,*,*,1.0]", 1.0)
		if self.location:
			self._data.position = self.location
		self._data['entity_base'] = self



	def _unwrap(self):
		if self._data is not None:
			if not self._data.invalid:
				tweener.singleton.add(self._data, "color", "[*,*,*,0.0]", 1.0, callback=self._data.endObject)
			self._data = None

	def __getattr__(self, name):
		if name in EntityBase._kx_game_object_descriptors or name in EntityBase._kx_game_object_methods:
			return to_entity_base(getattr(self._data, name))
		else:
			raise AttributeError

	def __setattr__(self, name, val):
		if name in EntityBase._kx_game_object_descriptors or name in EntityBase._kx_game_object_methods:
			setattr(self._data, name, from_entity_base(val))
		else:
			self.__dict__[name] = val

	def __getitem__(self, item):
		return self._data[item]

	def __setitem__(self, item, value):
		self._data[item] = value

	def __delitem__(self, item):
		self._data.__delitem__(item)

	def __contains__(self, item):
		return item in self._data