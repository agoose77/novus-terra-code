import sys
sys.path.append('./src/')
sys.path.append('./src/bgui/') #the SVN external is all the bgui folders not just the module
sys.path.append('./data/') #we have a theme folder in data

import tweener
import cell
import bgui
import bge

class Start(bgui.Widget):
	"""Frame for storing other widgets"""
	theme_section = 'Frame'
	theme_options = {'Color1', 'Color2', 'Color3', 'Color4', 'BorderSize', 'BorderColor'}
	
	def __init__(self, parent, name, aspect=None, size=[1, 1], pos=[0, 0],
				sub_theme='', options=bgui.BGUI_DEFAULT):	
		bgui.Widget.__init__(self, parent, name, aspect, size, pos, sub_theme, options)
		
		theme = self.theme[self.theme_section] if self.theme else None
		
		self.bg = bgui.Frame(self, 'background', size=[1, 1], pos=[0,0],
			options=bgui.BGUI_DEFAULT)
		self.bg.colors = [(0,0,0,1) for i in range(4)]
		self.win = bgui.Frame(self, 'win', size=[741, 450], pos=[0,700],
			options=bgui.BGUI_THEMED|bgui.BGUI_CENTERED)
		self.win.img = bgui.Image(self.win, 'image', './data/textures/nt.png', size=[731, 235], pos=[5, 210],
			options = bgui.BGUI_THEMED|bgui.BGUI_CENTERX|bgui.BGUI_CACHE)
			
		self.button = bgui.FrameButton(self.win, 'button', text='ENTER GAME', size=[110, 30], pos=[100, 120],
			options = bgui.BGUI_THEMED)
		# Setup an on_click callback for the image
		self.button.on_click = self.start_game
		blurb = "NOVUS TERRA : Alpha v0.2"
		self.lbl = bgui.Label(self.win, 'label',text=blurb, pos=[100, 180], options = bgui.BGUI_THEMED )
		#tweener.singleton.add(self, 'color', '[*,*,*,1]', length=2.0)
		
		self.input = bgui.TextInput(self.win, 'input', "terrain.cell", size=[160, 30], pos=[220, 120], pt_size=12,
			input_options = bgui.BGUI_INPUT_SELECT_ALL, options = bgui.BGUI_THEMED)
		#self.input.activate()
		self.input.on_enter_key = self.on_input_enter
	
	def start_game(self, data):
		try:
			fo = open('./data/cells/'+self.input.text)
			fo.close()
			self.parent.show_loading('./data/cells/'+self.input.text)
		except:
			self.lbl.color = [1.0,0,0,1]
			self.lbl.text = "ERROR: cell "+self.input.text+" not found."
	def on_input_enter(self, widget):
		widget.deactivate()
		widget.frozen = 1