import sys

# So we can find the bgui module
sys.path.append('../..')

import bgui
import bge
import time



class Nbox(bgui.Widget):
	"""Novus UI background box"""

	
	def __init__(self, parent, name, aspect=None, size=[1, 1], pos=[0, 0],
				sub_theme='', options=bgui.BGUI_THEMED):	
		bgui.Widget.__init__(self, parent, name, aspect, size, pos, sub_theme, options)
		
		print( "NBOX: width = ", self.size)
		self.part = bgui.Image(self, 'part', './data/textures/ui/ui_middle.png', pos=[32, 0], size=[self.size[0]-32, self.size[1]],
			options = bgui.BGUI_CACHE )
		self.left = bgui.Image(self, 'left', './data/textures/ui/ui_left.png', pos=[0, 0], size=[32, self.size[1]],
			options = bgui.BGUI_CACHE )
		self.right = bgui.Image(self, 'right', './data/textures/ui/ui_right.png', pos=[size[0], 0],size=[32, self.size[1]],
			options = bgui.BGUI_CACHE )
		image_size = self.part.image_size
		ratio = [ self.size[0] / image_size[0], self.size[1] / image_size[1] ]
		self.part.color, self.left.color, self.right.color = [1,1,1,.4], [1,1,1,.4], [1,1,1,.4]
		self.part.texco=[(0,0), (ratio[0],0), (ratio[0],ratio[1]), (0,ratio[1])]
		self.left.texco=[(0,0), (1,0), (1,ratio[1]), (0,ratio[1])]
		self.right.texco=[(0,0), (1,0), (1,ratio[1]), (0,ratio[1])]
		

		
class Nbutton(bgui.Widget):
	"""Novus UI button"""

	
	def __init__(self, parent, name, aspect=None, text='Click me', shadow=[-2,2], size=[1, 1], pos=[0, 0],
				sub_theme='', image='./data/textures/ui/blur.png', options=bgui.BGUI_THEMED):	
		bgui.Widget.__init__(self, parent, name, aspect, size, pos, sub_theme, options)
		
		csize = self.size[1]*.3
		
		self.image = bgui.Image(self, 'blur', image, pos=[0, 0], size=[1,1],
			options = bgui.BGUI_CACHE | bgui.BGUI_DEFAULT | bgui.BGUI_CENTERED )
		self.image.visible = 0
		
		self.corner1 = bgui.Image(self, 'corner1', './data/textures/ui/nbutton_corner.png', pos=[0, 0], size=[csize,csize],
			options = bgui.BGUI_CACHE )
		self.corner1.visible = 0
		
		self.corner2 = bgui.Image(self, 'corner2', './data/textures/ui/nbutton_corner.png', pos=[self.size[0]-csize, 0], size=[csize,csize],
			options = bgui.BGUI_CACHE )
		self.corner2.visible = 0
		
		self.corner3 = bgui.Image(self, 'corner3', './data/textures/ui/nbutton_corner.png', pos=[0, self.size[1]-csize], size=[csize,csize],
			options = bgui.BGUI_CACHE )
		self.corner3.visible = 0
		
		self.corner4 = bgui.Image(self, 'corner4', './data/textures/ui/nbutton_corner.png', pos=[self.size[0]-csize, self.size[1]-csize], size=[csize,csize],
			options = bgui.BGUI_CACHE )
		self.corner4.visible = 0
		
		self.corner1.texco=[ (0,1), (0,0), (1,0), (1,1)]
		self.corner2.texco=[ (1,1), (0,1), (0,0), (1,0)]
		self.corner4.texco=[ (1,0), (1,1), (0,1), (0,0)]
		self.corners = [self.corner1, self.corner2, self.corner3, self.corner4]
		
		self.text1 = bgui.Label(self, 'text1', text=text, pt_size=39, color=[0,0,0,1], font='./data/fonts/FFF_Tusj.ttf', options=bgui.BGUI_CENTERED)
		print( self.text1.position)
		off = [ self.text1.position[0]+shadow[0]-self.position[0], self.text1.position[1]+shadow[1] -self.position[1] ]
		self.text2 = bgui.Label(self, 'text2', text=text, pos=off , 
											pt_size=39, color=[1,1,1,1], font='./data/fonts/FFF_Tusj.ttf', options=bgui.BGUI_NONE)
											
		self.active = 0									

	def _handle_mouse(self, pos, event):
		if event == bgui.BGUI_MOUSE_NONE:
			self.image.visible = 1
		elif event == bgui.BGUI_MOUSE_CLICK:
			self.button_logic(self)
		bgui.Widget._handle_mouse(self, pos, event)
		
	def _draw(self):
		if self._hover == False:
			self.image.visible = 0
		if self.active == 1:
			for entry in self.corners:
				entry.visible = 1
		else:
			for entry in self.corners:
				entry.visible = 0
		bgui.Widget._draw(self)
		
	def button_logic(self, button):
		pass

class Ninv_icon( Nbutton ):
	def __init__(self, parent, name, aspect=None, text='item name', image='./data/textures/ui/blur.png', shadow=[-2,2], size=[1, 1], pos=[0, 0],
				sub_theme='', options=bgui.BGUI_THEMED):	
		Nbutton.__init__(self, parent, name, aspect, image=image, size=size, pos=pos, sub_theme=sub_theme, options=options)
		self.image.visible = 1
		self._remove_widget(self.text1)
		self._remove_widget(self.text2)
		self.text1 = bgui.Label(self, 'text1', text=text, pt_size=14, color=[1,1,1,1], font='./data/fonts/akzidenze.ttf', options=bgui.BGUI_CENTERX)
		self.text1.position = [0,2]
		
		self.amount = bgui.Label(self, 'amount', text="", pt_size=32, color=[1,.9,0,1], 
				pos = [self.size[0]*.7, self.size[0]*.8 ], font='./data/fonts/FFF_Tusj.ttf', options=bgui.BGUI_NONE)

	def button_logic(self, button):
		self.active = 1
		
	def _draw(self):
		if self._hover == False:
			for entry in self.corners:
				entry.visible = 1
		if self.active == 1:
			for entry in self.corners:
				entry.visible = 1
		else:
			for entry in self.corners:
				entry.visible = 0
		bgui.Widget._draw(self)
		
class Ninfo(bgui.Widget):
	"""Novus UI background box"""

	
	def __init__(self, parent, name, aspect=None, size=[1, 1], pos=[0, 0],
				sub_theme='', options=bgui.BGUI_NONE):	
		bgui.Widget.__init__(self, parent, name, aspect, size, pos, sub_theme, options)
		
		self.frame = bgui.Frame(self, 'frame', size=size, pos=pos, options=options)
		self.text = bgui.TextBlock(self, 'text', text="hello world/nline2", font='./data/fonts/FFF_Tusj.ttf', pt_size=12, color=None, aspect=None,
					size=[1, 1], pos=[0, 0], sub_theme='', overflow=bgui.BGUI_OVERFLOW_HIDDEN, options=bgui.BGUI_NONE)