


class Action:
	""" Base class for actions """

	FINISHED = 0
	RUNNING = 1
	FAILED = 2

	def __init__(self):
		events.Event._current_event.register_action(self)

		self.error_msg = ''

	def run(self):
		""" Called every tick while the action is running.
		Must return one of Action.RUNNING, Action.FINISHED or
		Action.FAILED depending on it's state """
		return Action.FINISHED

	@staticmethod
	def parse(node):
		""" Parses an xml node, called from Event.parse """
		getattr(events.actions, node.tag)(**node.attrib)

import events