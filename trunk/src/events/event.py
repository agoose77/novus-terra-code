import xml.etree.ElementTree as ElementTree
import events.actions as actions

class Event:
	_current_event = None
	FINISHED = 0
	RUNNING = 1
	FAILED = 2

	def __init__(self):
		Event._current_event = self
		self.action_stack = []

	def register_action(self, action):
		self.action_stack.append(action)

	def run(self):
		if len(self.action_stack) == 0:
			return Event.FINISHED
		else:
			code = self.action_stack[-1].run()
			if code == actions.Action.FINISHED:
				self.action_stack.pop(-1)
			elif code == actions.Action.FAILED:
				print('failed')
				return Event.FAILED
			return Event.RUNNING

	@staticmethod
	def parse(filename):
		event = Event()
		xml = ElementTree.parse(filename)
		root = xml.getroot()
		for child in root:
			actions.Action.parse(child)
		return event