import bge
import sys

import tweener
import cell
import bgui
import bge
from paths import *

class Pause(bgui.Widget):
	"""Frame for storing other widgets"""
	theme_section = 'Frame'
	theme_options = {'Color1', 'Color2', 'Color3', 'Color4', 'BorderSize', 'BorderColor'}
	
	def __init__(self, parent, name, aspect=None, size=[1, 1], pos=[0, 0],
				sub_theme='', options=bgui.BGUI_THEMED):	
		bgui.Widget.__init__(self, parent, name, aspect, size, pos, sub_theme, options)
		
		theme = self.theme[self.theme_section] if self.theme else None
		
		self.bg = bgui.Frame(self, 'background', size=[1, 1], pos=[0,0],
			options=bgui.BGUI_DEFAULT)
		self.bg.colors = [(0,0,0,.5) for i in range(4)]
		self.nbox = Nbox(self, 'nbox', size=self.size)
		blurb = "testing menu paused PAUSED MENU"
		self.lbl = bgui.Label(self, 'label',text=blurb,sub_theme='Large', font='./data/fonts/Greyscale_Basic_Bold.ttf', pos=[.5, .5], options = bgui.BGUI_DEFAULT )
		
		
class Nbox(bgui.Widget):
	"""Novus UI background box"""

	
	def __init__(self, parent, name, aspect=None, size=[1, 1], pos=[0, 0],
				sub_theme='', options=bgui.BGUI_THEMED):	
		bgui.Widget.__init__(self, parent, name, aspect, size, pos, sub_theme, options)
		
		print( "NBOX: width = ", self.size)
		self.part = bgui.Image(self, 'part', safepath('./data/textures/ui_segment.png'), size=[self.size[0], 45], pos=[0, 0],
			options = bgui.BGUI_CACHE)

		
		
		
