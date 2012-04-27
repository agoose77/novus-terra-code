import events


class EventManager:
	""" Manages a list of running events, updating them each frame
	and removing them when finished.
	"""

	def __init__(self):
		self.running_events = []  # A list of (Event, callback) pairs

	@property
	def busy(self):
		""" When True, there are events running """
		# This property should be good for saving.
		# We don't want to be able to save while
		# events are in progress.
		return len(self.running_events) > 0

	def add(self, filename, callback=None):
		""" Run an event """
		event = events.Event.parse(filename)
		self.running_events.append((event, callback))
		return event

	def main(self):
		""" Update each running event """
		for event, callback in self.running_events:
			# Run the event
			code = event.run()

			if code == events.Event.FINISHED:
				# Event has finished running, remove it from the list
				self.running_events.remove((event, callback))

				if callback is not None:
					callback(events.Event.FINISHED)

			elif code == events.Event.FAILED:
				# Event encountered an error and could not finish,
				# remove it from the list
				self.running_events.remove((event, callback))

				if callback is not None:
					callback(events.Event.FAILED)
