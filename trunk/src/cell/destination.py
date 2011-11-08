class Destination:
	""" Represents a location and rotation that the player can teleport to """
	def __init__(self, id=0, co=[0.0, 0.0, 0.0], rotation=[1.0, 0.0, 0.0]):
		self.id = id # should be unique to the cell
		self.co = co
		self.rotation = rotation