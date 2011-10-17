import pickle
import os
import time
from copy import deepcopy

import session
import tweener
import terrain
import cell
import ui
from item import Item
from weapon import Weapon

class Kernel:
	def __init__(self):
		self.entities={}
		self.player = 0

class Save:

	def __init__(self):
		self.entities = {}
		self.player = 0
		
	def load(self, filename):
		pass
	def save(self, filename='default.sav'):
		clone = Kernel()
		for name in self.entities:
			clone.entities[name] = []
			for i in self.entities[name]:
				clone.entities[name].append(i.packet)
		fo = open('./data/saves/'+filename, 'wb')
		pickle.dump(clone, fo)