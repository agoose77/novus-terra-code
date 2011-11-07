import inspect

entity_map = {}

try:
	import bge
	
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

class Container:
	pass

class EntityBase:
	""" Base object for classes representing game objects.

	Maps KX_GameObject functions to the inheriting class."""
	
	_kx_game_object_descriptors = []
	_kx_game_object_methods = []
	
	for name, value in inspect.getmembers(bge.types.KX_GameObject):
		# is property
		if inspect.isdatadescriptor(value):
			_kx_game_object_descriptors.append(name)
			
		# is method
		elif inspect.isroutine(value) and not name.startswith('__'):
		   _kx_game_object_methods.append((name, value))
	
	_containers = {}
		
	def __init__(self, packet=0):
		EntityBase._containers[self] = Container() # HACK - since setattr and getattr are overriden variables have to be stored on a dummy object
		#packet is the Entity instance from the cell
		self.packet = packet
		self._data = None
		
		self.iteract_icon = None
		self.iteract_label = None

	def main(self):
		pass
		
	def on_interact(self):
		pass
			
	def _wrap(self, obj):
		self._data = obj
		self._data['entity_base'] = self
		
		if self.packet:
			for name, value in self.packet.properties:
				self[name] = value
		
		for name, value in EntityBase._kx_game_object_methods:
			self.__dict__[name] = method_wrapper(getattr(self._data, name))
		
	def _unwrap(self):
		if self._data is not None:
			self._data = None
			
			for name, value in EntityBase._kx_game_object_methods:
				self.__dict__.pop(name)

	def __getattr__(self, name):
		if name in EntityBase._kx_game_object_descriptors:
			return to_entity_base(getattr(self._data, name))
		else:
			return getattr(EntityBase._containers[self], name)
		
	def __setattr__(self, name, val):
		if name in EntityBase._kx_game_object_descriptors:
			setattr(self._data, name, from_entity_base(val))
		else:
			setattr(EntityBase._containers[self], name, val)

	def __getitem__(self, item):
		return self._data[item]

	def __setitem__(self, item, value):
		self._data[item] = value

	def __delitem__(self, item):
		self._data.__delitem__(item)

	def __contains__(self, item):
		return item in self._data