###
### X-Particles - Particle Systems for the X-Emitter
###
### Author: SolarLune
### Date Updated: 8/26/11

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
### This script, code, materials, and textures
### are under the 'do what you wish' license
### agreement under a single condition. 
### You may use any part of the 'X-Emitter' scene
### and/or scripts in your own works, commercial,
### educational, or personal, for free, -WITH- ATTRIBUTION.
###
###
### This script and associated blend file(s) are also the sole property of the Author, 
### SolarLune - even if you should edit the script, it is still the property of the 
### Author, and as such, he still has rights to the material contained within the script and blend file(s).
### He may at any time revoke rights for legal usage of this script and associated blend file at any time,
### for any reason.
###
### By using this script, you agree to this license agreement.
###
### You may NOT edit this license agreement.
###
### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from bge import logic
from mathutils import *

def Generic(particlelist):

	"""
	Author: SolarLune (Josiah Lane)
	Date Updated: 4/26/11
	License: Custom - users of this script can use this script for any purpose, commercial or otherwise, with attribution.
	
	A generic particle handling script. Works for most kinds of particle effects.	
	"""

	sce = logic.getCurrentScene()
	cont = logic.getCurrentController()
	
	always = cont.sensors[0]
	freq = always.frequency + 1
	f = freq
	
	cam = sce.active_camera

	particles = particlelist[:] # Make a copy of the array
	
	def Init(obj, override = 0):
	
		if not 'init' in obj or override == 1:
				
			obj['init'] = 1
			obj['sf'] = 0.0 
			
			if obj.parent == None:
				obj['scale'] = obj.scaling.copy()
			else:
				obj['scale'] = obj.localScale.copy()           # Original scale of the particle
				
			if not 'emitter' in obj:                    # Owner emitter object
				obj['emitter'] = None
		
			obj['time'] = 0.0                           # Time before death
			
			obj['alpha'] = 0.0
			
			if not 'speed' in obj:
				obj['speed'] = [0.0, 0.0, 0.0]
			if not 'forcespd' in obj:					# Force speed
				obj['forcespeed'] = [0.0, 0.0, 0.0]
				
			if not 'friction' in obj:                   # Default friction for the particle; if 1, then the smoke won't slow down
				obj['friction'] = [0.0, 0.0, 0.0]
			if not 'growrate' in obj:
				obj['growrate'] = 0.02                  # Default growth rate
			if not 'force' in obj:
				obj['force'] = [0.0, 0.0, 0.0]        # Force on a given axis (constant or stacking)
			if not 'forcecompound' in obj:         		# Whether the force grows over time (i.e. with z-axis grav. = 0.1, first frame = 0.1, second 0.2, third 0.3, etc.)
				obj['forcecompound'] = 0
			if not 'forcelocal' in obj:
				obj['forcelocal'] = 0
				
			if not 'cache' in obj:
				obj['cache'] = 0
				
			if not 'lod' in obj:
				obj['lod'] = 1
			if not 'loddist' in obj:
				obj['loddist'] = 20
				
			if not 'collide' in obj:
				obj['collide'] = 0
			if not 'collidevar' in obj:
				obj['collidevar'] = None
				
			if not 'startalpha' in obj:
				obj['startalpha'] = obj.color[3]            # Original (starting) alpha (alpha to get up to when fading in)
			
			if not 'fadeout' in obj:
				obj['fadeout'] = 40.0
				
			if not 'fadein' in obj:
				obj['fadein'] = 0.0
			
			obj['fadingin'] = 0
				
			if obj['fadein'] > 0.0:
				obj.color = [obj.color[0], obj.color[1], obj.color[2], 0.0] # Set the alpha to 0 to fade in from
				obj['fadingin'] = 1

			if not 'movelocal' in obj:    
				obj['movelocal'] = 0
		
			if not 'prototype' in obj:
				obj['prototype'] = 0
			
			obj['protoindex'] = 0
		
			obj['skip'] = 0								# Particle calculation LOD based on life
		
			if not 'life' in obj:   
				obj['life'] = 40                        # Default number of frames that the particle lives
				
			obj['frictionon'] = 0                       # A simple check I do to make sure that friction is on; this reduces logic load on the CPU
			obj['forceon'] = 0                        # Another simple check to make sure that force is on, reducing logic load
			obj['speedon'] = 0							# Another check for speed
			
			if obj['friction'][0] != 0 or obj['friction'][1] != 0 or obj['friction'][2] != 0:  # Don't compute all this stuff if friction isn't on
				obj['frictionon'] = 1
				
			if obj['force'][0] != 0 or obj['force'][1] != 0 or obj['force'][2] != 0:  # Don't compute all this stuff if force isn't on
				obj['forceon'] = 1
			
			if obj['speed'][0] != 0 or obj['speed'][1] != 0 or obj['speed'][2] != 0:
				obj['speedon'] = 1
			
			obj['origscale'] = obj['scale'].copy()
			obj['origspd'] = obj['speed'][:]	
			obj['origpos'] = obj.worldPosition.copy()
			
			if obj['emitter'] != None and not obj['emitter'].invalid:
				obj['origoff'] = obj['emitter'].worldPosition.copy() - obj.worldPosition.copy()
			else:
				obj['origoff'] = obj.worldPosition.copy()
				
			obj['origcolor'] = obj.color[:]
	
	for x in range(len(particles)):
	
		obj = particles[x]
	
		Init(obj)
		
		#emitter = obj['emitter']
		
		die = 0	# By default, the particle doesn't die, but later on, in the right circumstances, this variable will show that it should end

		##### PARTICLE UPDATE #####
		
		amproto = 0
		if obj['emitter'].invalid or obj['emitter'] == None:
			obj['prototype'] = 0
		else:
			amproto = obj == obj['emitter']['firstparticle']
		
		if obj['prototype'] == 1 and not amproto and not obj['emitter']['protodone'] == None:
		
			proto = obj['emitter']['emitterproto'][obj['protoindex']]
			
			#print (proto)
			
			color = proto[0]
			scaling = proto[1]
			spd = proto[2]
			frc = proto[3]
			
			#print (spd, frc)
		
			if spd != None:
				obj.applyMovement( [spd[0], spd[1], spd[2]], obj['movelocal'])
			if frc != None:
				obj.applyMovement( [frc[0], frc[1], frc[2]], obj['forcelocal'])
				
			obj.color = color
			obj.scaling = scaling
			
			obj['protoindex'] += 1
			
			if obj['protoindex'] >= len(obj['emitter']['emitterproto']):
				die = 1
		
		else:
		
			obj['time'] += 1.0 * f
			   
			if obj['frictionon']:
			
				obj['speed'][0] -= obj['speed'][0] * (obj['friction'][0] * f)
				obj['speed'][1] -= obj['speed'][1] * (obj['friction'][1] * f)
				obj['speed'][2] -= obj['speed'][2] * (obj['friction'][2] * f)
				
			spd = obj['speed']
				
			if obj['speedon']:				# Handle collisions
			
				if obj['collide'] != 0:
				
					pos = obj.worldPosition.copy()
					topos = pos.copy()
					
					topos.x += spd[0] * 2.0 * f
					topos.y += spd[1] * 2.0 * f
					topos.z += spd[2] * 2.0 * f
					
					col = obj.rayCast(topos, pos, 0, obj['collidevar'])

					if col[0] != None:
						if obj['collide'] == 1:		# Stop
							obj['speed'] = [0, 0, 0]
						elif obj['collide'] == 2:	# Die
							die = 1
						elif obj['collide'] == 3:	# Full reflection
							movement = Vector(obj['speed'])
							refl = movement.reflect(col[2])
							obj['speed'] = [refl.x, refl.y, refl.z]
						elif obj['collide'] == 4:	# Angled reflection
							movement = Vector(obj['speed'])
							refl = movement.reflect(col[2])
							spd = [refl.x, refl.y, refl.z]
		
				obj.applyMovement( [spd[0] * f, spd[1] * f, spd[2] * f] , obj['movelocal'])
			
			if (obj.getDistanceTo(cam) <= obj['loddist'] and obj['lod'] == 1) or obj['lod'] == 0:

				if obj['forceon']:
					
					frcspd = obj['forcespeed']

					if obj['forcecompound']:
						
						obj['forcespeed'] = [obj['forcespeed'][0] + (obj['force'][0] * f), obj['forcespeed'][1] + (obj['force'][1] * f), obj['forcespeed'][2] + (obj['force'][2] * f)]
						frcspd = obj['forcespeed']
						
					else:
						frcspd = [obj['forcespeed'][0] + (obj['force'][0] * f), obj['forcespeed'][1] + (obj['force'][1] * f), obj['forcespeed'][2] + (obj['force'][2] * f)]
									
					#frcspd = [frcspd[0] * f, frcspd[1] * f, frcspd[2] * f]
					
					#if obj['collide'] != 0:		# Handle collisions for force; disabled due to irregular movement
					
					#	pos = obj.worldPosition.copy()
					#	topos = pos.copy()
						
					#	topos.x += frcspd[0] 
					#	topos.y += frcspd[1] 
					#	topos.z += frcspd[2] 
						
					#	col = obj.rayCast(topos, pos, 0, obj['collidevar'])
						
					#	if col[0] != None:
					#		if obj['collide'] == 1:		# Stop
					#			frcspd = [0, 0, 0]
					#		elif obj['collide'] == 2:	# Die
					#			die = 1
					#		elif obj['collide'] == 3:	# Full reflection
					#			movement = mathutils.Vector(frcspd)
					#			refl = movement.reflect(col[2])
					#			obj['forcespeed'] = [refl.x, refl.y, refl.z]
					#		elif obj['collide'] == 4:	# Angled reflection
					#			movement = mathutils.Vector(frcspd)
					#			refl = movement.reflect(col[2])
					#			frcspd = [refl.x, refl.y, refl.z]

					#frcspd = obj['forcespeed']
					
					obj.applyMovement(frcspd, obj['forcelocal'])
		
				if obj['growrate'] != 0:
					obj['sf'] += obj['growrate'] * f                # Scale the smoke by the particle's growth rate
					obj.scaling = [obj['scale'].x + obj['sf'], obj['scale'].y + obj['sf'], obj['scale'].z + obj['sf']]
				
				alpha = obj['startalpha']

				if obj['fadingin']:
					
					if obj['fadein'] > 0.0 and obj['startalpha'] > 0.0:

						if obj.color[3] >= obj['startalpha']:
							obj['fadingin'] = 0
							obj.color = [obj.color[0], obj.color[1], obj.color[2], obj['startalpha']]
						else:
							rate = (float(obj['startalpha']) / float(obj['fadein'])) * f
							alpha = obj.color[3] + rate
				  
				if obj['time'] >= obj['life'] - obj['fadeout']:
					
					if obj['fadeout'] > 0.0 and obj['startalpha'] > 0.0:
						
						rate = (-float(obj['startalpha']) / float(obj['fadeout'])) * f
						alpha = obj.color[3] + rate 
				
				obj.color = [obj.color[0], obj.color[1], obj.color[2], alpha]
		   
			if amproto and obj['prototype']:	# Prototype
			
				proto = obj['emitter']['emitterproto']
				
				if obj['forceon']:
					protofrc = frcspd
				else:
					protofrc = None
					
				if obj['speedon']:
					protospd = spd	
				else:
					protospd = None
					
				stats = [obj.color.copy(), obj.scaling.copy(), protospd, protofrc]
				
				proto.append(stats)
		   
		##### PARTICLE DEATH #####
		
		if (amproto and obj['prototype']) or not obj['prototype']:
	
			if obj['fadeout'] == 1 and obj.color[3] <= 0.0:
				die = 1
				
			elif obj['time'] >= obj['life']:   # If the particle is invisible or it has been alive for longer than it's life variable,
				die = 1
				   
			elif not cam.pointInsideFrustum(obj.position) and obj['partcull']:
				die = 1
				   
		if die:
		
			if amproto:
			
				obj['emitter']['protodone'] = 1#obj['emitter']['emitterproto']
				#obj['emitterproto'] = []
				#obj['emitter']['firstparticle'] = None
			
				#print ("I was the prototype")
				
		
			if obj['cache'] and not obj['emitter'].invalid:			# If the emitter still exists and caching is on
			
				del obj['init']										# Reinitialize the object
				obj['speed'] = obj['origspd'][:]					# And reset it, because the BGE will use the same particle again
				
				obj.worldPosition = obj['emitter'].worldPosition.copy() + obj['origoff']	# Offset the object
				
				obj.scaling = obj['origscale'].copy()
				obj.color = obj['origcolor'][:]
				Init(obj)
				
				if obj['emitter']['partcache']:
					obj['emitter']['cachedone'] = 1

			else:
				particlelist.remove(obj)
				obj.endObject()                                     			# End the object

				if obj['emitter'] != None and not obj['emitter'].invalid:        # Tell the emitter that spawned you that you're gone
					obj['emitter']['emitterpartamt'] -= 1
					obj['emitter']['particles'].remove(obj)
					
def Flame(particlelist):

	"""
	Author: SolarLune (Josiah Lane)
	Date Updated: 4/26/11
	License: Custom - users of this script can use this script for any purpose, commercial or otherwise, with attribution.
	
	A generic particle handling script. Works for most kinds of particle effects.	
	"""

	sce = logic.getCurrentScene()
	cont = logic.getCurrentController()
	
	always = cont.sensors[0]
	freq = always.frequency + 1

	cam = sce.active_camera

	particles = particlelist[:] # Make a copy of the array
	
	def Init(obj, override = 0):
	
		if not 'init' in obj or override == 1:
		
			obj['init'] = 1
			obj['sf'] = 0.0 
			
			if obj.parent == None:
				obj['scale'] = obj.scaling.copy()
			else:
				obj['scale'] = obj.localScale.copy()           # Original scale of the particle
				
			if not 'emitter' in obj:                    # Owner emitter object
				obj['emitter'] = None
		
			obj['time'] = 0.0                           # Time before death
			
			obj['alpha'] = 0.0
			
			if not 'speed' in obj:
				obj['speed'] = [0.0, 0.0, 0.0]
			if not 'forcespd' in obj:					# Force speed
				obj['forcespeed'] = [0.0, 0.0, 0.0]
				
			if not 'friction' in obj:                   # Default friction for the particle; if 1, then the smoke won't slow down
				obj['friction'] = [0.0, 0.0, 0.0]
			if not 'growrate' in obj:
				obj['growrate'] = 0.02                  # Default growth rate
			
			obj['colorchange'] = 0
			obj.color = [1.0, 1.0, 0.0, obj.color[3] ]
			
			if not 'cache' in obj:
				obj['cache'] = 0
				
			if not 'lod' in obj:
				obj['lod'] = 1
			if not 'loddist' in obj:
				obj['loddist'] = 10
				
			if not 'collide' in obj:
				obj['collide'] = 0
			if not 'collidevar' in obj:
				obj['collidevar'] = None
				
			if not 'startalpha' in obj:
				obj['startalpha'] = obj.color[3]            # Original (starting) alpha (alpha to get up to when fading in)
			
			if not 'fadeout' in obj:
				obj['fadeout'] = 40.0
				
			if not 'fadein' in obj:
				obj['fadein'] = 0.0
			
			obj['fadingin'] = 0
				
			if obj['fadein'] > 0.0:
				obj.color = [obj.color[0], obj.color[1], obj.color[2], 0.0] # Set the alpha to 0 to fade in from
				obj['fadingin'] = 1

			if not 'movelocal' in obj:    
				obj['movelocal'] = 0
		
			obj['skip'] = 0								# Particle calculation LOD based on life
		
			if not 'life' in obj:   
				obj['life'] = 40                        # Default number of frames that the particle lives
				
			obj['frictionon'] = 0                       # A simple check I do to make sure that friction is on; this reduces logic load on the CPU
			obj['forceon'] = 0                        # Another simple check to make sure that force is on, reducing logic load
			obj['speedon'] = 0							# Another check for speed
			
			if obj['friction'][0] != 0 or obj['friction'][1] != 0 or obj['friction'][2] != 0:  # Don't compute all this stuff if friction isn't on
				obj['frictionon'] = 1
				
			if obj['force'][0] != 0 or obj['force'][1] != 0 or obj['force'][2] != 0:  # Don't compute all this stuff if force isn't on
				obj['forceon'] = 1
			
			if obj['speed'][0] != 0 or obj['speed'][1] != 0 or obj['speed'][2] != 0:
				obj['speedon'] = 1
			
			obj['origscale'] = obj['scale'].copy()
			obj['origspd'] = obj['speed'][:]	
			obj['origpos'] = obj.worldPosition.copy()
			
			if obj['emitter'] != None and not obj['emitter'].invalid:
				obj['origoff'] = obj['emitter'].worldPosition.copy() - obj.worldPosition.copy()
			else:
				obj['origoff'] = obj.worldPosition.copy()
				
			obj['origcolor'] = obj.color[:]
	
	for x in range(len(particles)):
	
		obj = particles[x]
	
		Init(obj)
		
		f = freq
		
		#emitter = obj['emitter']
		
		die = 0	# By default, the particle doesn't die, but later on, in the right circumstances, this variable will show that it should end

		##### PARTICLE UPDATE #####

		obj['time'] += 1.0 * f
		   
		if obj['frictionon']:
		
			obj['speed'][0] -= obj['speed'][0] * (obj['friction'][0] * f)
			obj['speed'][1] -= obj['speed'][1] * (obj['friction'][1] * f)
			obj['speed'][2] -= obj['speed'][2] * (obj['friction'][2] * f)
			
		spd = obj['speed']
		
		obj.applyMovement( [spd[0] * f, spd[1] * f, spd[2] * f] , 0)
		
		if (obj.getDistanceTo(cam) <= obj['loddist'] and obj['lod'] == 1) or obj['lod'] == 0:

			if obj['growrate'] != 0:
				obj['sf'] += obj['growrate'] * f                # Scale the smoke by the particle's growth rate
				obj.scaling = [obj['scale'].x + obj['sf'], obj['scale'].y + obj['sf'], obj['scale'].z + obj['sf']]
			
			alpha = obj['startalpha']

			if obj['time'] >= obj['life'] - obj['fadeout']:
				
				if obj['fadeout'] > 0.0 and obj['startalpha'] > 0.0:
					
					rate = (-float(obj['startalpha']) / float(obj['fadeout'])) * f
					alpha = obj.color[3] + rate 
			
			obj.color = [obj.color[0], obj.color[1], obj.color[2], alpha]
			
			if obj['colorchange'] == 0:
				if obj.color[1] > 0.5:
					
					c = obj.color
					c[1] -= 0.025 * f
					obj.color = c
				
				else:
					obj['colorchange'] = 1
			else:
				r = 0.025
				c = obj.color
				c[1] -= r * f
				c[2] -= r * f
				obj.color = c
	   
		##### PARTICLE DEATH #####

	
		if obj['fadeout'] == 1 and obj.color[3] <= 0.0:
			die = 1
			
		elif obj['time'] >= obj['life']:   # If the particle is invisible or it has been alive for longer than it's life variable,
			die = 1
			   
		elif not cam.pointInsideFrustum(obj.position) and obj['partcull']:
			die = 1
			   
		if die:
		
			if obj['cache'] and not obj['emitter'].invalid:			# If the emitter still exists and caching is off
			
				del obj['init']										# Reinitialize the object
				obj['speed'] = obj['origspd'][:]					# And reset it, because the BGE will use the same particle again
				
				obj.worldPosition = obj['emitter'].worldPosition.copy() + obj['origoff']
				
				obj.scaling = obj['origscale'].copy()
				obj.color = obj['origcolor'][:]
				Init(obj)
				
				if obj['emitter']['partcache']:
					obj['emitter']['cachedone'] = 1

			else:
				particlelist.remove(obj)
				obj.endObject()                                     			# End the object

				if obj['emitter'] != None and not obj['emitter'].invalid:        # Tell the emitter that spawned you that you're gone
					obj['emitter']['emitterpartamt'] -= 1
					obj['emitter']['particles'].remove(obj)

def Template(particlelist):

	sce = logic.getCurrentScene()
	cont = logic.getCurrentController()
	
	always = cont.sensors[0]
	freq = always.frequency + 1
		
	cam = sce.active_camera

	particles = particlelist[:] # Make a copy of the array
	
	for x in range(len(particles)):
		
		obj = particles[x]
		
		if not 'init' in obj:	# Initialize values
			obj['init'] = 1
			obj['life'] = 0
			#obj['spd'] = 0.02
		
		obj['life'] += freq		# Add the frequency of the calculator to the life value
		
		obj.worldPosition.z += (obj['speed'][2] + 0.0075) * freq	# Move upwards
		
		s = obj.scaling[0] - (0.005 * freq)
		obj.scaling = [s, s, s]
		
		c = obj.color
		if obj['life'] > 40:
			c[3] -= 0.05 * freq
		obj.color = [c[0], c[1] - (0.05 * freq), c[2], c[3]]
		
		die = 0
		
		if c[3] <= 0.0:
			die = 1
		elif obj['life'] > 60:
			die = 1
			
		if die:
		
			particlelist.remove(obj)
			obj.endObject()                                     			# End the object

			if obj['emitter'] != None and not obj['emitter'].invalid:        # Tell the emitter that spawned you that you're gone
				obj['emitter']['emitterpartamt'] -= 1
				obj['emitter']['particles'].remove(obj)