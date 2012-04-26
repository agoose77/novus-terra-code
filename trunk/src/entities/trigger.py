import entities
import events
import sudo


class Trigger(entities.EntityBase):
	""" An entity that when activated (by either interation, entering or leaving
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
		self.trigger = False  # If the event should be created

		self.mode = None  # One of either 'enter', 'exit' or 'interact', set
						  # in _wrap

	def _wrap(self, ob):
		super()._wrap(ob)
		self.mode = self.get('mode', 'enter')

	def on_interact(self, entity=None):
		self.trigger = True

	def update(self):
		if self.trigger:
			# The event needs to be run for the first time
			self.event = events.Event.parse(self['event'])
			self.running = True
			self.trigger = False

		elif self.running:
			# Run the event
			code = self.event.run()

			if code == events.Event.FINISHED:
				# Event has finished running
				self.running = False
				self.event = None
			elif code == events.Event.FAILED:
				# Event encountered an error and could not finish
				self.running = False
				self.event = None

		elif self.mode != 'interact':
			ppos = sudo.player.worldPosition
			tpos = self.worldPosition

			if (abs(tpos.x - ppos.x) < self.scaling.x and
					abs(tpos.y - ppos.y) < self.scaling.y and
					abs(tpos.z - ppos.z) < self.scaling.z):
				# Player is in trigger region
				if not self.in_region:
					# Player has entered region for first time
					self.in_region = True
					if self.mode == 'enter':
						self.trigger = True

			elif self.in_region:
				# Player has left the region for the first time
				self.in_region = False
				if self.mode == 'exit':
					self.trigger = True
