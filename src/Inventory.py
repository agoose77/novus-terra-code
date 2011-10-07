from item import Item

class Inventory:
	def __init__(self):
		self.items = {}
		self.weapons = {}

        # Weapons
		self.weapon_slot_1 = None
		self.weapon_slot_2 = None
		self.current_weapon = self.weapon_slot_1

		#
		self.current_items_count = 0
		self.max_items = 100#-1

	def has_item(self, item_id, amount=1):
		if item_id in self.items.keys():
			return self.items[item_id] >= amount
		else:
			return False

	def take_items(self, items, destination=None):
		for (item_id, amount) in items.items():
			self.add_item(item_id, -amount)
			destination.add_item(item_id, amount)

	def add_item(self, item_id, amount=1):
		print ('added items 123')

		#if self.current_items_count + amount * Item.items[item_id].size < self.max_items or\
		#		self.max_items == 1:

		### Test to fix name
		if self.current_items_count + amount < self.max_items or self.max_items == 1:
			if item_id in self.items.keys():
				self.items[item_id] += amount
				self.current_items_count += Item.items[item_id].size * amount
			else:
				self.items[item_id] = amount
				self.current_items_count += amount#Item.items[item_id] * amount

			if self.items[item_id] <= 0:
				self.current_items_count += Item.items[item_id] * (amount - self.items[item_id])
				self.items.pop(item_id)

			return True
		else:
			return False


	def add_items(self, items):
		for (item_id, amount) in items.items():
			self.add_item(item_id, amount)

	def drop_item(self, item_id, amount=1):
		self.add_item(item_id, -amount)

		# add to world

	def use_item(self, item_id, amount=1):
		pass

	def switch_weapon(self):
		if self.current_weapon == self.weapon_slot_1:
			self.current_weapon = self.weapon_slot_2

		if self.current_weapon == self.weapon_slot_2:
			self.current_weapon = self.weapon_slot_1

	def replace_weapon(self, weapon):
		print('--------------')
		print(weapon)
		print('--------------')

		if self.current_weapon == self.weapon_slot_1:
			if self.weapon_slot_1 == None:
				if self.weapon_slot_2 == None:
					self.weapon_slot_2 = self.weapon_slot_1

				self.weapon_slot_1 = weapon
				self.current_weapon = self.weapon_slot_1


		elif self.current_weapon == self.weapon_slot_2:
			if self.weapon_slot_2 == None:
				if self.weapon_slot_1 == None:
					self.weapon_slot_1 = self.weapon_slot_2

				self.weapon_slot_2 = weapon
				self.current_weapon = self.weapon_slot_2




