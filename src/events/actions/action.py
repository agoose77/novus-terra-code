import events


class Action:
	""" Base class for actions """

	FINISHED = 0
	RUNNING = 1
	FAILED = 2

	def __init__(self):
		events.Event._current_event.register_action(self)

	def run(self):
		return Action.FINISHED

	@staticmethod
	def parse(node):
		getattr(events.actions, node.tag)(**node.attrib)
