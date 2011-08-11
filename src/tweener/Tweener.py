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
			
	def nuke(self):
		for entry in self.tweens:
			self.tweens[entry] = 0
	

class Tween:
	"""
	
	property, will type check for float and int
	if property is a string it could be one of the following:
		"[*,*,1.0]" a list of any length   gameobject.position / rotation / color
			parse this to determine the length of the list and what values are changing
			check this with the target
	"""
	def __init__(self, object, property, target, length=1.0, mode="Linear", callback=None, parent=None):
		self.parent = parent
	
		self.object = object
		self.property = property #string such as 'length'
		self.target = target
		self.length = length
		self.mode = mode
		self.callback = callback

		
		self.starting_time = float(time.time())
		
		#hack to get this to work with custom KX_Game object props

		if self.property[-1:] != "]":
			self.property = "."+self.property
			
		self.starting_value = eval("self.object"+self.property)
		
		if type(target) == str:
			temp = []
			target = target.strip("[")
			target = target.strip("]")
			split_type = target.split(",")
			for entry in split_type:
				try:
					temp.append(float(entry))
				except:
					temp.append(entry)
			self.target = temp
			self.starting_value = list(self.starting_value)


	def update(self):
		
		try:
			if self.object:
				pass
			if self.object.invalid:
				self.parent[self] = 0
				return
		except:
			print("no object")
			self.parent[self] = 0
			return
		#if it's one value apply it
		#if it's a list, iterate through starting_value
		
		if type(self.starting_value) in [int, float]:
			changed = self.LINEAR( time.time()-self.starting_time, self.starting_value, self.target-self.starting_value, self.length )
			exec("self.object"+self.property+" = " + str(changed) )
		elif type(self.target) == list:
			#get the original value
			l = self.starting_value
			for i in range( len(self.target) ):
				if type(self.target[i]) != str:
					changed = self.LINEAR( time.time()-self.starting_time, self.starting_value[i], self.target[i]-self.starting_value[i], self.length )
					l[i] = changed
			exec("self.object"+self.property+" = " + str(l) )

		if time.time() >= self.starting_time+self.length:
			if self.callback:
				self.callback()
			self.parent[self] = 0
		
	def LINEAR(self, t, b, c, d):
		return c * t / d + b