import xml.etree.ElementTree as ElementTree

import bge

import bgui
import dialogue
import game


class DialogueManager:
	def __init__(self):
		self.current_dialogue = None
		self.current_node = None
		self.previous_node = None

		self.parent_map = None
		self.labels = {}  # A map of labels -> nodes

		# init the gui
		self.gui = bgui.System(theme='./data/themes/dialogue')
		self.gui.message_box = dialogue.MessageBox(self.gui)
		self.gui.message_box.visible = False

		self.keymap = {getattr(bge.events, val): getattr(bgui, val) for val in dir(bge.events) if val.endswith('KEY') or val.startswith('PAD')}

	def display_dialogue(self, filename):
		""" Display a dialogue tree

		filename - the path to the dialogue file
		"""
		game.Game.singleton.world.suspend()
		self.current_dialogue = self.parse_dialogue(filename)
		self.current_node = self.current_dialogue.getroot()
		self.parent_map = dict((c, p) for p in self.current_dialogue.getiterator() for c in p)
		self.parent_map[self.current_dialogue.getroot()] = None
		self.previous_node = None

		# find all the labels
		for element in self.current_dialogue.iter():
			if element.tag == 'label':
				self.labels[element.text] = element

	def parse_dialogue(self, filename):
		""" Given the filepath to a dialogue file, return the xml element tree """
		return ElementTree.parse(filename)

	def end_dialogue(self):
		""" Finish displaying the current dialogue file and reset the values """
		self.current_dialogue = None
		self.current_node = None
		self.previous_node = None
		self.parent_map = None
		self.labels = {}

		self.gui.message_box.visible = False
		self.gui.message_box.name = ''
		game.Game.singleton.world.resume()

	def handle_name(self):
		""" Called when a <name> node is active """
		# Set the name on the message box
		self.gui.message_box.set_name(self.current_node.text)
		# The execution of this node has finished, return the next node
		return self.get_next_node(self.current_node, self.previous_node)

	def handle_text(self):
		""" Called when a <text> node is active """
		if not self.gui.message_box.visible:
			# The node needs initialising

			# Set the text on the message box
			self.gui.message_box.display_dialogue(self.current_node.text)

			# If the next node is an option container, push updateing onto that
			next_node = self.get_next_node(self.current_node, self.previous_node)
			if next_node is not None and next_node.tag == 'option_container':
				self.gui.message_box.visible = False
				return next_node

		if self.gui.message_box.done:
			# The user has finished reading
			self.gui.message_box.banish()
			return self.get_next_node(self.current_node, self.previous_node)

		# The user is still reading, return False to indicate this
		return False

	def handle_option_container(self):
		""" Called when an <option_container> node is active """
		if not self.gui.message_box.visible:  # this is set to False in handle_text
			# The option box needs initialising

			# Create a list of options
			options = []
			for option in self.current_node:
				options.append(option.attrib['choice_text'])

			# Pass the list to the message box so it can display them
			self.gui.message_box.display_options(options)

		if self.gui.message_box.selected_option is not None:
			# The user has selected an option
			option = self.gui.message_box.selected_option
			self.gui.message_box.banish()
			return self.current_node[option][0]
		elif self.gui.message_box.done:
			# The user has cancelled the option, finish the dialogue
			return None

		# The user is still selecting an option, return False to indicate this
		return False

	def update_current_node(self):
		""" Update the dialogue based on the tag of the current node

		returns - next node to run, False if the current node is still
				executing or None if the dialogue has ended
		"""
		if self.current_node.tag == 'conversation':
			return self.current_node[0]
		elif self.current_node.tag == 'name':
			return self.handle_name()
		elif self.current_node.tag == 'text':
			return self.handle_text()
		elif self.current_node.tag == 'label':
			return self.get_next_node(self.current_node, self.previous_node)
		elif self.current_node.tag == 'goto':
			return self.labels[self.current_node.text]
		elif self.current_node.tag == 'option_container':
			return self.handle_option_container()
		elif self.current_node.tag == 'option':
			# return the node after the option container
			container = self.parent_map[self.current_node]
			return self.get_next_node(self.parent_map[container], container)

	def get_next_node(self, current_node, prev_node):
		""" Crawl the tree looking for the next node to run """
		if len(current_node) > 0:
			# the node has children, find the next child to run
			next = False
			for child in current_node:
				if next:
					# There is still a child to run on this node
					return child

				elif child == prev_node:
					next = True

		# all children of current node have been run (or there were no children)
		if current_node == self.current_dialogue.getroot():
			#  there is no next node, all children of the root have been run
			return None
		else:
			# recurse upwards
			return self.get_next_node(self.parent_map[current_node], current_node)

	def handle_mouse(self):
		""" Push mouse behaviour to bgui """
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

		self.gui.click_state = mouse_state
		self.gui.update_mouse(pos, mouse_state)

	def handle_keyboard(self):
		""" Push keyboard behaviour to bgui """
		keyboard = bge.logic.keyboard

		key_events = keyboard.events
		is_shifted = key_events[bge.events.LEFTSHIFTKEY] == bge.logic.KX_INPUT_ACTIVE or \
					key_events[bge.events.RIGHTSHIFTKEY] == bge.logic.KX_INPUT_ACTIVE

		for key, state in keyboard.events.items():
			if state == bge.logic.KX_INPUT_JUST_ACTIVATED:
				self.gui.update_keyboard(self.keymap[key], is_shifted)

	def update_gui(self):
		bge.render.showMouse(1)

		self.handle_mouse()
		self.handle_keyboard()

		# Now setup the scene callback so we can draw
		if self.gui.render not in bge.logic.getCurrentScene().post_draw:
			bge.logic.getCurrentScene().post_draw.append(self.gui.render)

	def main(self):
		if self.current_dialogue:
			# There is dialogue to display

			# Keep updating the dialogue until a node returns false
			next_node = self.update_current_node()
			while next_node is not False:
				if next_node is None:
					self.end_dialogue()
					return

				self.previous_node = self.current_node
				self.current_node = next_node
				next_node = self.update_current_node()

			self.update_gui()
