import bge
from bgl import *
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
		area = self.parent.image_back
		self.frame = bgui.Frame(self, 'frame', pos=area.position, size = area.size, options=bgui.BGUI_CENTERX)
		self.frame.colors = [ [0,0,0,0]]*4



		self.back1 = Fut_Box(self.frame, 'back1', pos=[250,0], size = [500, 450], options=bgui.BGUI_NONE)
		
		self.button = bgui.FrameButton(self.back1, 'button', text='ENTER GAME', size=[110, 30], pos=[100, 120],
			options = bgui.BGUI_THEMED)
		# Setup an on_click callback for the image
		self.button.on_click = self.start_game
		
	
		
		
		blurb = "NOVUS TERRA : Alpha v0.2 : Thanks for waiting!"
		self.lbl = bgui.Label(self.back1, 'label',text=blurb, pos=[100, 180], options = bgui.BGUI_THEMED )
		#tweener.singleton.add(self, 'color', '[*,*,*,1]', length=2.0)
		
		self.input = bgui.TextInput(self.back1, 'input', "dynamic.cell", size=[160, 30], pos=[220, 120], pt_size=32,
			input_options = bgui.BGUI_INPUT_SELECT_ALL, options = bgui.BGUI_THEMED)
		#self.input.activate()
		self.input.on_enter_key = self.on_input_enter
	
	def start_game(self, data):
		try:
			fo = safeopen('./data/cells/'+self.input.text, 'rb')
			fo.close()
			self.parent.show_loading('./data/cells/'+self.input.text)
		except:
			self.lbl.color = [1.0,0,0,1]
			self.lbl.text = "ERROR: cell "+self.input.text+" not found."

class InvScreen(bgui.Widget):
	"""Frame for storing other widgets"""
	def __init__(self, parent, name, aspect=None, size=[1, 1], pos=[0, 0],
				sub_theme='', options=bgui.BGUI_DEFAULT):
		bgui.Widget.__init__(self, parent, name, aspect, size, pos, sub_theme, options)
		area = self.parent.image_back
		self.frame = bgui.Frame(self, 'frame', pos=area.position, size = area.size, options=bgui.BGUI_CENTERX)
		self.frame.colors = [ [0,0,0,0]]*4



		self.back1 = Fut_Box(self.frame, 'back1', pos=[250,0], size = [450, 450], options=bgui.BGUI_NONE)


		self.items = []


	def reconstruct_inv(self):
		for entry in self.items:
			self.frame._remove_widget(entry)
		self.items = []

		temp_items = []
		for entry in session.game.player.inventory.items:
			print(entry)
			temp_items.append(entry)

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
	def button_logic(self, button):
		if button in self.items:
			for entry in self.items:
				entry.active = 0
			button.active = 1


class Pause(bgui.Widget):
	"""Frame for storing other widgets"""


	def __init__(self, parent, name, aspect=None, size=[1, 1], pos=[0, 0],
				sub_theme='', options=bgui.BGUI_NONE):
		bgui.Widget.__init__(self, parent, name, aspect, size, pos, sub_theme, options)

		#self.info = Ninfo( self, 'info', pos=[10,10], size=[40,40], options=bgui.BGUI_NONE)
		#print(self.info.size, self.info.position)

		self.current = None #this is where the widget for the individual screens will go

		self.frame = bgui.Frame(self, 'frame', size=[1,1], options=bgui.BGUI_CENTERED|bgui.BGUI_DEFAULT)
		self.frame.colors = [ [0,0,0,1]]*4
		self.image_back = bgui.Image(self.frame, 'image_back', './data/textures/ui/show.png' , pos=[0, 0], size=[900,600], color=[.4,.7,.9,.4],
			options = bgui.BGUI_CACHE | bgui.BGUI_NONE | bgui.BGUI_CENTERED, interpolate="NEAREST" )
		self.menudown = Nbox(self.frame, 'nbox3', pos=[20,-500], size = [32, 50])
		self.frame.menu_back = Fut_Box(self, 'menu_back', pos=self.image_back.position, size = [190, 450], options=bgui.BGUI_NONE)


		self.button1 = Fut_Button(self.image_back, 'game', pos=[5, 400], size=[182, 45], text="GAME", options=bgui.BGUI_NONE)
		self.button2 = Fut_Button(self.image_back, 'button2', pos=[5, 350], size=[182, 45], text="OPTIONS", options=bgui.BGUI_NONE)
		self.button3 = Fut_Button(self.image_back, 'inventory', pos=[5, 300], size=[182, 45], text="INVENTORY", options=bgui.BGUI_NONE)
		self.button4 = Fut_Button(self.image_back, 'button4', pos=[5, 250], size=[182, 45], text="PLAYER", options=bgui.BGUI_NONE)
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
				self.current.reconstruct_inv()
				self.current.visible = 1
			if button.name == 'game':
				self.current = self.screens['gamescreen']
				self.current.visible = 1

