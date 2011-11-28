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
		
	def save_prefs(self):
		prfs = [session.game.graphics_options, session.game.game_options, session.game.sound_options, session.game.default_cell ]
		fo = open('./data/'+'settings.prf', 'wb')
		pickle.dump(prfs, fo)
		fo.close()
		
	def load_prefs(self):
		try:
			fo = open('./data/'+'settings.prf', 'rb')
			prfs = pickle.load(fo)
			fo.close()
			session.game.graphics_options = prfs[0]
			session.game.game_options = prfs[1]
			session.game.sound_options = prfs[2]
			session.game.default_cell = prfs[3]
		except:
			print('no prf file found')