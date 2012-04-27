import bge

import bgui


class ContextMenu(bgui.Widget):
	""" Displays a context menu (right-click menu) """

	def __init__(self, parent, name, items=[], pos=[0, 0], sub_theme=''):
		""" Items is a tuple of (label, callable) pairs """

		super().__init__(parent, name, size=[1, 1], pos=pos)

		PADDING = 10

		self.lines = []
		for i, item in enumerate(items):
			line = bgui.Label(self, 'line_' + str(i), item[0], sub_theme='context_menu')
			line.action = item[1]
			self.lines.append(line)

		# Get the max width and height any line
		height = 0
		width = 0
		for line in self.lines:
			if line.size[0] > width:
				width = line.size[0]
			if line.size[1] > height:
				height = line.size[1]

		ww = self.parent.size[0]
		wh = self.parent.size[1]

		# Reposition everything based on the new max width and height values
		self.size = [(width + PADDING * 2) / ww, (0 + (height + PADDING) * len(self.lines)) / wh]
		self.position[1] -= self.size[1]

		# A frame to store the lines in
		self.frame = bgui.Frame(self, 'frame', size=[1, 1], pos=[0, 0], sub_theme='context_menu')

		# A cursor for highlighting the line the mouse is over
		self.cursor = bgui.Frame(self, 'cursor', size=[self.size[0] - 4, self.size[1] / len(self.lines) - 4],
			pos=[2, 0], sub_theme='context_menu_cursor', options=bgui.BGUI_THEMED)

		# The following is done here because the size of each line had
		# to be determined before positioning could happen
		for i, line in enumerate(self.lines[::-1]):
			# Bring each line to the front
			self._remove_widget(line)
			self._attach_widget(line)

			# Position each line
			line.position = [PADDING / self.size[0], (PADDING / 2 + i * (height + PADDING)) / self.size[1]]

	def _draw(self):
		# Grab the mouse coordinates
		pos = list(bge.logic.mouse.position)
		pos[0] *= bge.render.getWindowWidth()
		pos[1] = bge.render.getWindowHeight() - (bge.render.getWindowHeight() * pos[1])

		# Determine the index of the line the cursor is over
		i = (pos[1] - self.position[1]) / (self.size[1] / len(self.lines))
		if i >= 0 and i < len(self.lines):
			# Position the cursor over that line
			self.cursor.position = [2, self.lines[::-1][int(i)].position[1] - self.position[1] - 3]
			self.cursor.visible = True

			# Reset the colour of each line
			for line in self.lines:
				line.color = [1, 1, 1, 1]

			# Highlight the colour of the selected line
			line = self.lines[::-1][int(i)]
			line.color = [0, 0, 0, 1]

			# De-attach then re-attach the line to bring it above the cursor
			self._remove_widget(line)
			self._attach_widget(line)
		else:
			# Reset the colour of each line
			for line in self.lines:
				line.color = [1, 1, 1, 1]

			# Hide the cursor
			self.cursor.visible = False

		if bge.logic.mouse.events[bge.events.LEFTMOUSE] == bge.logic.KX_INPUT_ACTIVE:
			if int(i) >= 0 and int(i) < len(self.lines):
				# The mouse was clicked on an item, call it
				self.lines[::-1][int(i)].action()
			else:
				# The mouse was clicked in empty space, hide the menu
				self.visible = False

		super()._draw()
