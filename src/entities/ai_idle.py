import entities
import sudo
import bge, random
import tweener
import time

""" editor properties:
 - dialogue - a string of the dialogue file, minus the path and file extension
 """
class AIIdle():
	""" A simple entity for talking to """
	def __init__(self, packet=None):
		self.interact_label = 'Talk'
		print ('AI idle _init_')

	def update(self):
		pass