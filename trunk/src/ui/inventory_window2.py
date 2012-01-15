import time

import bge
import blf

import bgui
import ui
from item import Item

class InventoryWindow2(bgui.Widget):
	""" A bgui widget that displays the contents of an inventory. Displays a single inventory, which can be linked to another one
	so items can be dragged from inventory to inventory.
	"""

	def __init__(self, parent, name, inventory=None, pos=[0,0], size=[6, 8], options=bgui.BGUI_NONE):
		""" pos is in grid spaces, not pixels! One grid space is 50x50 px
		don't pass size in normalized values!
		"""
		super().__init__(parent, name, size=[size[0]*50, size[1]*50], pos=pos, options=options)

		self.border = ui.MetalBorder(self, 'border', size=[320, 420], pos=[-10,-10], options=bgui.BGUI_NONE)
		self.bg = bgui.Image(self, 'bg', img='./data/textures/ui/inventory_back.png', size=[300, 400], pos=[0,0],
			options=bgui.BGUI_NONE)

		self.description_window = bgui.Frame(self, 'description_window', size=[200, 100], pos=[0,0],
			sub_theme='description_window', options=bgui.BGUI_THEMED)
		self.description_window.visible = False
		self.description = bgui.Label(self.description_window, 'description', '', sub_theme='description', pos=[5, 80], options=bgui.BGUI_THEMED)

		self.inventory = inventory
		self.linked_inventory = None # other inventory that can be dragged to
		self.items = []

		self.hover_item = None
		self.hover_time = 0.0

		self.drag_item = None
		self.dragging = False
		self.drag_offset = [0,0]
		self.drag_start = [0,0]
		self.drag_grid_id = 0
		

		self.redraw()

	def redraw(self):
		""" Re-calculate what items are where """
		for item in self.items:
			self._remove_widget(item)

		self.items = []

		if self.inventory is not None:
			for grid_id, (item_id, item_amount) in self.inventory._items.items():
				pos = self.inventory.get_pos(grid_id)
				
				icon = './data/textures/inventory_icons/' + Item.items[item_id].icon
				size = Item.items[item_id].size
				item = bgui.Image(self, 'item_' + str(grid_id), img=icon, size=[size[0]*50, size[1]*50],
					pos=[pos[0]*50, pos[1]*50], options=bgui.BGUI_NONE)
				
				# amount of items in the stack and its shadow
				item.label1 = bgui.Label(item, 'amount1', str(item_amount), pos=[6,4], sub_theme='inventory_amount_shadow',
					options=bgui.BGUI_THEMED)
				item.label2 = bgui.Label(item, 'amount2', str(item_amount), pos=[5,5], sub_theme='inventory_amount',
					options=bgui.BGUI_THEMED)
				
				# Assign item data
				item.item_id = item_id
				item.item_amount = item_amount
				item.item_size = size
				item.item_name = Item.items[item_id].name
				item.item_description = Item.items[item_id].description

				# Setup event callbacks
				item.on_hover = self.handle_item_hover
				item._handle_mouse_exit = self.handle_item_exit
				item._handle_click = self.handle_item_click
				item._handle_release = self.handle_item_release

				self.items.append(item)

	def link(self, inventory):
		""" Link another inventory to drag to """
		self.linked_inventory = inventory
	
	def handle_item_click(self):
		""" Initiate item dragging """

		if self.linked_inventory and self.linked_inventory.dragging:
			# don't initiate a drag if the linked inventory is already dragging
			return

		if self.hover_item:
			self.drag_item = self.hover_item
			self.hover_item = None

			self.drag_offset = [self.mouse[0] - self.drag_item.position[0],
				self.mouse[1] - self.drag_item.position[1]]
			self.drag_start = [int(self.drag_item.position[0] - self.position[0]) // 50,
				int(self.drag_item.position[1] - self.position[1]) // 50]
			self.drag_grid_id = self.inventory._item_grid[self.drag_start[0]][self.drag_start[1]]
			self.inventory.clear_pos(self.drag_start, self.drag_item.item_size)

			self._remove_widget(self.drag_item)
			self._attach_widget(self.drag_item)
			self.parent._remove_widget(self)
			self.parent._attach_widget(self)
			
			self.dragging = True

	def handle_item_release(self):
		""" Finish item dragging, either set the item to a new position or revert it to its old one """

		if self.linked_inventory and self.linked_inventory.dragging or not self.drag_item:
			# the release is not associated with this inventory
			return

		self.dragging = False
		
		if self.position[0] < self.mouse[0] and self.mouse[0] < self.position[0] + self.size[0] \
			and self.position[1] < self.mouse[1] and self.mouse[1] < self.position[1] + self.size[1]:
			# dropped in current inventory
			pos = [int(round((self.drag_item.position[0] - self.position[0]) / 50) * 50) // 50,
				int(round((self.drag_item.position[1] - self.position[1]) / 50) * 50) // 50]
			
			check = self.inventory.check_pos(pos, self.drag_item.item_size)
			if check is True:
				self.inventory.set_pos(self.drag_grid_id, pos, self.drag_item.item_size)
				self.drag_item.position = [pos[0] * 50, pos[1] * 50]
			else:
				self.drag_item.position = [self.drag_start[0] * 50, self.drag_start[1] * 50]
				self.inventory.set_pos(self.drag_grid_id, self.drag_start, self.drag_item.item_size)

		elif self.linked_inventory \
			and self.linked_inventory.position[0] < self.mouse[0] and self.mouse[0] < self.linked_inventory.position[0] + self.linked_inventory.size[0] \
			and self.linked_inventory.position[1] < self.mouse[1] and self.mouse[1] < self.linked_inventory.position[1] + self.linked_inventory.size[1]:
			# dropped in linked inventory
			pos = [int(round((self.drag_item.position[0] - self.linked_inventory.position[0]) / 50) * 50) // 50,
				int(round((self.drag_item.position[1] - self.linked_inventory.position[1]) / 50) * 50) // 50]
			
			check = self.linked_inventory.inventory.check_pos(pos, self.drag_item.item_size)
			if  check is True:
				# dragged to an empty spot
				self.linked_inventory.inventory.add_item(self.drag_item.item_id, self.drag_item.item_amount, pos)
				self.inventory.remove_grid_id(self.drag_grid_id)
				self.redraw()
				self.linked_inventory.redraw()
			
			elif check == self.drag_item.item_id:
				# dragged onto same item type
				# add to stack in other inventory
				leftover = self.linked_inventory.inventory.add_to_stack(self.drag_item.item_id, self.drag_item.item_amount, pos)
				self.inventory.remove_grid_id(self.drag_grid_id)

				if leftover is not True and leftover > 0:
					# if not all the items could be added to the other inventory add leftovers back to the original spot
					self.inventory.add_item(self.drag_item.item_id, leftover, self.drag_start)

				self.redraw()
				self.linked_inventory.redraw()
				
			else:
				# dropped onto different item spot
				self.drag_item.position = [self.drag_start[0] * 50, self.drag_start[1] * 50]
				self.inventory.set_pos(self.drag_grid_id, self.drag_start, self.drag_item.item_size)

		else:
			# dropped in neither inventory, add to world
			pass

		self.drag_item = None

	def handle_item_exit(self):
		""" Hides the description window if an item is not being dragged """

		if self.linked_inventory and self.linked_inventory.dragging:
			return

		if not self.dragging:
			self.item_hover = None

	def handle_item_hover(self, item=None):
		""" Summon the description winndow if the mouse is over an item long enough """

		if self.linked_inventory and self.linked_inventory.dragging:
			return

		if item is None or self.dragging:
			# don't bother about the description window while an item is being dragged
			return

		if self.hover_item != item:
			# mouse has just entered an item
			self.hover_item = item
			self.hover_time = time.time()

		else:
			if time.time() > self.hover_time + 0.3:
				# mouse was already on the item and has been for that last .3 seconds
				self.description_window.visible = True
				self.description_window.position = [self.mouse[0] - self.position[0] + 5, self.mouse[1] - self.position[1] - 100 - 5]
				self.description.text = self.hover_item.item_name + "\n" + self.hover_item.item_description

				# removing and reattaching brings the description window's z position to the top
				self._remove_widget(self.description_window)
				self._attach_widget(self.description_window)

	def _draw(self):
		# grab the mouse coordinates
		pos = list(bge.logic.mouse.position)
		pos[0] *= bge.render.getWindowWidth()
		pos[1] = bge.render.getWindowHeight() - (bge.render.getWindowHeight() * pos[1])
		self.mouse = pos
    	
		if self.dragging:
			# move the item thats being dragged
			self.drag_item.position = [self.mouse[0] - self.position[0] - self.drag_offset[0],
				self.mouse[1] - self.position[1] - self.drag_offset[1]]

		super()._draw()

		# hide the description window, it will be recalled if its still needed
		self.description_window.visible = False
