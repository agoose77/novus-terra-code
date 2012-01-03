import bge

import bgui
import game
import tweener
import ui

class ItemSwap(ui.Screen):
	def __init__(self, parent, name):
		super().__init__(parent, name, blocking=True)
		
		ww = parent.size[0]
		wh = parent.size[1]
		
		# a frame to darken the game screen
		self.backdrop = bgui.Frame(self, 'backdrop', size=[1,1], pos=[0,0])
		self.backdrop.colors = [(0,0,0,0.55)]*4
		
		self.player_inventory = ui.InventoryWindow(self, 'player_inventory',
			game.Game.singleton.world.player.inventory, size=[340, 440], pos=[ww//2-400, 0],
			options=bgui.BGUI_CENTERY)
		self.other_inventory = None
		
		self.player_label = bgui.Label(self, 'player_label', 'Player', pt_size=64,
			color=[1,1,1,1], font='./data/fonts/olney_light.otf', pos=[ww//2 - 400,
			wh//2 + 220 + 10], options=bgui.BGUI_NONE)
		self.other_label = bgui.Label(self, 'other_label', '', pt_size=64,
			color=[1,1,1,1], font='./data/fonts/olney_light.otf',
			pos=[ww//2 + 60, wh//2 + 220 + 10], options=bgui.BGUI_NONE)
		
		self.swap_button = bgui.Image(self, 'swap_iamge', './data/textures/ui/inv_swap.png',
			size=[110, 110], options=bgui.BGUI_CENTERED)
		self.swap_button.on_click = self.swap
		
		self.tabs = ui.InventoryWindow.Tabs(self, 'tabs', pos=[ww//2 - 400 - 197, wh//2 - 235],
			inventories=[self.player_inventory, self.other_inventory])
		
		self.return_but = ui.Fut_Button(self, 'return', pos=[ww//2 - 400 - 192, wh//2 - 220 - 10],
			size=[182, 45], text="BACK", options=bgui.BGUI_NONE)
		self.return_but.on_click = self.return_
		self.tweener = tweener.TweenManager()
		self.hook = 0.0 # for tweener
		
	def return_(self, widget):
		bge.render.setMousePosition(bge.render.getWindowWidth()//2, bge.render.getWindowHeight()//2)
		self.tweener.add(self, "hook", 3, length=0.01, callback=game.Game.singleton.ui_manager.hide('item_swap'))
		
	def set_inventory(self, inventory):
		ww = self.parent.size[0]
		wh = self.parent.size[1]
		self.other_inventory = ui.InventoryWindow(self, 'other_inventory', inventory, size=[340, 440],
			pos=[ww//2+60, 0], options=bgui.BGUI_CENTERY)
		self.tabs.inventories = [self.player_inventory, self.other_inventory]
		self.other_label.text = inventory.name
		
	def swap(self, widget):
		player_items = []
		to_remove = []
		for item in self.player_inventory.selected_items:
			player_items.append((item.item.id, item.count))
			to_remove.append((item.item.id, item.stack_index))
			self.player_inventory.items.remove(item)
			self.player_inventory._remove_widget(item)
			
		to_remove = sorted(to_remove, key=lambda n: n[1])[::-1]
		for id, index in to_remove:
			self.player_inventory.inventory.remove_item(id, index)
			
		other_items = []
		to_remove = []
		for item in self.other_inventory.selected_items:
			other_items.append((item.item.id, item.count))
			to_remove.append((item.item.id, item.stack_index))
			self.other_inventory.items.remove(item)
			self.other_inventory._remove_widget(item)
			
		to_remove = sorted(to_remove, key=lambda n: n[1])[::-1]
		for id, index in to_remove:
			self.other_inventory.inventory.remove_item(id, index)
			
		for item in player_items:
			self.other_inventory.inventory.add_item(*item)
			
		for item in other_items:
			self.player_inventory.inventory.add_item(*item)
			
		self.player_inventory.redraw()
		self.other_inventory.redraw()

	def show(self, args=[]):
		self.set_inventory(args[0])
		super().show()
		
	def main(self):
		self.tweener.update()
