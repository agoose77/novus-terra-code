import entities
import sudo


class Trigger(entities.EntityBase):
	""" An entity that when activated (by either interation, entering, or leaving
		the space the entity occupies) will trigger an event. The space the entity
		occupies is determined by the scaling of the entity.

		properties:
			* event: the filepath to the event file
			* mode: one of either 'enter', 'exit' or 'interact'
	"""

	def __init__(self, packet=None):
		super().__init__(packet)

		self.running = False  # If the event is currently running
		self.event = None  # The event object, created when it's first run
		self.in_region = False  # If the player is within the trigger region
		self.mode = None  # One of either 'enter', 'exit' or 'interact', set in _wrap()

	def _wrap(self, ob):
		super()._wrap(ob)
		self.mode = self.get('mode', 'enter')

	def on_interact(self, entity=None):
		if not self.running:
			self.run_event()

	def on_event_finish(self, code):
		self.running = False

	def run_event(self):
		""" Tell the event manager to run the event """
		self.running = True
		sudo.world.event_manager.add(self['event'], self.on_event_finish)

	def update(self):
		if self.mode != 'interact':
			ppos = sudo.player.worldPosition
			tpos = self.worldPosition
			pos = ppos - tpos
			if (abs(pos.x) < self.scaling.x and
					abs(pos.y) < self.scaling.y and
					abs(pos.z) < self.scaling.z):
				# Player is in region
				if not self.in_region and self.mode == 'enter' and not self.running:
					# Player has entered region, run event
					self.run_event()
				self.in_region = True

			else:
				# Player is not in region
				if self.in_region and self.mode == 'exit' and not self.running:
					# Player has left region, run event
					self.run_event()
				self.in_region = False
