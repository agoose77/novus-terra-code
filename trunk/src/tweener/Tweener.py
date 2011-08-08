from weakref import WeakKeyDictionary
import time

class Testor:
	def __init__(self):
		self.v = [0,0,0,0]

class TweenManager:
	def __init__(self):
		self.tweens = WeakKeyDictionary()
		
	def add(self, object, property, target, length=1.0, mode="Linear", callback=None):
		new_tween = Tween(object, property, target, length=1.0, mode="Linear", callback=callback, parent=self.tweens)
		self.tweens[new_tween] = new_tween
		
	def update(self):
		for key in self.tweens:
			key.update()

class Tween:
	"""
	This is hackish for gettinga feature in, when done it will be able to tween 
	any int or float properties (or slice of them in a list)
	Will also have all the transition functions
	"""
	def __init__(self, object, property, target, length=1.0, mode="Linear", callback=None, parent=None):
		self.parent = parent
	
		self.object = object
		self.property = property #string such as '.length' or '[2]' or '.position[0]'
		self.target = target
		self.length = length
		self.mode = mode
		self.callback = callback
		
		self.slot = None

		
		#handle [2]
		if property[-1:] == "]":
			self.slot = property[-2:-1]
			self.property = property[:-3]
		self.starting_time = float(time.time())
		if self.slot:
			self.starting_value = eval("self.object."+self.property+"["+self.slot+"]")
		else:
			self.starting_value = eval("self.object."+self.property)

		
	def update(self):
		
		try:
			if self.object:
				pass
		except:
			print("no object")
			self.parent[self] = 0
			return
		
		changed = self.LINEAR( time.time()-self.starting_time, self.starting_value, self.target, self.length )
			
		if self.slot:
			l = self.object.color
			if self.slot == "3":
				l = [l[0], l[1], l[2], changed]
				self.object.color = l
			else:
				l = [1.0,1.0,1.0]
			
		else:
			pass
		if time.time() >= self.starting_time+self.length:
			if self.callback:
				self.callback()
			self.parent[self] = 0
		
	def LINEAR(self, t, b, c, d):
		return c * t / d + b