import time

from .action import Action


class wait(Action):
	""" Wait for a number of seconds """
	def __init__(self, time=1):
		super().__init__()
		self.time = time
		self.run_time = 0

	def run(self):
		if self.run_time == 0:
			self.run_time = time.time()

		if self.run_time + self.time > time.time():
			return Action.FINISHED
		else:
			return Action.RUNNING