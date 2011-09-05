class BehaviorTree:

	def __init__(self, parent):
		self.parent = parent
		self.nodes = {}

	def add_condition(self, node_name, condition, parent_name=None):

		if parent_name != None:
			if self.nodes[parent_name]['children'][node_name]:
				self.nodes[parent_name]['children'][node_name] = {'conditions':[], 'actions':[], 'children':{}}
			self.nodes[parent_name]['children'][node_name]['conditions'].append(condition)

		else:
			if self.nodes['Hungry']:
				self.nodes[node_name] = {'conditions':[], 'actions':[], 'children':{}}
			self.nodes[node_name]['conditions'].append(condition)

	def add_action(self, node_name, action=None):
		self.nodes[node_name]['actions'].append(action)

	def main(self):
		for node in self.nodes:

			# IF diction isn't empty
			if self.nodes[node]['conditions']:
				con = []

				for condition in self.nodes[node]['conditions']:
					called = condition()
					if called == True:
						con.append(called)

				if len(con) == len(self.nodes[node]['conditions']):
					for action in self.nodes[node]['actions']:
						action() # Call it


			# If it has children
			if self.nodes[node]['children']:
				print ('Got Children')