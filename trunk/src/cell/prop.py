from cell import CellManager
import math

class Prop:
	""" A static object to be added to a cell """
	def __init__(self, name="None", co=[0.0,0.0,0.0], scale=[1.0,1.0,1.0], dimensions=[1.0,1.0,1.0], rotation=[1.0,0.0,0.0], index=0, properties=[]):
		self.id = 0
		self.name = name
		self.co = co
		self.scale = scale
		self.dimensions = dimensions
		self.rotation = rotation
		self.game_object = 0 #the BGE object pointer
		self.index = index # index for CellManager.props_in_game
		self.properties = properties

	def kill(self):
		CellManager.singleton.props_in_game[self.index].remove(self)
		self.game_object.endObject()
		self.game_object = False