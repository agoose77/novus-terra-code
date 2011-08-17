import sys, bge
sys.path.append( bge.logic.expandPath("//src//bgui"))


sys.path.append('./src/')
sys.path.append('./src/bgui/') #the SVN external is all the bgui folders not just the module
sys.path.append('./data/') #we have a theme folder in data

import tweener
import cell

try:
	import bge
	import bgui
except:
	print("import bge failed, normal if you are running an addon")

class Loading(bgui.Widget):
	"""Frame for storing other widgets"""
	theme_section = 'Frame'
	theme_options = {'Color1', 'Color2', 'Color3', 'Color4', 'BorderSize', 'BorderColor'}
	
	def __init__(self, parent, name, aspect=None, size=[1, 1], pos=[0, 0],
				sub_theme='', options=bgui.BGUI_DEFAULT):	
		bgui.Widget.__init__(self, parent, name, aspect, size, pos, sub_theme, options)
		
		theme = self.theme[self.theme_section] if self.theme else None
		self.color_mod = [1,1,1,0]
		self.win_color = [0,0,0,1]
		self.text_color = [1,1,0,1]
		self.win = bgui.Frame(self, 'win', size=[1, 1],
			options=bgui.BGUI_DEFAULT|bgui.BGUI_CENTERED)
		
		
		self.lbl = bgui.Label(self, 'label', sub_theme="Large",font='./data/fonts/akzidenze.ttf',text="Loading..", pos=[0, 0.5], color=self.text_color, options = bgui.BGUI_DEFAULT | bgui.BGUI_CENTERX)
		
		self.color = self.color_mod
		
		
	def load(self, filename): #here we're completely hijacking the cell.singleton.load command to wrap it with fades	
		self.loadfile = filename
		tweener.singleton.add(self, 'color', '[*,*,*,1]', length=0.1, callback = self.load_internal)
	def load_internal(self):
		cell.singleton.load(self.loadfile)
		cell.singleton.load_state = 1
		tweener.singleton.add(self, 'color', '[*,*,*,0]', length=3.0, callback = self.parent.clear)
		
	@property
	def color(self):
		"""The widget's name"""
		return self.color_mod
		
	@color.setter
	def color(self, value):
		self.color_mod = value
		new = []
		for i in range(4):
			new.append(self.win_color[i] * value[i])
		self.win.colors = [ tuple(new) for i in range(4) ]
		new = []
		for i in range(4):
			new.append(self.text_color[i] * value[i])
		self.lbl.color = new