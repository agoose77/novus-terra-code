from weakref import WeakKeyDictionary
import time

class Testor:
	def __init__(self):
		self.v = 0.0

class TweenManager:
	def __init__(self):
		self.tweens = WeakKeyDictionary()
		
	def tween(self, object, property, target, length=1.0, mode="Linear", callback=None):
		original_value = object.__dict__[property]
		self.tweens[object] = [property, original_value, target, time.time(), length, mode, callback]
		
	def update(self):
		print("?")
		for key in self.tweens:
			data = self.tweens[key]
			t = time.time()-data[3] #time since start
			b = data[1] #starting value
			c = data[2] #target value
			d = data[4]
			
			#everything is linear for now
			updated = self.LINEAR(t,b,c,d)
			print(updated, "!")
			key.__dict__[data[0]] = updated
			if updated == data[2]:
				print("Tweener: removing tween for ",key)
				self.tweens.pop(key)
			
			
			
	def LINEAR(self, t, b, c, d):
		return c * t / d + b
		
class Fader:
	def __init__(self):
		self.tweens = WeakKeyDictionary()
		
	def fadein(self, object):
		try:
			c = object.color
			c = [c[0],c[1],c[2],c[3]+.1]
			if c[3] > 1.0:
				self.tweens.pop(object)
		except:
			pass
	def add(self, object):
		self.tweens[object] = 0
		
	def update(self):
		for key in self.tweens:
			self.fadein(key)
			
			
			
			
	def LINEAR(self, t, b, c, d):
		return c * t / d + b