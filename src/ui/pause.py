import bge
import sys

import tweener
import cell
import bgui
from .nwidgets import *
import bge
from paths import *
import session

class GameScreen(bgui.Widget):
	"""Frame for storing other widgets"""
	def __init__(self, parent, name, aspect=None, size=[1, 1], pos=[0, 0],
				sub_theme='', options=bgui.BGUI_DEFAULT):	
		bgui.Widget.__init__(self, parent, name, aspect, size, pos, sub_theme, options)
		self.test = Nbox(self, 'test', pos=[20,self.size[1]*.75-550], size = [800, 500], options=bgui.BGUI_CENTERX)

class InvScreen(bgui.Widget):
	"""Frame for storing other widgets"""
	def __init__(self, parent, name, aspect=None, size=[1, 1], pos=[0, 0],
				sub_theme='', options=bgui.BGUI_DEFAULT):	
		bgui.Widget.__init__(self, parent, name, aspect, size, pos, sub_theme, options)
		
		self.frame = bgui.Frame(self, 'frame', pos=[20,self.size[1]*.75-550], size = [800, 500], options=bgui.BGUI_CENTERX)
		self.frame.colors = [ [0,0,0,.4]]*4
		
		
		
		self.back1 = Nbox(self.frame, 'back1', pos=[300,0], size = [500, 500], options=bgui.BGUI_NONE)
		self.back2 = Nbox(self.frame, 'back2', pos=[0,0], size = [230, 500], options=bgui.BGUI_NONE)
		
		self.black_frame = bgui.Frame(self.frame, 'black_frame', pos=[325, 20], border=2, size = [480, 460], options=bgui.BGUI_NONE)
		self.black_frame.colors = [ [.3,.3,.3,.8]]*4
		self.black_frame.border_color = [.5,.5,.5,.5]
		
		temp_items = []
		for entry in session.game.player.inventory.items:
			print(entry)
			temp_items.append(entry)
		
		self.items = []
		size = 110
		counter = 0
		print (temp_items)
		for j in range(3):
			for i in range(4):
				if counter < len(temp_items):
					item = temp_items[counter]
					imageicon = './data/textures/inventory_icons/'+item.icon
					imagename = item.name
					new_item_widget = Ninv_icon(self.frame, str(i)+str(j), image=imageicon,text=imagename, pos = [((size+10)*i+335), 
												( 370 - (size+10)*j)], size = [size, size], options=bgui.BGUI_NONE)
					self.items.append( new_item_widget )
					if session.game.player.inventory.items[item] > 1:
						new_item_widget.amount.text = 'x'+str( session.game.player.inventory.items[item] )
				counter += 1

		
class Pause(bgui.Widget):
	"""Frame for storing other widgets"""

	
	def __init__(self, parent, name, aspect=None, size=[1, 1], pos=[0, 0],
				sub_theme='', options=bgui.BGUI_NONE):	
		bgui.Widget.__init__(self, parent, name, aspect, size, pos, sub_theme, options)
		
		#self.info = Ninfo( self, 'info', pos=[10,10], size=[40,40], options=bgui.BGUI_NONE)	
		#print(self.info.size, self.info.position)
		
		self.current = None #this is where the widget for the individual screens will go
		
		self.frame = bgui.Frame(self, 'frame', size=[1,1], options=bgui.BGUI_CENTERED|bgui.BGUI_DEFAULT)
		self.frame.colors = [ [0,0,0,.4]]*4

		self.menudown = Nbox(self.frame, 'nbox3', pos=[20,-500], size = [32, 50])
		self.frame.menu_back = Nbox(self, 'menu_back', pos=[20,self.frame.size[1]*.75], size = [800, 65], options=bgui.BGUI_CENTERX)
		
		
		self.button1 = Nbutton(self.frame.menu_back, 'game', pos=[20, 10], size=[130,50], text="GAME", options=bgui.BGUI_NONE)
		self.button2 = Nbutton(self.frame.menu_back, 'button2', pos=[170, 10], size=[190,50], text="OPTIONS", options=bgui.BGUI_NONE)
		self.button3 = Nbutton(self.frame.menu_back, 'inventory', pos=[380, 10], size=[250,50], text="INVENTORY", options=bgui.BGUI_NONE)
		self.button4 = Nbutton(self.frame.menu_back, 'button4', pos=[655, 10], size=[170,50], text="PLAYER", options=bgui.BGUI_NONE)
		# Create the button

		self.main_menu = [self.button1, self.button2, self.button3, self.button4]
		for entry in self.main_menu:
			entry.button_logic = self.button_logic
			
		self.screens = { 'gamescreen':GameScreen(self, 'gamescreen'), 
						'invscreen':InvScreen(self, 'invscreen') }
		for entry in self.screens:
			self.screens[entry].visible = 0
		
		
	def button_logic(self, button):
		if button in self.main_menu:
			for entry in self.main_menu:
				entry.active = 0
			button.active = 1
			self.menudown.position = [(button.position[0]-self.frame.position[0])+button.size[0]/2-30, self.frame.menu_back.position[1]-50]
			
			if self.current:
					if self.current.name in self.children:
						self.current.visible = 0
						print( '?- ', self.current)
			
			if button.name == 'inventory':
				self.current = self.screens['invscreen']
				self.current.visible = 1
			if button.name == 'game':
				self.current = self.screens['gamescreen']
				self.current.visible = 1
