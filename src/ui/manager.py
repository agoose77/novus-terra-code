

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
import ui

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

		self.screens = { 'pause': Pause(self, 'pause', size=self.size),
						 'start': Start(self, 'start'),
						 'loading': Loading(self, 'loading'),
						 'item_swap': ui.ItemSwap(self, 'item_swap')}
		for entry in self.screens:
			self.screens[entry].visible = 0
		
		
	def clear(self):
		if self.current:
			if self.current.name in self.children:
				self.current.visible = 0
			
	def show_loading(self):
		if self.current:
			if self.current.name in self.children:
				self.current.visible = 0
		self.current = self.screens['loading']
		self.current.visible = 1
		tweener.singleton.add(self.current, 'color', '[*,*,*,1]', length=0.1)
		
	def show_item_swap(self, inventory):
		[scene for scene in bge.logic.getSceneList() if scene.name == 'Construct'][0].suspend()
		if self.current:
			if self.current.name in self.children:
				self.current.visible = 0
		self.current = self.screens['item_swap']
		self.current.visible = 1
		self.current.set_inventory(inventory)
		
	def hide_item_swap(self, widget):
		[scene for scene in bge.logic.getSceneList() if scene.name == 'Construct'][0].resume()
		self.current.visible = 0
		self.current = 0
		
		bge.render.setMousePosition(bge.render.getWindowWidth()//2, bge.render.getWindowHeight()//2)
		
	def show_start(self):
		if self.current:
			if self.current.name in self.children:
				self.current.visible = 0
		self.current = self.screens['pause']
		self.current.visible = 1
		
	def pause(self):
		if bge.logic.globalDict['pause'] == 0:
			bge.logic.globalDict['pause'] = 1
			if self.current:
				if self.current.name in self.children:
					self.current.visible = 0
			self.current = self.screens['pause']
			self.current.visible = 1
		else:
			bge.logic.globalDict['pause'] = 0
			#get rid of the pause menu
			if self.current:
				self.current.visible = 0
				self.current = 0
	
	def handle_mouse(self):
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
		
		self.click_state = mouse_state
		self.update_mouse(pos, mouse_state)
		
	def handle_keyboard(self):
		keyboard = bge.logic.keyboard
		
		key_events = keyboard.events
		is_shifted = key_events[bge.events.LEFTSHIFTKEY] == bge.logic.KX_INPUT_ACTIVE or \
					key_events[bge.events.RIGHTSHIFTKEY] == bge.logic.KX_INPUT_ACTIVE
					
		for key, state in keyboard.events.items():
			if state == bge.logic.KX_INPUT_JUST_ACTIVATED:
				self.update_keyboard(self.keymap[key], is_shifted)
		
	def update(self):
		bge.render.showMouse(1)
		"""A high-level method to be run every frame"""
		
		self.handle_mouse()
		self.handle_keyboard()
		
		# Now setup the scene callback so we can draw
		bge.logic.getCurrentScene().post_draw = [self.render]