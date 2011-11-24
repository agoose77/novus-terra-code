import time

class Profiler:
	"""
	
	"""
	def __init__(self):
		self.gauges = {}
		self.since_announce = {}
		self.record = {}
		self.update_every = .5
		
	def start_timer(self, name):
		self.gauges[name] = time.time()
		if name not in self.since_announce:
			self.since_announce[name] = time.time()
			
	def stop_timer(self, name):
		if name not in self.record:
			self.record[name] = []
		self.record[name].append( time.time()-self.gauges[name] )
		if time.time() - self.since_announce[name] > 2:
			print('{'+name+'} '+str( self.mean(self.record[name]) ) )
			self.record[name] = []
			self.since_announce[name] = time.time()

	def mean(self, numberList):
		if len(numberList) == 0:
			return float('nan')
	 
		floatNums = [float(x) for x in numberList]
		return sum(floatNums) / len(numberList)