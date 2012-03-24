from events.actions.Action import FINISHED, FAILED
import events.actions as actions
import xml.etree.ElementTree as ElementTree


class Event:
	_current_event = None
	FINISHED = 0
	RUNNING = 1
	FAILED = 2

	def __init__(self):
		Event._current_event = self
		self.action_stack = []

	def register_aciton(self, action):
		self.action_stack.append(action)

	def run(self):
		if len(self.action_stack) == 0:
			return Event.FINISHED
		else:
			code = self.action_stack[-1].run()
			if code == FINISHED:
				self.action_stack.pop(-1)
			elif code == FAILED:
				print('failed')
				return Event.FAILED
			return Event.RUNNING

	@staticmethod
	def parse(filename):
		event = Event()
		xml = ElementTree.parse(filename)
		root = xml.getroot()
		for child in root:
			actions.Actions.parse(child)
		return event
