class Entity:
	""" This is an entity as far as what needs to be known from a cell file.  """
	def __init__(self, name="None", co=[0.0,0.0,0.0], scale=[1.0,1.0,1.0], dimensions=[1.0,1.0,1.0], rotation=[1.0,0.0,0.0], properties=[], class_ = 'EntityBase'):
		self.id = 0
		self.name = name
		self.co = co
		self.scale = scale
		self.dimensions = dimensions
		self.rotation = rotation
		self.game_object = 0 # the BGE object pointer
		self.properties = properties
		self.class_ = class_ # the name of the class that represents the entity, e.g 'EntityBase', 'Door'