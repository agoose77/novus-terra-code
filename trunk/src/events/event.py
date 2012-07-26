import xml.etree.ElementTree as ElementTree
import events.actions as actions


class Event:
	""" Events are composed by a sequence of Actions.
	Events are stored in xml files in the form:
	<event>
		<action_name1 action_param1='value' action_param2='value2' />
		<action_name2 action_param1='value' action_param2='value2' />
	</event>
	The name of the action directly corresponds to its class name
	and the parameters are that of it's init method.
	"""

	_current_event = None
	FINISHED = 0
	RUNNING = 1
	FAILED = 2

	def __init__(self, filename=''):
		Event._current_event = self
		self.action_stack = []

		self.filename = filename

	def register_action(self, action):
		self.action_stack.append(action)

	def run(self):
		if len(self.action_stack) == 0:
			return Event.FINISHED
		else:
			code = self.action_stack[0].run()
			if code == actions.Action.FINISHED:
				self.action_stack.pop(0)
			elif code == actions.Action.FAILED:
				print('[Error] ' + self.filename,)
				if self.action_stack[0].error_msg:
					print(':\n\t' + self.action_stack[0].error_msg)
					
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