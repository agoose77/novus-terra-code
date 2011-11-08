from cell import CellManager

class Lamp:
	def __init__(self, name="None", co=[0.0,0.0,0.0], rotation=[1.0,0.0,0.0], type="POINT", color=[0.0,0.0,0.0], distance=0.5, energy=50, spot_size=100, spot_blend=0.25, spot_bias=2.0):
		print ('added Lamp 00000000000000000000000000000')
		self.id = 0
		self.name = name
		self.co = co
		self.rotation = rotation
		self.type = type
		self.color = color
		self.distance = distance
		self.energy = energy
		self.spot_size = spot_size
		self.spot_blend = spot_blend
		self.spot_bias= spot_bias

	def kill(self):
		CellManager.singleton.lamps_in_game.remove(self)
		if self.type == "SPOT":
			CellManager.singleton.spots.append(self.game_object.name)
		if self.type == "POINT":
			CellManager.singleton.points.append(self.game_object.name)
		self.game_object.endObject()
		self.game_object = False