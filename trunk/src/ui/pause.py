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
import game
import ui

class OptionsScreen(bgui.Widget):
	"""Frame for storing other widgets"""
	def __init__(self, parent, name, aspect=None, size=[1, 1], pos=[0, 0],
				sub_theme='', options=bgui.BGUI_DEFAULT):
		bgui.Widget.__init__(self, parent, name, aspect, size, pos, sub_theme, options)
		area = self.parent.image_back
		self.frame = bgui.Frame(self, 'frame', pos=area.position, size = area.size, options=bgui.BGUI_CENTERX)
		self.frame.colors = [ [0,0,0,0]]*4
		
		#save the option settings
		self.button = Fut_Button(self.frame, 'button', text='APPLY', size=[160, 45], pos=[230, 0],
			options = bgui.BGUI_NONE)
		self.button.on_click = self.apply
		
		self.text = bgui.Label(self.frame, 'text', text='Graphics Options', pos=[230, 440] , 
											pt_size=18, color=[1,1,1,1], font='./data/fonts/olney_light.otf', options=bgui.BGUI_NONE)
		
		self.graphic_options = []		
		i = 0
		for entry in session.game.graphics_options:
			if type(session.game.graphics_options[entry]) == bool:
				i += 1
				self.graphic_options.append(Fut_Radio(self.frame, str(entry), aspect=None, text=str(entry), 
													pos=[230, 430-i*20], size=[130,15], sub_theme='', options=bgui.BGUI_NONE) )
				if session.game.graphics_options[entry]:
					self.graphic_options[-1].toggle()
		
	def apply(self, data):
		for entry in self.graphic_options:
			if entry.name in session.game.graphics_options:
				state = entry.state
				if state in [True, 1]:
					session.game.graphics_options[entry.name] = True
				else:
					session.game.graphics_options[entry.name] = False
		session.savefile.save_prefs()

class GameScreen(bgui.Widget):
	"""Frame for storing other widgets"""
	def __init__(self, parent, name, aspect=None, size=[1, 1], pos=[0, 0],
				sub_theme='', options=bgui.BGUI_DEFAULT):
		bgui.Widget.__init__(self, parent, name, aspect, size, pos, sub_theme, options)
		area = self.parent.image_back
		self.frame = bgui.Frame(self, 'frame', pos=area.position, size = area.size, options=bgui.BGUI_CENTERX)
		self.frame.colors = [ [0,0,0,0]]*4



		self.back1 = Fut_Box(self.frame, 'back1', pos=[250,0], size = [500, 450], options=bgui.BGUI_NONE)
		self.back1.border = 0
		blurb = ""
		self.lbl = bgui.Label(self.back1, 'label',text=blurb, pt_size=18, pos=[10, 100], options = bgui.BGUI_THEMED )
		self.button = Fut_Button(self.back1, 'button', text='NEW GAME', size=[182, 45], pos=[10, 400],
			options = bgui.BGUI_NONE)
		self.button.on_click = self.start_game
		self.input = Fut_Input(self.back1, 'input', text=session.game.default_cell, size=[160, 30], pos=[230, 410],
			options = bgui.BGUI_NONE)

			
		self.button2 = Fut_Button(self.back1, 'button2', text='LOAD GAME', size=[182, 45], pos=[10, 300],
			options = bgui.BGUI_NONE)
		# Setup an on_click callback for the image
		self.button2.on_click = self.load_game
		self.input2 = Fut_Input(self.back1, 'input2', text="default.sav", size=[160, 30], pos=[230, 320],
			options = bgui.BGUI_NONE)
			
		self.button3 = Fut_Button(self.back1, 'button3', text='SAVE GAME', size=[182, 45], pos=[10, 200],
			options = bgui.BGUI_NONE)
		# Setup an on_click callback for the image
		self.button3.on_click = self.save_game
		self.input3 = Fut_Input(self.back1, 'input3', text="default.sav", size=[160, 30], pos=[230, 220],
			options = bgui.BGUI_NONE)

	
	def start_game(self, data):
		try:
			fo = safeopen('./data/cells/'+self.input.text, 'rb')
			fo.close()
			session.game.default_cell = self.input.text
			session.savefile.save_prefs()
			cell.CellManager.singleton.load('./data/cells/'+self.input.text)
		except:
			self.lbl.color = [1.0,0,0,1]
			self.lbl.text = "ERROR: cell "+self.input.text+" not found."
	def load_game(self, data):
		pass
	def save_game(self, data):
		try:
			session.savefile.save(self.input3.text)
			self.lbl.color = [1.0,1,1,1]
			self.lbl.text = "Game saved as: "+self.input3.text
		except:
			self.lbl.color = [1.0,0,0,1]
			self.lbl.text = "Error saving: "+self.input3.text

class InvScreen(bgui.Widget):
	"""Frame for storing other widgets"""
	def __init__(self, parent, name, aspect=None, size=[1, 1], pos=[0, 0],
				sub_theme='', options=bgui.BGUI_DEFAULT):
		bgui.Widget.__init__(self, parent, name, aspect, size, pos, sub_theme, options)
		area = self.parent.image_back
		self.frame = bgui.Frame(self, 'frame', pos=area.position, size = area.size, options=bgui.BGUI_CENTERX)
		self.frame.colors = [ [1,0,0,1]]*4



		self.back1 = Fut_Box(self.frame, 'back1', pos=[250,0], size = [450, 450], options=bgui.BGUI_NONE)


		self.items = []


	def reconstruct_inv(self):
		for entry in self.items:
			self.frame._remove_widget(entry)
		self.items = []

		temp_items = []
		for entry in session.game.world.player.inventory.items:
			temp_items.append(entry)

		size = 110
		counter = 0
		for j in range(3):
			for i in range(4):
				if counter < len(temp_items):
					item = temp_items[counter]
					imageicon = './data/textures/inventory_icons/'+item.icon
					imagename = item.name
					new_item_widget = Ninv_icon(self.frame, str(i)+str(j), image=imageicon,text=imagename, pos = [((size+10)*i+335),
												( 370 - (size+10)*j)], size = [size, size], options=bgui.BGUI_NONE)
					self.items.append( new_item_widget )
					if session.game.world.player.inventory.items[item] > 1:
						new_item_widget.amount.text = 'x'+str( session.game.world.player.inventory.items[item] )
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
		self.image_back = bgui.Image(self.frame, 'image_back', './data/textures/ui/show.png' , pos=[0, 0], size=[900,600],
			options = bgui.BGUI_CACHE | bgui.BGUI_NONE | bgui.BGUI_CENTERED )
			
		self.image_back.color=[.4,.7,.9,.4]
			
		self.frame.menu_back = Fut_Box(self, 'menu_back', pos=self.image_back.position, size = [193, 450], options=bgui.BGUI_NONE)

		
		self.title = bgui.Label(self.image_back, 'title',text="NOVUS:TERRA", pt_size=48, font='./data/fonts/olney_light.otf', 
								color=[1,1,1,1], pos=[0, 550], options = bgui.BGUI_THEMED )

		self.button1 = Fut_Button(self.image_back, 'game', pos=[5, 400], size=[182, 45], text="GAME", options=bgui.BGUI_NONE)
		self.button2 = Fut_Button(self.image_back, 'options', pos=[5, 350], size=[182, 45], text="OPTIONS", options=bgui.BGUI_NONE)
		self.button3 = Fut_Button(self.image_back, 'inventory', pos=[5, 300], size=[182, 45], text="INVENTORY", options=bgui.BGUI_NONE)
		self.button4 = Fut_Button(self.image_back, 'button4', pos=[5, 250], size=[182, 45], text="PLAYER", options=bgui.BGUI_NONE)
		
		
		# Create the button

		self.main_menu = [self.button1, self.button2, self.button3, self.button4]
		for entry in self.main_menu:
			entry.button_logic = self.button_logic

		self.screens = { 'gamescreen':GameScreen(self, 'gamescreen'), 'options':OptionsScreen(self, 'options'),
						'invscreen':ui.InventoryWindow(self, 'invscreen', game.Game.singleton.world.player.inventory, size=[340, 330], pos=[0,50], options=bgui.BGUI_CENTERED) }
		for entry in self.screens:
			self.screens[entry].visible = 0
			
		self.button_logic(self.button1)


	
		
	def button_logic(self, button):
		if button in self.main_menu:
			for entry in self.main_menu:
				entry.active = 0
			button.active = 1
			if self.current:
					if self.current.name in self.children:
						self.current.visible = 0

			if button.name == 'inventory':
				self.current = self.screens['invscreen']
				#self.current.reconstruct_inv()
				self.current.redraw()
				self.current.visible = 1
			if button.name == 'game':
				self.current = self.screens['gamescreen']
				self.current.visible = 1
			if button.name == 'options':
				self.current = self.screens['options']
				self.current.visible = 1
