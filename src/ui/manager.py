try:
	import bge
	import bgui
except:
	print("import bge failed, normal if you are running an addon")

#import widgets from the ui module here
from .loading import *
from .start import *
from .pause import *
from paths import *

FONTPATH = './data/fonts/'

class System(bgui.System):
	def __init__(self):
		# Initiate the system
		bgui.System.__init__(self, safepath('./data/themes/default'))
		
		# Use a frame to store all of our widgets
		self.frame = bgui.Frame(self, 'window', border=0)
		self.frame.colors = [(0, 0, 0, 0) for i in range(4)]
		self.focused_widget = self.frame
		self.current = None
		self.paused = 0
		
		# Create a keymap for keyboard input
		self.keymap = {getattr(bge.events, val): getattr(bgui, val) for val in dir(bge.events) if val.endswith('KEY') or val.startswith('PAD')}

	def clear(self):
		if self.current.name in self.children:
			self._remove_widget(self.current)
			
	def show_loading(self, filename):

		if self.current.name in self.children:
			self._remove_widget(self.current)
		self.current = Loading(self, 'loading')
		self.current.load(filename)
		
	def show_start(self):
		if self.current:
			if self.current.name in self.children:
				self._remove_widget(self.current)
		self.current = Start(self, 'start')

	def pause(self):
		if self.paused == 0:
			self.paused = 1
			if self.current:
				if self.current.name in self.children:
					self._remove_widget(self.current)
			print( "SYSTEM SIZE:", self.size)
			self.current = Pause(self, 'pause', size=self.size)
		else:
			self.paused = 0
			#get rid of the pause menu
			if self.current:
				self._remove_widget(self.current)
				self.current = 0
					
	def update(self):
		bge.render.showMouse(1)
		"""A high-level method to be run every frame"""
		
		
		# Handle the mouse
		mouse = bge.logic.mouse
		
		pos = list(mouse.position)
		pos[0] *= bge.render.getWindowWidth()
		pos[1] = bge.render.getWindowHeight() - (bge.render.getWindowHeight() * pos[1])
		
		mouse_state = bgui.BGUI_MOUSE_NONE
		mouse_events = mouse.events
				
		if mouse_events[bge.events.LEFTMOUSE] == bge.logic.KX_INPUT_JUST_ACTIVATED:
			mouse_state = bgui.BGUI_MOUSE_CLICK
		elif mouse_events[bge.events.LEFTMOUSE] == bge.logic.KX_INPUT_JUST_RELEASED:
			mouse_state = bgui.BGUI_MOUSE_RELEASE
		elif mouse_events[bge.events.LEFTMOUSE] == bge.logic.KX_INPUT_ACTIVE:
			mouse_state = bgui.BGUI_MOUSE_ACTIVE
		
		self.update_mouse(pos, mouse_state)
		
		# Handle the keyboard
		keyboard = bge.logic.keyboard
		
		key_events = keyboard.events
		is_shifted = key_events[bge.events.LEFTSHIFTKEY] == bge.logic.KX_INPUT_ACTIVE or \
					key_events[bge.events.RIGHTSHIFTKEY] == bge.logic.KX_INPUT_ACTIVE
					
		for key, state in keyboard.events.items():
			if state == bge.logic.KX_INPUT_JUST_ACTIVATED:
				self.update_keyboard(self.keymap[key], is_shifted)
		
		# Now setup the scene callback so we can draw
		bge.logic.getCurrentScene().post_draw = [self.render]