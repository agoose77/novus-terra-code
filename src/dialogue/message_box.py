import bge

import bgui
import ui


class MessageBox(bgui.Widget):
	""" Message box for displaying dialogue in, displays batches of text or
	several options to choose """
	PADDING = 30  # pixels to pad text by
	LINE_PADDING = 5  # pixels to put in between each line of text

	class Divider(bgui.Frame):
		def __init__(self, parent, name, pos=[0, 0]):
			super().__init__(parent, name, size=[parent.size[0] - MessageBox.PADDING * 2 - 14, 3], pos=pos, options=bgui.BGUI_NONE)

			self.colors = [[0.5, 0.5, 0.5, 1]] * 4

	def __init__(self, parent):
		ww = bge.render.getWindowWidth()
		wh = bge.render.getWindowHeight()

		w = ww * 0.7  # width of the message window is 70% of horinztonal screen space
		h = wh * 0.4  # 40% of vertical space

		PADDING = MessageBox.PADDING
		super().__init__(parent, name='message_box', size=[w, h], pos=[0, 15],
			options=bgui.BGUI_THEMED | bgui.BGUI_CENTERX)

		# Make the background image
		# Corners
		self.bg_top_left = bgui.Image(self, 'bg_top_left', img='./data/textures/ui/dialogue_back.png',
			size=[30, 30], pos=[0, h - 30], texco=((0, .8828), (.1172, .8828), (.1172, 1), (0, 1)),
			options=bgui.BGUI_THEMED)
		self.bg_top_right = bgui.Image(self, 'bg_top_right', img='./data/textures/ui/dialogue_back.png',
			size=[30, 30], pos=[w - 30, h - 30], texco=((.8828, .8828), (1, .8828), (1, 1), (.8828, 1)),
			options=bgui.BGUI_THEMED)
		self.bg_bot_left = bgui.Image(self, 'bg_bot_left', img='./data/textures/ui/dialogue_back.png',
			size=[30, 30], pos=[0, 0], texco=((0, 0), (0, .1172), (.1172, .1172), (0, .1172)),
			options=bgui.BGUI_THEMED)
		self.bg_bot_right = bgui.Image(self, 'bg_bot_right', img='./data/textures/ui/dialogue_back.png',
			size=[30, 30], pos=[w - 30, 0], texco=((.8828, 0), (1, 0), (1, .1172), (.8828, .1172)),
			options=bgui.BGUI_THEMED)

		# Sides
		self.bg_left = bgui.Image(self, 'bg_left', img='./data/textures/ui/dialogue_back.png',
			size=[30, h - 60], pos=[0, 30], texco=((0, .1172), (.1172, .1172), (.1172, .8828), (0, .8828)),
			options=bgui.BGUI_THEMED)
		self.bg_right = bgui.Image(self, 'bg_right', img='./data/textures/ui/dialogue_back.png',
			size=[30, h - 60], pos=[w - 30, 30], texco=((.8828, .1172), (1, .1172), (1, .8828), (.8828, .8828)),
			options=bgui.BGUI_THEMED)
		self.bg_top = bgui.Image(self, 'bg_top', img='./data/textures/ui/dialogue_back.png',
			size=[w - 60, 30], pos=[30, h - 30], texco=((.1172, .8828), (.8828, .8828), (.8828, 1), (.1172, 1)),
			options=bgui.BGUI_THEMED)
		self.bg_bot = bgui.Image(self, 'bg_bot', img='./data/textures/ui/dialogue_back.png',
			size=[w - 60, 30], pos=[30, 0], texco=((.1172, 0), (.8828, 0), (.8828, .1172), (.1172, .1172)),
			options=bgui.BGUI_THEMED)

		# Centre piece
		self.bg_centre = bgui.Image(self, 'bg_centre', img='./data/textures/ui/dialogue_back.png',
			size=[w - 60, h - 60], pos=[30, 30], texco=((.1172, .1172), (.8828, .1172), (.8828, .8828), (.1172, .8828)),
			options=bgui.BGUI_THEMED)

		# The additional 30 that is floating around in position and size values bleow is for the
		# vertical space taken up by the more button
		self.scrollbar = ui.Scrollbar(self, 'messsage_box_scrollbar', pos=[w - PADDING - 10, PADDING + 30],\
			size=[10, h - PADDING * 2 - 30], direction=bgui.BGUI_VERTICAL_SCROLLBAR,
			sub_theme='message_box', options=bgui.BGUI_THEMED)
		self.scrollbar.on_scroll = self.scroll
		self.top = 0  # the line of text that is displayed at the top of the window

		# Calculate line height
		line = bgui.Label(self, "tmp", "Mj|")
		self._remove_widget(line)
		char_height = line.size[1]  # TODO replace this block with constant value
		self.char_height = char_height

		# Name of the NPC talking
		self.name = ''

		# list of bgui.Label's
		self.lines = []

		# highlights the selected option
		self.option_box = bgui.Frame(self, 'option_box', size=[w - MessageBox.PADDING * 2 - 8, self.char_height],
			pos=[MessageBox.PADDING - 4, 100], options=bgui.BGUI_THEMED)
		self.option_box.visible = False
		self.option_lines = {}  # a map for how many lines of text each option contains
		self.option_start = {}  # a map for which line index each option starts at

		# button for displaying the next node
		self.more_button = bgui.Label(self, 'message_box_more_button', text='More',\
			font='./data/fonts/Sansation_Regular.ttf', pt_size=24, color=(0.8, 0.2, 0.25, 1.0),
			pos=[w - 30 - 60, 30], options=bgui.BGUI_THEMED)

		self.more_button.visible = True
		self.more_button.on_click = self.more

		# When true, the more button has been pressed
		self.done = False

		# the index of the option thats been selected, when None no options
		# has been selected
		self.selected_option = None

	def more(self, widge):
		""" Callback for when the more button is pressed """
		self.done = True

	def set_name(self, name):
		""" Sets the name of the person talking """
		self.name = name + ':'

	def banish(self):
		""" Reset all attributes and hide the message box """
		for line in self.lines:
			self._remove_widget(line)

		self.lines = []
		self.option_start = {}
		self.option_lines = {}

		self.done = False
		self.selected_option = None
		self.option_box.visible = False
		self.visible = False

	def display_dialogue(self, text):
		""" Format text to fit into dialogue box """
		self.visible = True
		self.done = False
		self.top = 0
		self.more_button.text = 'More'

		for line in self.lines:
			self._remove_widget(line)

		self.lines = []

		lines = text.split('\n')
		i = 0

		# If there is a name set, add the name
		if self.name != '':
			self.lines.append(bgui.Label(self, 'line_0', text=self.name, pos=[MessageBox.PADDING,
				self.size[1] - (i + 1) * self.char_height - MessageBox.PADDING], sub_theme='message_box_name',
				options=bgui.BGUI_THEMED))
			i += 1

		# Now add the dialogue
		for line in lines:
			words = line.split(' ')

			line = bgui.Label(self, 'line_' + str(i), '', pos=[MessageBox.PADDING,
				self.size[1] - (i + 1) * self.char_height - i * MessageBox.LINE_PADDING - MessageBox.PADDING],
				sub_theme='message_box', options=bgui.BGUI_THEMED)

			while words:
				# try to add a word
				line.text += ' ' + words[0]

				if line.size[0] + MessageBox.PADDING * 2 > self.size[0] - MessageBox.PADDING * 2 - 10:
					# the line is too big, add the remaining words to a new line
					line.text = line.text[0:-len(words[0])]  # remove the last word
					self.lines.append(line)
					i += 1
					line = bgui.Label(self, 'line_' + str(i), '', pos=[MessageBox.PADDING,
						self.size[1] - (i + 1) * self.char_height - i * MessageBox.LINE_PADDING - MessageBox.PADDING],
						sub_theme='message_box', options=bgui.BGUI_THEMED)
				else:
					# the word fits
					words.pop(0)

			self.lines.append(line)
			i += 1

		# resize scrollbar
		self.scrollbar.slider_size = (self.scrollbar.size[1] / ((i) * self.char_height + (i - 1) * MessageBox.LINE_PADDING)) * self.scrollbar.size[1]
		self.scrollbar.slider_position = self.scrollbar.size[1] - self.scrollbar.slider_size
		if self.scrollbar.slider_size == self.scrollbar.size[1]:
			self.scrollbar.visible = False
		else:
			self.scrollbar.visible = True

		self.handle_overflow()

	def display_options(self, options):
		""" Insert several options beneath the current text in the message box """
		self.visible = True
		self.done = False
		self.top = 0
		self.more_button.text = 'Cancel'

		self.option_start = {}
		self.option_lines = {}

		i = len(self.lines)

		# Add divider
		if len(self.lines) != 0:
			self.lines.append(MessageBox.Divider(self, 'line_' + str(i), pos=[MessageBox.PADDING,
				self.size[1] - (i + 0.5) * self.char_height - (i) * MessageBox.LINE_PADDING - MessageBox.PADDING]))
			i += 1

		# Add options
		for j, option in enumerate(options):
			# j = option number
			# i = line number
			words = option.split(' ')

			line = bgui.Label(self, 'line_' + str(i), '', pos=[MessageBox.PADDING,
				self.size[1] - (i + 1) * self.char_height - (i) * MessageBox.LINE_PADDING - MessageBox.PADDING],
				sub_theme='message_box', options=bgui.BGUI_THEMED)
			line.on_hover = self.hover_option
			line.on_click = self.click_option
			line.option = j

			self.option_start[j] = i
			self.option_lines[j] = 1

			while words:
				# try to add a word
				line.text += ' ' + words[0]

				if line.size[0] + MessageBox.PADDING * 2 > self.size[0]:
					# the line is too big, add the remaining words to a new line
					line.text = line.text[0:-len(words[0]) + 1]  # remove the last word
					line.size[1] += 4
					line.position[1] -= 4
					self.lines.append(line)
					i += 1
					self.option_lines[j] += 1
					line = bgui.Label(self, 'line_' + str(i), '', pos=[MessageBox.PADDING,
						self.size[1] - (i + 1) * self.char_height - (i) * MessageBox.LINE_PADDING - MessageBox.PADDING],
						sub_theme='message_box', options=bgui.BGUI_THEMED)
					line.on_hover = self.hover_option
					line.on_click = self.click_option
					line.option = j
				else:
					# the word fits
					words.pop(0)

			self.lines.append(line)
			i += 1
			if j != len(options) - 1:
				self.lines.append(bgui.Widget(self, 'line_' + str(i)))
				i += 1

		# Resize scrollbar
		self.scrollbar.slider_size = (self.scrollbar.size[1] / ((i) * self.char_height + (i - 1) * MessageBox.LINE_PADDING)) * self.scrollbar.size[1]
		self.scrollbar.slider_position = self.scrollbar.size[1] - self.scrollbar.slider_size
		if self.scrollbar.slider_size == self.scrollbar.size[1]:
			self.scrollbar.visible = False
		else:
			self.scrollbar.visible = True

		self.handle_overflow()

	def handle_overflow(self):
		""" Hides any text that lies outside the message box """
		for line in self.lines:
			if line.position[1] > self.position[1] + self.size[1] - MessageBox.PADDING \
				or line.position[1] < self.position[1] + MessageBox.PADDING + 30:
				line.visible = False
			else:
				line.visible = True

	def scroll(self, scrollbar):
		""" Callback for when the scrollbar is moved """
		# Determine how many pixels on the scrollbar are equivilant to one line in the message box
		incriment = (self.scrollbar.size[1]) / (len(self.lines) * (MessageBox.LINE_PADDING + self.char_height))

		# Move each line by a scaled amount of pixels
		for line in self.lines:
			line._base_pos[1] += scrollbar.change / incriment
			line._update_position()

		self.handle_overflow()

	def hover_option(self, line):
		""" Called when an option is being hovered over, line is the line the mouse is over """
		self.option_box.visible = True

		self.option_box.position = [MessageBox.PADDING - 4,
			self.lines[self.option_start[line.option]].position[1] - self.option_lines[line.option] *
				(self.char_height + MessageBox.LINE_PADDING) + MessageBox.LINE_PADDING - 4]

		size = 0
		for i in range(self.option_start[line.option], self.option_start[line.option] + self.option_lines[line.option]):
			if self.lines[i].size[0] > size:
				size = self.lines[i].size[0]
		self.option_box.size = [size + 8, self.option_lines[line.option] * self.char_height + 8]

	def click_option(self, line):
		""" Called when an option is clicked, line is the line that was clicked """
		self.selected_option = line.option

	def _draw(self):
		""" Extend the Widget draw method to just reset the visibility of the selection box """
		super()._draw()

		self.option_box.visible = False
