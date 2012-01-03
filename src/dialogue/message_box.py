import bge

import bgui
import ui

class MessageBox(bgui.Widget):
	""" Message box for displaying dialogue in, displays batches of text or
	several options to choose """
	PADDING = 4 # pixels to pad text by

	def __init__(self, parent):
		super().__init__(parent, name='message_box', size=[600, 205], pos=[0, 15],\
			options=bgui.BGUI_THEMED|bgui.BGUI_CENTERX)
		
		ww = bge.render.getWindowWidth()

		# background frame
		self.frame = bgui.Frame(self, 'message_box_frame', pos=[0, 35], size=[600, 170],\
			sub_theme='message_box', options=bgui.BGUI_THEMED|bgui.BGUI_CENTERX)

		self.scrollbar = ui.Scrollbar(self, 'messsage_box_scrollbar', pos=[self.size[0]-10, 35],\
			size=[10, self.size[1]-35], direction = bgui.BGUI_VERTICAL_SCROLLBAR,
			sub_theme='message_box', options=bgui.BGUI_THEMED)
		
		line = bgui.Label(self, "tmp", "Mj|", sub_theme='message_box')
		self._remove_widget(line)
		char_height = line.size[1] # TODO replace this block with constant value
		char_height /= self.size[1]
		self.char_height = char_height

		# list of bgui.Label's
		self.lines = []
		
		# highlights the selected option
		#self.option_box = bgui.Frame(...)
		#self.option_box.visible = False
		
		# button for displaying the next node
		self.more_button = bgui.FrameButton(self, 'message_box_more_button', text='More',\
			font='./data/fonts/Greyscale_Basic_Regular.ttf', pt_size=18, size=[60, 25],
			pos=[0,0], sub_theme='more_button', options=bgui.BGUI_THEMED)

		self.more_button = ui.Fut_Button(self, 'message_box_more_button', text='More',\
			size=[100, 35], pos=[self.size[0]-100, -3], options=bgui.BGUI_NONE)
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

	def banish(self):
		""" Reset all attributes and hide the message box """
		for line in self.lines:
			self._remove_widget(line)

		self.lines = []

		self.done = False
		self.selected_option = None
		self.option_box.visible = False
		self.visible = False

	def display_dialogue(self, text):
		""" Format text to fit into dialogue box """

		self.visible = True

		for line in self.lines:
			self._remove_widget(line)

		self.lines = []

		lines = text.split('\n')
		i = 0
		for line in lines:
			words = line.split()
			print(words) # DBG

			line = bgui.Label(self, 'line_'+str(i), '', pos=[0, 1-(i+1)*self.char_height],
				sub_theme='message_box', options=bgui.BGUI_DEFAULT)
			
			while words:
				# try to add a word
				line.text += ' ' + words[0]

				if line.size[0] + MessageBox.PADDING * 2 > self.size[0]:
					# the line is too big, add the remaining words to a new line
					line.text = line.text[0:-len(words[0])+1] # remove the last word
					self.lines.append(line)
					i += 1
					line = bgui.Label(self, 'line_'+str(i), '', pos=[0, 1-(i+1)*self.char_height],
						sub_theme='message_box')
				else:
					# the word fits
					words.pop(0)

			self.lines.append(line)
			i += 1

		self.handle_overflow()

	def display_options(self, options):
		pass

	def handle_overflow(self):
		""" Hides any text that lies outside the message box """
		for line in self.lines:
			if line.position[0] > self.position[0] \
				or line.position[1] < self.position[1]:
				line.visible = False
			else:
				line.visible = True