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

		### INIT ###
		print("-- VehicleBase.__init__() --")
		entities.EntityBase.__init__(self, None)
		#super().__init__()
		entities.EntityBase._wrap(self, object_name)

		### Activate Vehicle Controls
		self.vehicle_on = False

		### Vehicle Properties
		self.speed = 15
		self.acceleration = 1.0
		self.brake_amount = 0.5
		self.steer_amount = 0.5
		self.current_steer = 0
		self.gear = 1
		self.engine_sound = 0.0
		self.car_susp 	= 0.70 # suspension factor for the car
		
		###
		self.ray_pos = [child for child in self.childrenRecursive if 'ray' in child][0]
		self.rotation_speed = 0.0
		self.last_rotation = 0.0
		self.rotation_difference = 0.0
		
		###
		self.steer		= "steer"
		self.drive		= "drive"
		self.brake		= "brake"
		
		# properties body
		self.vehicle			= "vehicle"	# marks an object is a vehicle
		self.suspension			= "susp"	# overall suspension on car individual suspension on wheel
		self.turning_center		= "turningCenter"	# marks an object is turning center
		self.wheel 				= "wheel"	# marks an object is wheel
		self.susp_angle			= "suspAngle"
		self.radius				= "radius"	# wheel radius
		self.wheel_axis			= "axis"
		self.max_right_steer	= "maxRightSteer" 	# max steering to right
		self.max_left_steer		= "maxLeftSteer" 	# max steering to left
		self.max_brake			= "maxBrake"		# max brake on one wheel
		self.max_drive			= "maxDrive"		# max forward drive on one wheel
		self.max_reverse_drive	= "maxReverse"		# max reverse drive on one wheel
		self.roll				= "roll"			# Sets how much a wheel rolls (leans) to the side
		self.friction			= "friction"		# Sets the friction of a wheel
		self.compression		= "compression"		# Sets how much the suspension compresses.
		self.damping			= "damping"			# Sets the suspension damping.
		self.stiffness			= "stiffness"		# Sets the suspension stiffness.
		# defaults driving
		
		#defaults car
		self.car_drive	= 0.0 # no drive
		self.car_steer 	= 0.0 # no steering
		self.car_brake	= 0.0 # no braking
		
		# defaults wheel
		self.wheel_radius			= 1.0
		self.wheel_suspension		= 1.0
		self.wheel_roll				= 0.1
		self.wheel_friction			= 1.0
		self.wheel_compression		= 2.0
		self.wheel_damping			= 1.5
		self.wheel_stiffness		= 6.0
		self.wheel_susp_angle 		= [  0.0,	0.0, 	-1.0]
		self.wheel_axis				= [ -1.0, 	0.0,  	 0.0]
		
		self.wheel_max_drive			= 1.0
		self.wheel_max_reverse_drive	= 1.0
		self.wheel_max_brake			= 0.1
		self.wheel_max_left_steer		= 0.0
		self.wheel_max_right_steer		= 0.0
		
		#internal properties
		self.vehicle_constraint	= "__vehicle_Constraint"
		self.vehicle_wrapper 			= "__vehicleWrapper"
		self.vehicle			= "__vehicle"
		self.wheels				= "__wheels"
		self.wheel_Id			= "__wheelId"

		### BUILD VEHICLE
		self.assembleVehicle(self._data)
		self._data['build'] = True

		# HACK
		self._data['entity_base'] = self

		### Children
		self.camera = [child for child in self.childrenRecursive if 'vcam' in child][0]
		#self.camera.removeParent()

		### FSM
		self.FSM = FiniteStateMachine(self)
		self.FSM.add_state('on', self.handle_on)
		self.FSM.add_state('off', self.handle_off)
		self.FSM.add_transition('off', 'on', self.is_active)

		self.FSM.current_state = 'off'

	def _unwrap(self):
		EntityBase._unwrap(self)

	### FSM
	def is_active(self, FSM):
		return bool(self.vehicle_on)
	
	### Functions
	def defaultProperty(self, obj, propName, default):
		if not propName in obj:
			obj[propName] = default

	def getProperty(self, obj, propName, default):
		if propName in obj:
			return obj[propName]
		return default

	def convertToFloatList(self, aList):
		if type(aList) == type(''):
			aList = eval(aList)
		newList = []
		for entry in aList:
			newList.append(float(entry)) 
		
		return newList

	def degToRad(deg):
		return deg/360*2*3.14157

	def getFinalProperty(self, wheel, vehicle, propName, default):
		return self.getProperty(wheel, propName, self.getProperty(vehicle, propName, default))
	
	def onePositive(cont):
		for sensor in cont.sensors:
			if sensor.positive:
				return True
		return False
	
	def getActive(cont):
		if onePositive(cont):
			return 1
		else:
			return 0
		
		
	### Build Vehicle
	def assembleVehicle(self, vehicle):
		if self.vehicle_wrapper in vehicle:
			return
	
		vehicleWrapper = self.createConstraint(vehicle)
		
		self.defaultProperty( vehicle, self.drive,	self.car_drive)
		self.defaultProperty( vehicle, self.brake,	self.car_brake)
		self.defaultProperty( vehicle, self.steer,	self.car_steer)
		self.defaultProperty( vehicle, self.wheels,	self.findWheels(vehicle))
		
		#global values for the wheels - if not defined separate
		self.defaultProperty( vehicle, self.max_drive,			self.wheel_max_drive)
		self.defaultProperty( vehicle, self.max_reverse_drive,	self.wheel_max_reverse_drive)
		self.defaultProperty( vehicle, self.max_brake,			self.wheel_max_brake)
	
		self.assembleWheels(vehicle, vehicleWrapper)

	def createConstraint(self, carObj):
		car_PhysicsID = carObj.getPhysicsId()
		vehicle_constraint = PhysicsConstraints.createConstraint(car_PhysicsID, 0, 11)
		carObj[self.vehicle_constraint]=vehicle_constraint
		
		constraint_ID = vehicle_constraint.getConstraintId()
		vehicleWrapper = PhysicsConstraints.getVehicleConstraint(constraint_ID)
		carObj[self.vehicle_wrapper] = vehicleWrapper
	
		return vehicleWrapper
	
	###
	def findWheels(self, vehicle):
		wheels = []
		children = list(vehicle.children)
		for child in children:
			if self.wheel in child and child[self.wheel]!=0:
				wheels.append(child)		
		return wheels

	def findTurningCenter(self, vehicle):
		children = list(vehicle.children)
		for child in children:
			if self.turning_center in child and child[self.turning_center]!=0:
				return child
	

	###
	def assembleWheels(self, vehicle, vehicleWrapper):
		wheels = vehicle[self.wheels]
		wheelId = 0
		turningCenter = self.findTurningCenter(vehicle)
		if turningCenter!=None:
			rightCenterPos = Mathutils.Vector(turningCenter.worldPosition)
			vehiclePos = Mathutils.Vector(vehicle.worldPosition)
			rightCenterVec = rightCenterPos-vehiclePos
			# symetric on the x-axis
			leftCenterVec = Mathutils.Vector(rightCenterVec)
			leftCenterVec[0] = -leftCenterVec[0]
			
			rightTangente = Mathutils.Vector([1.0,0.0,0.0])
			leftTangente  = Mathutils.Vector([-1.0,0.0,0.0])
		else:
			print("warning: no turningCenter found"	)
			
		# loop through wheels and add wheels to the wrapper
		for wheel in wheels:
			
			# Determine the original position relative to the body
			pos = Mathutils.Vector(wheel.localPosition)
			
			if turningCenter!=None and not max_left_steer in wheel:
				right = applyTurningRadius(wheel, rightCenterVec, rightTangente)
				left  = applyTurningRadius(wheel, leftCenterVec,  leftTangente)
				wheel[max_right_steer] = right
				wheel[max_left_steer]  = left
			
			self.defaultProperty( wheel, self.max_left_steer,		self.wheel_max_left_steer)
			self.defaultProperty( wheel, self.max_right_steer,		self.wheel_max_right_steer)
			self.defaultProperty( wheel, self.max_drive,			vehicle[self.max_drive])
			self.defaultProperty( wheel, self.max_reverse_drive,	vehicle[self.max_reverse_drive])
			self.defaultProperty( wheel, self.max_brake,			vehicle[self.max_brake])
	
			# Remove the parent as the wheel will be part 
			# of the physics
			wheel.removeParent()
	
			radius 			= self.getFinalProperty(wheel, vehicle, self.radius, self.wheel_radius)
			roll 			= self.getFinalProperty(wheel, vehicle, self.roll, self.wheel_roll)
			friction 		= self.getFinalProperty(wheel, vehicle, self.friction, self.wheel_friction)
			compression		= self.getFinalProperty(wheel, vehicle, self.compression, self.wheel_compression)
			damping			= self.getFinalProperty(wheel, vehicle, self.damping, self.wheel_damping)
			stiffness		= self.getFinalProperty(wheel, vehicle, self.stiffness, self.wheel_stiffness)
			suspension		= self.getFinalProperty(wheel, vehicle, self.suspension, self.wheel_suspension)
			
			suspensionAngle	= self.convertToFloatList(self.getProperty(wheel, self.susp_angle, self.wheel_susp_angle))
			axis			= self.convertToFloatList(self.getProperty(wheel, self.wheel_axis, self.wheel_axis))
			
			vehicleWrapper.addWheel( 
				wheel, pos, suspensionAngle, axis,
				suspension,  radius, True )
			vehicleWrapper.setRollInfluence(roll, wheelId)
			vehicleWrapper.setTyreFriction(friction, wheelId)
			vehicleWrapper.setSuspensionCompression(compression, wheelId)
			vehicleWrapper.setSuspensionDamping(damping, wheelId)
			vehicleWrapper.setSuspensionStiffness(stiffness, wheelId)
			
			wheel[self.wheel_Id] = wheelId
			wheel[self.vehicle] = vehicle
			wheelId += 1
	
	
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
				
						
		for wheel in self._data[self.wheels]:
			id = self._data[self.wheels].index(wheel)
			vehicle_wrapper.applyEngineForce(speed, id)
				
	### Brake
	def handle_brake(self, vehicle_wrapper):
		
		###
		keyboard = bge.logic.keyboard.events
		brake = 0
		
		###
		if keyboard[bge.events.SPACEKEY]:
			brake = self.brake_amount
		
		for wheel in self._data[self.wheels]:
			id = self._data[self.wheels].index(wheel)
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
		

	###
	def handle_on(self, FSM):
		print("ON")
		vehicle_wrapper = self._data[self.vehicle_wrapper]

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
		
		### TO fix 2x crash
		#if message.positive:
		#	bge.constraints.removeConstraint(vehicle_wrapper.getConstraintId())

	def handle_off(self, FSM):
		vehicle_wrapper = self._data[self.vehicle_wrapper]
		print("OFF")

	###
	def on_interact(self, entity):
		if self.vehicle_on == False:
			print("TURNING ON ---")
			self.vehicle_on = True
			entity.current_vehicle = self
			entity.in_vehicle = True

	###
	def main(self):
		EntityBase.main(self)
		self.FSM.main()
	

