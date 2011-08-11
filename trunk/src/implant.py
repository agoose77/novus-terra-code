class Implant:

	implants = {}

	def __init__(self, id, name, description='', effects={}):
		self.id = id
		self.type = type
		self.on_interact= 0

		self.name = name
		self.description = description

		if 'health' in effects:
			self.health = effects['health']
		if 'energy' in effects:
			self.energy= effect['energy']
		if 'speed' in effects:
			self.speed = effect['speed']
		if 'effect' in effects:
			self.effect = effect['effect']

		Implant.implants[id] = self

	def activate_item(self):
		func = self.effect
		if callable(func):
			func (self)