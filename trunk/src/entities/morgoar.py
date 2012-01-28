import entities
import sudo
import bge, random
import tweener
import time
""" editor properties:
 - dialogue - a string of the dialogue file, minus the path and file extension
 """
class Morgoar(entities.EntityBase):
	""" A simple entity for talking to """
	def __init__(self, packet=None):
		super().__init__(packet)

		self.interact_label = 'Talk'
		self.health = 200
		#self.localScale = self.localScale * (1+random.random*.3)
		self.update_time = time.time() + random.random()
		self.ticker = 1.0
		self.ai_state = None
		self.alert_radius = 80
		self.speed = 8
		print ('ghost init')

	def on_interact(self, player):
		sudo.world.dialogue_manager.display_dialogue('./data/dialogue/' + self['dialogue'] + '.xml')

	def update(self):
		
		if time.time()-self.update_time > self.ticker:
			self.update_time = time.time()

			if self.health < 200:
				self.health += 5
			if self.health < 0:
				pass	
			elif self.health < 70:
				self['Steer'] = 0
				loc = sudo.world.player.position
				l = [self.position[0]-loc[0], self.position[1]-loc[1], 0]
				self._data.alignAxisToVect(l, 1, 1.0)
				self._data.alignAxisToVect([0,0,1], 2, 1.0)

				self._data.setLinearVelocity( [0,self.speed*1.5,-3], True)

			elif self._data.getDistanceTo( sudo.world.player.position ) < 4:
				self['Steer'] = 0
				self.ai_state ='attacking'
				if not self._data.children[0].isPlayingAction(6):
					if random.randint(0,1) == 0:
						self._data.children[0].playAction('attack1',0,20,6,0,10, bge.logic.KX_ACTION_MODE_PLAY, speed=1.0)
					else:
						self._data.children[0].playAction('attack2',0,28,6,0,10, bge.logic.KX_ACTION_MODE_PLAY, speed=1.0)

			elif self._data.getDistanceTo( sudo.world.player.position ) < self.alert_radius or self.ai_state == 'hunting':
				self.move_to( sudo.world.player._data, behavior=3)
				self.ai_state = 'hunting'

			
			
			else:
				self.dick_around()

		
					# # just track to
					# # if sudo.world.player.position:
					# 	loc = sudo.world.player.position
					# 	l = [loc[0]-self.position[0], loc[1]-self.position[1], 0]
					# 	self._data.alignAxisToVect(l, 1, 1.0)
					# 	self._data.alignAxisToVect([0,0,1], 2, 1.0)

					# 	self._data.setLinearVelocity( [0,6,-3], True)


	def dick_around(self):
		roll = random.randint(0,100)
		if not self._data.children[0].isPlayingAction(5):
			if roll < 10:
				self._data.children[0].playAction('all',0,20,5,0,10, bge.logic.KX_ACTION_MODE_PLAY, speed=0.5)
			elif roll < 30:
				self._data.children[0].playAction('all',130,140,5,0,10, bge.logic.KX_ACTION_MODE_PLAY, speed=1.0)

	def flee(self):
		pass

	def hunt(self, target):
		pass


	def damage(self, amount=1, object=None):
		self.health -= amount
		self.color = [1.0,self.health*.01,self.health*.01, 1.0]
		if self.health < 0:
			self._data.children[0].playAction('die',0,20,0,0,10, bge.logic.KX_ACTION_MODE_PLAY, speed=1.0)
			tweener.singleton.add(self._data, "color", "[*,*,*,0.0]", 2.0, callback=self.remove)


	def move_to(self, target_obj, behavior=3):
		self._data.children[0].playAction('walk',0.0,40.0,0,2,4, bge.logic.KX_ACTION_MODE_LOOP, speed=1.0)

		navmesh = self.find_navmesh()
		if navmesh:		
			st = self.controllers[0].actuators['Steering']
			st.behaviour = behavior
			st.velocity = 10
			st.acceleration = 0.5
			st.turnspeed = 10
			st.target = target_obj
			st.navmesh = navmesh
			# Activate it
			self['Steer'] = 1
			return True
