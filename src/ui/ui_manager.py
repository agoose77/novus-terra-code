try:
	import bge
	import bgui
except:
	print("import bge failed, normal if you are running an addon")

#import widgets from the ui module here
from paths import *
import ui


class UIManager(bgui.System):
	""" Manages a stack of Screen objects, drawing and updating them in the correct order """

	def __init__(self):
		# Initiate the system
		bgui.System.__init__(self, safepath('./data/themes/default'))

		self.focused_widget = self

		# A stack of screens, screens at the back are drawn first
		self.current = []

		# Create a keymap for keyboard input
		self.keymap = {getattr(bge.events, val): getattr(bgui, val) for val in dir(bge.events) if val.endswith('KEY') or val.startswith('PAD')}

		# Initialise all the screens
		self.screens = { 'pause': ui.Pause(self),
						 'start': ui.Start(self, 'start'),
						 'loading': ui.Loading(self),
						 'item_swap': ui.ItemSwap(self, 'item_swap'),
						 'hud': ui.HUD(self, 'hud')}

		# Initially disable the visibility of each screen
		for screen in self.screens:
			self.screens[screen].visible = False
	
	def show(self, screen, args=[]):
		""" Display a screen.

		screen : The name of the screen.
		args : (optional) A list of arguments to pass to the screen's show method."""
		if not self.screens[screen].visible:
			self.current.append(self.screens[screen])
			self.screens[screen].show(args=args)
			self._update_order()

	def hide(self, screen):
		if self.screens[screen].visible:
			self.current.remove(self.screens[screen])
			self.screens[screen].hide()
			self._update_order()

	def toggle(self, screen):
		""" Toggle the visibility of a screen (doesn't pass arguments) """
		if self.screens[screen].visible:
			self.current.remove(self.screens[screen])
			self.screens[screen].hide()
		else:
			self.current.append(self.screens[screen])
			self.screens[screen].show(args=[])

		self._update_order()

	def hide_current(self):
		""" Hide the top most screen """
		if len(self.current) != 0:
			screen = self.current.pop(-1)
			screen.hide()

	def clear(self):
		""" Hide all visible screens """
		while len(self.current) != 0:
			screen = self.current.pop(-1)
			screen.hide()

	def _update_order(self):
		""" Update the order of the screens in the children dictionary
		to ensure the screen on the top of the stack recieves input
		last, therefore retains the focused_widget prpoerty """
		for screen in self.current:
			self._remove_widget(screen)
			self._attach_widget(screen)

	def _draw(self):
		""" Override the draw function to draw the screens in proper order """
		# Draw the screens from the back to the front.
		for screen in self.current:
			screen._draw()
	
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
		is_shifted = (key_events[bge.events.LEFTSHIFTKEY] == bge.logic.KX_INPUT_ACTIVE or
					key_events[bge.events.RIGHTSHIFTKEY] == bge.logic.KX_INPUT_ACTIVE)
					
		for key, state in keyboard.events.items():
			if state == bge.logic.KX_INPUT_JUST_ACTIVATED:
				self.update_keyboard(self.keymap[key], is_shifted)
		
	def main(self):
		"""A high-level method to be run every frame"""
		bge.render.showMouse(1)
		
		self.handle_mouse()
		self.handle_keyboard()

		# Update screens from the front backwards until a blocking screen is reached.
		for screen in self.current[::-1]:
			screen.main()
			if screen.blocking:
				break

		# Now setup the scene callback so we can draw
		if self.render not in bge.logic.getCurrentScene().post_draw:
			bge.logic.getCurrentScene().post_draw.append(self.render)