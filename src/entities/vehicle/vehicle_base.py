import sys
sys.path.append('./src/')
sys.path.append('./src/weapons/')
sys.path.append('./src/entities/')


import math
import random
import aud
import bge
from mathutils import Vector, Matrix

from sound_manager import SoundManager
from inventory import Inventory
from dialogue_system import DialogueSystem
from finite_state_machine import FiniteStateMachine
from paths import PATH_SOUNDS, PATH_MUSIC

import entities
from item import Item
from weapon import Weapon

import game
import ui


###
import mathutils as Mathutils
import PhysicsConstraints

from entity_base import EntityBase


###
class VehicleBase(EntityBase):
	
	### INIT
	def __init__(self, object_name):

		print("-- VehicleBase.__init__() --")
		entities.EntityBase.__init__(self, None)
		entities.EntityBase._wrap(self, object_name)
		self.vehicle_wheels = None


		### Vehicle Properties
		self.speed = 15
		self.acceleration = 1.0
		self.brake_amount = 0.5
		self.steer_amount = 0.5
		self.car_susp 	= 0.70 # suspension factor for the car

		self.gear = 1
		self.engine_sound = 0.0

		
		### Wheel properties
		self.wheel_radius			= 1.0
		self.wheel_suspension		= 1.0
		self.wheel_roll				= 0.1
		self.wheel_friction			= 1.0
		self.wheel_compression		= 2.0
		self.wheel_damping			= 1.5
		self.wheel_stiffness		= 6.0
		self.wheel_susp_angle 		= [0.0,0.0,-1.0]
		self.wheel_axis				= [-1.0,0.0,0.0]

		
		### DONT MESS WITH THESE
		self.wheel_max_drive			= 1.0
		self.wheel_max_reverse_drive	= 1.0
		self.wheel_max_brake			= 0.1
		self.wheel_max_left_steer		= 0.0
		self.wheel_max_right_steer		= 0.0

		###
		self.car_drive	= 0.0
		self.car_steer 	= 0.0
		self.car_brake	= 0.0
		self.current_steer = 0

		###
		self.ray_pos = [child for child in self.childrenRecursive if 'ray' in child][0]
		self.rotation_speed = 0.0
		self.last_rotation = 0.0
		self.rotation_difference = 0.0

		### Activate Vehicle Controls
		self.vehicle_on = False

		# HACK
		self._data['entity_base'] = self
		self.camera = [child for child in self.childrenRecursive if 'vcam' in child][0]

		for child in self.childrenRecursive:
			if 'remove' in child:
				child.removeParent()
				#pass

		self.camera.removeParent()

		### FSM
		self.FSM = FiniteStateMachine(self)
		self.FSM.add_state('on', self.handle_on)
		self.FSM.add_state('off', self.handle_off)
		self.FSM.add_transition('off', 'on', self.is_active)

		self.FSM.current_state = 'off'

		### BUILD VEHICLE
		self.assembleVehicle(self._data)
		self._data['build'] = True

	def _unwrap(self):
		EntityBase._unwrap(self)

	

	### Functions
	def findWheels(self, vehicle):
		wheels = []
		children = list(vehicle.children)

		for child in children:
			if "wheel" in child:
				wheels.append(child)
		return wheels

	def convertToFloatList(self, aList):
		if type(aList) == type(''):
			aList = eval(aList)
		newList = []
		for entry in aList:
			newList.append(float(entry)) 

		return newList


	### Build Vehicle
	def assembleVehicle(self, vehicle):	
		vehicleWrapper = self.createConstraint(vehicle)
		self.vehicle_wheels = self.findWheels(vehicle)	
		self.assembleWheels(vehicle, vehicleWrapper)

	def createConstraint(self, carObj):
		car_PhysicsID = carObj.getPhysicsId()
		vehicle_constraint = PhysicsConstraints.createConstraint(car_PhysicsID, 0, 11)
		self.vehicle_constraint = vehicle_constraint
		
		constraint_ID = vehicle_constraint.getConstraintId()
		vehicleWrapper = PhysicsConstraints.getVehicleConstraint(constraint_ID)
		
		self.wrapper = vehicleWrapper
	
		return vehicleWrapper	

	def assembleWheels(self, vehicle, vehicleWrapper):
		#wheels = self.vehicle_wheels
		wheelId = 0
		
		###
		for wheel in self.vehicle_wheels:
			#pos = wheel.localPosition
			pos = Mathutils.Vector(wheel.localPosition)
			#pos = Mathutils.Vector(wheel.localPosition)#wheel.position - wheel.parent.position

			#print (pos)
			#print (wheel.localPosition)
			#print (Mathutils.Vector(wheel.localPosition))

			wheel.removeParent()

			vehicleWrapper.addWheel( wheel, pos, self.convertToFloatList(self.wheel_susp_angle), self.convertToFloatList(self.wheel_axis), self.wheel_suspension,  wheel['radius'], True )
			vehicleWrapper.setRollInfluence(self.wheel_roll, wheelId)
			vehicleWrapper.setTyreFriction(wheel['friction'], wheelId)
			vehicleWrapper.setSuspensionCompression(self.wheel_compression, wheelId)
			vehicleWrapper.setSuspensionDamping(self.wheel_damping, wheelId)
			vehicleWrapper.setSuspensionStiffness(self.wheel_stiffness, wheelId)
			
			wheel["wheelId"] = wheelId
			wheel["vehicle"] = vehicle
			wheelId += 1
		
		print("STARTED")
	


	### Drive
	def handle_drive(self, vehicle_wrapper):
		
		###
		keyboard = bge.logic.keyboard.events
		speed = 0

		###
		if keyboard[bge.events.WKEY]:
			speed = self.speed*self.acceleration			
			
			if self.acceleration < 1.0:
				self.acceleration += 0.005
			
		elif keyboard[bge.events.SKEY]:
			speed = -self.speed*0.5
			
		else:
			if self.acceleration > 0.0:
				self.acceleration += -0.01
				
						
		for wheel in self.vehicle_wheels:
			id = self.vehicle_wheels.index(wheel)
			vehicle_wrapper.applyEngineForce(speed*wheel['maxDrive'], id)
				
	### Brake
	def handle_brake(self, vehicle_wrapper):
		
		###
		keyboard = bge.logic.keyboard.events
		brake = 0
		
		###
		if keyboard[bge.events.SPACEKEY]:
			brake = self.brake_amount
		
		for wheel in self.vehicle_wheels:
			id = self.vehicle_wheels.index(wheel)
			vehicle_wrapper.applyBraking(brake, id)
	
	### Steering
	def handle_steering(self, vehicle_wrapper):
		
		###
		keyboard = bge.logic.keyboard.events
		
		###
		if keyboard[bge.events.AKEY]:
			if self.current_steer < self.steer_amount:
				self.current_steer += 0.075#self.steer_amount
		
		elif keyboard[bge.events.DKEY]:
			if self.current_steer > -self.steer_amount:
				self.current_steer += -0.075#-self.steer_amount
			
		else:
			if self.current_steer > 0.1:
				self.current_steer += -0.075
			elif self.current_steer < -0.1:
				self.current_steer += 0.075
			else:
				self.current_steer = 0
		
		vehicle_wrapper.setSteeringValue(self.current_steer, 2)
		vehicle_wrapper.setSteeringValue(self.current_steer, 3)
		
	def handle_stablization(self):
		#ray_pos = [own.position[0],own.position[1],own.position[1]-10]
		ray = self.rayCast(self.ray_pos, self._data, 0, '', 0, 0, 0)
		
		if ray[0] == None:
			self.alignAxisToVect([0.0,0.0,1.0], 2, 0.03)			
		else:
			self.alignAxisToVect([0.0,0.0,1.0], 2, 0.01)
		


	### FSM
	def handle_on(self, FSM):
		print("ON")
		vehicle_wrapper = self.wrapper#_data[self.vehicle_wrapper]

		###
		self.handle_drive(vehicle_wrapper)
		self.handle_brake(vehicle_wrapper)
		self.handle_steering(vehicle_wrapper)
		self.handle_stablization()

		###
		self.last_rotation = self.rotation_speed
		self.rotation_speed = (vehicle_wrapper.getWheelRotation(0)+vehicle_wrapper.getWheelRotation(1))/2
		
		self.rotation_difference = self.last_rotation-self.rotation_speed
		
		### Gears
		if self.rotation_difference > 1.0:
			self.gear = 3
		elif self.rotation_difference > 0.75:
			self.gear = 2				
		elif self.rotation_difference > 0.5:
			self.gear = 1
		
		#self.engine_sound = self.rotation_difference*self.gear
		
		### TO fix reload crash
		#bge.constraints.removeConstraint(vehicle_wrapper.getConstraintId())

	def handle_off(self, FSM):
		vehicle_wrapper = self.wrapper#_data[self.vehicle_wrapper]
		print("OFF")

		# Brake amount
		brake = 0.25

		# Brake
		for wheel in self.vehicle_wheels:
			id = self.vehicle_wheels.index(wheel)
			vehicle_wrapper.applyBraking(brake, id)

	def is_active(self, FSM):
		return bool(self.vehicle_on)


	### Interact
	def on_interact(self, entity):
		if self.vehicle_on == False:
			print("TURNING ON ---")
			self.vehicle_on = True
			entity.current_vehicle = self
			entity.in_vehicle = True


	### MAIN
	def main(self):
		EntityBase.main(self)
		self.FSM.main()
		#print("R")
	

