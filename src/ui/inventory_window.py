import math

import bgui

from item import Item
import game
import ui

class InventoryWindow(bgui.Widget):
	class Item(bgui.Widget):
		def __init__(self, parent, name, item, stack_index, count, aspect=None, size=[1,1], pos=[0,0], sub_theme='', options=bgui.BGUI_DEFAULT):
			bgui.Widget.__init__(self, parent, name, aspect, size, pos, sub_theme, options)
			
			image = './data/textures/inventory_icons/'+item.icon
			
			self.item = item
			self.stack_index = stack_index
			self.count = count
			self.on_click = self.parent.select_item
			
			csize = self.size[1]*.3
			
			self.corner1 = bgui.Image(self, 'corner1', './data/textures/ui/nbutton_corner.png', pos=[0, 0], size=[csize,csize],
				options = bgui.BGUI_CACHE, interpolate='NEAREST' )
			self.corner1.visible = 0
			
			self.corner2 = bgui.Image(self, 'corner2', './data/textures/ui/nbutton_corner.png', pos=[self.size[0]-csize, 0], size=[csize,csize],
				options = bgui.BGUI_CACHE, interpolate='NEAREST' )
			self.corner2.visible = 0
			
			self.corner3 = bgui.Image(self, 'corner3', './data/textures/ui/nbutton_corner.png', pos=[0, self.size[1]-csize], size=[csize,csize],
				options = bgui.BGUI_CACHE, interpolate='NEAREST' )
			self.corner3.visible = 0
			
			self.corner4 = bgui.Image(self, 'corner4', './data/textures/ui/nbutton_corner.png', pos=[self.size[0]-csize, self.size[1]-csize], size=[csize,csize],
				options = bgui.BGUI_CACHE, interpolate='NEAREST' )
			self.corner4.visible = 0
			
			self.corner1.texco=[ (0,1), (0,0), (1,0), (1,1)]
			self.corner2.texco=[ (1,1), (0,1), (0,0), (1,0)]
			self.corner4.texco=[ (1,0), (1,1), (0,1), (0,0)]
			self.corners = [self.corner1, self.corner2, self.corner3, self.corner4]
			
			#self.frame = bgui.Frame(self, 'asd', size=[1,1], pos=[0,0], options=bgui.BGUI_DEFAULT)
			self.image = bgui.Image(self, 'image', image, size=[1,1], options = bgui.BGUI_CACHE | bgui.BGUI_DEFAULT | bgui.BGUI_CENTERED )
			self.amount = bgui.Label(self, 'amount', text="x5", pt_size=32, color=[1,.9,0,1], 
				pos = [self.size[0]*.5, self.size[0]*.75 ], font='./data/fonts/olney_light.otf', options=bgui.BGUI_NONE)
			
		def select(self):
			for corner in self.corners:
				corner.visible = 1
			
		def deselect(self):
			for corner in self.corners:
				corner.visible = 0
	
	def __init__(self, parent, name, inventory, aspect=None, size=[1,1], pos=[0,0],
			sub_theme='', options=bgui.BGUI_DEFAULT):
		bgui.Widget.__init__(self, parent, name, aspect, size, pos, sub_theme, options)
		
		self.inventory = inventory
		self.top = 0 # the row number that is displayed at the top of the window
		self.frame = bgui.Frame(self, 'frame', sub_theme='inventory_window', size=[1,1], pos=[0,0])
		self.scrollbar = ui.Scrollbar(self, '_scrollbar', pos=[1-10/self.size[0],0], size=[10/self.size[0], 1], sub_theme='Vertical')
		self.scrollbar.on_scroll = self.scroll
		
		self.items = []
		self.redraw()
		
	def select_item(self, item):
		game.Game.singleton.sound_manager.play_sound('select.wav', None)
		if item in self.selected_items:
			self.selected_items.remove(item)
			item.deselect()
		else:
			self.selected_items.append(item)
			item.select()
	
	def redraw(self):
		for item in self.items:
			self._remove_widget(item)
		
		self.items = []
		self.selected_items = []
		
		items = list(self.inventory.items.keys())
		size = 110
		n = 0
		for id in items:
			item = Item.items[id]
			for j in range(len(self.inventory.items[id])):
				x = n % 3
				y = n // 3
				self.items.append(InventoryWindow.Item(self, 'item_'+item.name+'_'+str(n), item, j,
						self.inventory.items[id][j], size=[size, size], options=bgui.BGUI_NONE,
						pos=[x*size, self.size[1] + self.parent.position[1] - (y+1)*size]))
				self.items[-1].amount.text = 'x' + str(self.inventory.items[id][j])
				
				if y >= self.size[1] // 110:
					self.items[-1].visible = 0
				
				n += 1
		
		count = 0
		for stacks in self.inventory.items.values():
			count += len(stacks)
		if count == 0:
			size = self.size[1]
			self.scrollbar.slider_size = size
			self.scrollbar.slider_position = 1 - size
		else:
			size = (self.size[1] / 110) / math.ceil(count / 3)
			self.scrollbar.slider_size = size
			self.scrollbar.slider_position = 1 - size
		
		self.scrollbar_scale = size
		
	def scroll(self, scrollbar):
		pos = (self.size[1] - self.scrollbar.slider_position - self.scrollbar.slider_size + self.position[1]) / self.scrollbar_scale
		top = (pos + 55) // 110
		if top > self.top:
			dif = top - self.top
			self.top = top
			
			for item in self.items:
				item.position = [item.position[0]-self.position[0],item.position[1]-self.position[1]+110*dif]
				if item.position[1] < self.position[1] or item.position[1] >= self.size[1] + self.position[1]:
					item.visible = 0
				else:
					item.visible = 1
		elif top < self.top:
			dif = self.top - top
			self.top = top
			for item in self.items:
				item.position = [item.position[0]-self.position[0],item.position[1]-self.position[1]-110*dif]
				if item.position[1] < self.position[1] or item.position[1] >= self.size[1] + self.position[1]:
					item.visible = 0
				else:
					item.visible = 1
	

"""
class InventoryWindow(bgui.Widget):
	def __init__(self, parent, name, inventory, aspect=None, size=[1, 1], pos=[0, 0],
				sub_theme='', options=bgui.BGUI_DEFAULT):
		bgui.Widget.__init__(self, parent, name, aspect, size, pos, sub_theme, options)
		
		area = self.parent.image_back
		self.frame = bgui.Frame(self, 'frame', pos=area.position, size = area.size, options=bgui.BGUI_CENTERX)
		self.frame.colors = [ [1,0,0,0]]*4
		self.back1 = Fut_Box(self.frame, 'back1', pos=[250,0], size = [450, 450], options=bgui.BGUI_NONE)

		self.inventory = inventory
		self.items = []

	def reconstruct_inv(self):
		for entry in self.items:
			self.frame._remove_widget(entry)
		self.items = []

		temp_items = []
		for entry in self.inventory.items:
			temp_items.append(entry)

		size = 110
		counter = 0
		for j in range(3):
			for i in range(4):
				if counter < len(temp_items):
					item = temp_items[counter]
					imageicon = './data/textures/inventory_icons/'+item.icon
					imagename = item.name
					new_item_widget = Ninv_icon(self.frame, str(i)+str(j), image=imageicon,text=imagename, pos = [((size+10)*i+335),
												( 370 - (size+10)*j)], size = [size, size], options=bgui.BGUI_NONE)
					self.items.append( new_item_widget )
					if session.game.world.player.inventory.items[item] > 1:
						new_item_widget.amount.text = 'x'+str( session.game.world.player.inventory.items[item] )
				counter += 1
				
	def button_logic(self, button):
		if button in self.items:
			for entry in self.items:
				entry.active = 0
			button.active = 1
"""