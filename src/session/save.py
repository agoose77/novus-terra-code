import pickle
import os
import time

import tweener
import terrain
import cell
from item import Item
from weapon import Weapon


class Save:

	def __init__(self):
		self.entities = {}
		self.player = 0
		
	def load(self, filename):
		pass
	def save(self, filename):
		pass