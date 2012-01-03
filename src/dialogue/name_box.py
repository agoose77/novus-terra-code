import bge

import bgui

class NameBox(bgui.Widget):

	PADDING = 5 # pixels to pad text in box by

	def __init__(self, parent):
		ww = bge.render.getWindowWidth()
		super().__init__(parent, 'name_box', size=[80, 35], pos=[ww/2-300, 220],\
			options=bgui.BGUI_THEMED)

		#self.frame = bgui.Frame(self, 'name_box_frame', ...)
		#self.label = bgui.Label(self, 'name_box_label', ...)

		self.visible = False

	def banish(self):
		""" Reset the attributes and hide the name box """
		self.label.text = ''
		self.visible = False

	def display_name(self, name):
		""" Change the name of the name box, if name == '' the box will be hidden """
		self.label = name

		self.frame.size = [self.label.size[0] + PADDING * 2, self.label.size[1] + PADDING * 2]
		self.label.position = [self.frame.position[0] + PADDING, self.frame.position[1] + PADDING]

		self.visible = bool(name)