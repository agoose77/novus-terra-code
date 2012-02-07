from item import Item

class Inventory:
	""" Implements a grid based inventory such as in stalker or diablo. The items are stored in two differet places in the code.
	Firstly, in the ._items attribute which is a dictionary where the values are [item_id, item_amount] and secondly in ._item_grid
	which is a 2D array where the values are the keys to the ._items dictionary.
	"""

	def __init__(self):
		self.id = ''
		self._item_id = 0 # id count for self.items, increased everytime a new item is added
		self.name = ''
		self.size = [6, 8]

		# The values in this dict are the items in a [item_id, item_amoumt]
		# format. The keys are unique IDs assosiated to the grid
		self._items = {}

		# The item grid is a 2D list, [x][y], the value's are ID's for ._items
		self._item_grid = []
		for x in range(self.size[0]):
			self._item_grid.append([None] * self.size[1])

		# Weapon
		self.weapon_slot_1 = None
		self.weapon_slot_2 = None
		self.current_weapon = None

	@property
	def items(self):
		""" easy access to the item list """
		return list(self._items.values())

	def switch_weapon(self):
		if self.current_weapon == self.weapon_slot_1:
			self.current_weapon = self.weapon_slot_2

		if self.current_weapon == self.weapon_slot_2:
			self.current_weapon = self.weapon_slot_1

	def replace_weapon(self, weapon):
		#if self.current_weapon == self.weapon_slot_1:
		temp = __import__(weapon)
		self.weapon_slot_1 = temp.weapon()
		self.current_weapon = self.weapon_slot_1

		print("Replaced weapon!!!")

	def add_item(self, item_id, item_amount=1, pos=None):
		""" add an item into the grid.
		*** Check that the grid spaces are free before you add ***

		item_id : the id of the item to add
		item_amount : the amount to add
		pos : the position to add it in. If None it will be added into any position
		"""

		def get_pos():
			# find a place to add an item stack
			# the two outer loops iterate over every spot in the grid
			pos = None
			for x1 in range(0, self.size[0] - item.size[0] + 1):
				for y1 in range(0, self.size[1] - item.size[1] + 1)[::-1]:
					# these two inner loops iterate over the spots needed to place the item
					for x2 in range(x1, x1 + item.size[0]):
						for y2 in range(y1, y1 + item.size[1]):
							if self._item_grid[x2][y2] is not None:
								# can't place an item here
								break

						# the following crap is a deep loop break
						else:
							continue
						break
					else:
						pos = [x1, y1]
						break
					continue
				else:
					continue
				break

			return pos
		

		item = Item.items[item_id]

		if pos is None:
			# look for existing stacks to add to
			for grid_id, (id, amount) in self._items.items():
				if id == item_id and amount < item.stack:
					# we can add to it
					n = min(item.stack - amount, item_amount) # amount to add
					self._items[grid_id][1] += n
					item_amount -= n
				
			# create new stacks
			while item_amount != 0:
				pos = get_pos()

				if pos is None:
					# there are no available spaces left, return the amount of items that can't be added
					return item_amount

				# add the item into the item list
				self._items[self._item_id] = [item_id, min(item.stack, item_amount)]
				item_amount -= min(item.stack, item_amount)

				# add the item to the item grid
				for x in range(pos[0], pos[0] + item.size[0]):
					for y in range(pos[1], pos[1] + item.size[1]):
						self._item_grid[x][y] = self._item_id

				self._item_id += 1


		else:
			# add the item into the item list
			self._items[self._item_id] = [item_id, min(item.stack, item_amount)]
			item_amount -= min(item.stack, item_amount)

			# add the item to the item grid
			for x in range(pos[0], pos[0] + item.size[0]):
				for y in range(pos[1], pos[1] + item.size[1]):
					self._item_grid[x][y] = self._item_id

			self._item_id += 1

			while item_amount != 0:
				pos = get_pos()

				if pos is None:
					# no more spaces available to add to
					return item_amount

				# add the item into the item list
				self._items[self._item_id] = [item_id, min(item.stack, item_amoutn)]
				item_amount -= min(item.stack, item_amount)

				# add the item to the item grid
				for x in range(pos[0], pos[0] + item.size[0]):
					for y in range(pos[1], pos[1] + item.size[1]):
						self._item_grid[x][y] = self._item_id

				self._item_id += 1
		
		# all items were added successfully
		return True

	def add_to_stack(self, item_id, item_amount, pos):
		""" Add an item grid space which is already occupied by the same type of item """
		grid_id = self.get_id(pos)
		amount = self._items[grid_id][1]
		n = min(Item.items[item_id].stack - amount, item_amount)
		self._items[self.get_id(pos)][1] += n
		item_amount -= n

		if item_amount != 0:
			return self.add_item(item_id, item_amount)
		
		return True

	def remove_grid_id(self, grid_id):
		""" Remove and item from the grid based on its grid_id """
		for x in range(self.size[0]):
			for y in range(self.size[1]):
				if self._item_grid[x][y] == grid_id:
					self._item_grid[x][y] = None

		self._items.pop(grid_id)

	def check_pos(self, pos, size=[1,1]):
		""" Check a position to see if another item is in it, checks bounds """
		# Check if out of index bounds
		if pos[0] + size[0] > self.size[0] or pos[1] + size[1] > self.size[1]:
			return False

		for x in range(pos[0], pos[0]+size[0]):
			for y in range(pos[1], pos[1]+size[1]):
				if self._item_grid[x][y] is not None:
					# an item is in this position, return the item id
					return self._items[self._item_grid[x][y]][0]

		return True

	def clear_pos(self, pos, size=[1,1]):
		""" Clear a position in the item grid, won't check bounds """
		for x in range(pos[0], pos[0]+size[0]):
			for y in range(pos[1], pos[1]+size[1]):
				self._item_grid[x][y] = None

	def set_pos(self, grid_id, pos, size=[1,1]):
		""" Set a position in the item grid to an ID, won't check bounds """
		for x in range(pos[0], pos[0]+size[0]):
			for y in range(pos[1], pos[1]+size[1]):
				self._item_grid[x][y] = grid_id


	def get_pos(self, grid_id):
		""" Get the bottom left corner of the item associated to the grid id """
		# the first occurance of grid_id in the inventory grid is the bottom left corner of the item
		for x in range(self.size[0]):
			for y in range(self.size[1]):
				if self._item_grid[x][y] == grid_id:
					return x, y

		return None, None

	def get_id(self, pos):
		return self._item_grid[pos[0]][pos[1]]