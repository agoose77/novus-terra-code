import time

import bge
import blf

import bgui
import ui
from item import Item

class HUD(bgui.Widget):
	""" A bgui widget that displays the contents of an inventory. Displays a single inventory, which can be linked to another one
	so items can be dragged from inventory to inventory.
	"""

	def __init__(self, parent, name, inventory=None, pos=[0,0], size=[6, 8], options=bgui.BGUI_NONE):
		""" pos is in grid spaces, not pixels! One grid space is 50x50 px
		don't pass size in normalized values!
		"""
		super().__init__(parent, name, size=[size[0]*50, size[1]*50], pos=pos, options=options)

		#self.border = ui.MetalBorder(self, 'border', size=[320, 420], pos=[-10,-10], options=bgui.BGUI_NONE)
		self.bg = bgui.Image(self, 'bg', img='./data/textures/ui/HUD.png', size=[300, 400], pos=[0,0],
			options=bgui.BGUI_NONE)


		self.interact_label = bgui.Label(self, 'interact_label', '', pos=[0.5, 0.8],
			sub_theme='interact', options=bgui.BGUI_DEFAULT | bgui.BGUI_CENTERX)
		self.interact_icon = bgui.Image(self, 'interact_icon', None)

		#self.inventory = inventory
		self.linked_inventory = None # other inventory that can be dragged to
		self.items = []

		self.hover_item = None
		self.hover_time = 0.0

		self.drag_item = None
		self.dragging = False
		self.drag_offset = [0,0]
		self.drag_start = [0,0]
		self.drag_grid_id = 0
		

		#self.redraw()


	def _draw(self):
		# grab the mouse coordinates
		pos = list(bge.logic.mouse.position)
		pos[0] *= bge.render.getWindowWidth()
		pos[1] = bge.render.getWindowHeight() - (bge.render.getWindowHeight() * pos[1])
		self.mouse = pos
    	
		super()._draw()

		# hide the description window, it will be recalled if its still needed
		#self.description_window.visible = False
