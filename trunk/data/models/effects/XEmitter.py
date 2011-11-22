### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
###
### X-Emitter V1.8.1
###		   
### Author: SolarLune (Josiah Lane)
### Date Updated: 8/26/11
###
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



### The 3D Emitter - This originally was just a 3D emitter script that just emitted a 
### smoke particle, which is in the hidden (last) layer. However, I got sidetracked by 
### variables and expanded it to be a much more beneficial emittor,
### with values for rate, speed, friction, randomness, and size.

### HOW TO USE: Simply set the variable desired in the object. It's pretty simple - 
### for list values (like speeds, which use three components, or colors, which use four),
### use a string-type object variable and type in the components you want, like
###
### partspeed : [1.0, 1.0, 1.0] 
###
### See the example emitters to see how it works. The fires use a seperate particle
### function which is contained in the 'Particle.py' script file (named Fire),
### but the other particle effects actually share the same 'Generic' particle function.


### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~Customizable variables~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


### partsize (string, tuple) = affects the starting size of the particles
### partsizerandom (string, tuple) = adds to the particle size a random value between 0 and partsizerandom
### partsizeuniform (bool) = makes the random value added uniform or not; default = 1

### partgrow = affects what the rate of growth (percentage of scaling per frame) the particles undergo
### partgrowrandom = adds to the particle growth a random value between 0 and partgrowrandom

### partspeed = speed that the particles move in Blender units per frame; is scaled by particles' Always sensor frequency; 
### a 3-value list, like this: [0.0, 1.0, 2.0].  
### partspeedrandom = adds to the particle speed a random value (a 3-value list, like this: [0.0, 1.0, 2.0]
### partmovelocal = whether or not to move the particles on the local axis of the emitter

### partforce (string, tuple) = speed that the particles move in Blender units per frame. It basically is another method of 
### motion, and can be set to compound over time, like gravity.
### partforcecompound (bool) = compounds the effect of the force provided by partforce.
### partforcelocal (bool) = whether or not the force applied is applied to the global, or object's local axis (gravity, for example, would generally be -Z, global)

### partnum = affects how many particles are spawned per frame; use in conjunction with
### the emitter's frequency value to control how many particles appear at a time

### partmax = maximum number of particles that can exist for a given emitter;
### note that if the number of particles equals or exceeds partmax, then new particles won't be spawned

### partfriction = speed that the particles slow down

### partcolor = original color of the particles; a 4-value list - corresponds to (Red, Green, Blue, Alpha)
### partcolorrandom = random color added to the particles
### partcolorchoose (string, list) = a list of colors, from which the emitter will randomly choose one to assign to created particles;
### as with all choices, making more of the same entry increases the chances that that particular entry will be chosen. 

### partlife = the life of the particles; in the Smoke particle example, the smoke uses this to expand and fade out
### Default = 60 (one second @ 60 FPS (BGE default) )
### partliferandom = adds to the particle life a random value between 0 and partliferandom
### Default = 0

### partfadeout (int) = Indicates how long before death the particle fades out for. Defaults to 60.
### partfadein (int) = Indicates how long after birth the particle fades out for. Defaults to 0.

### partobj = the object to spawn; if a string value, then the Add actuator will use that object; 
### if None, then it will just add the object specified in the actuator
### Default = None (uses the Add Actuator's object)

### partobjchoose (string, tuple of object names) = a list of string names of objects - Emitter will randomly choose one to spawn from the list

### emitteron = used to turn the emittor on or off
### Defaut = On

### emittertype = used to change particle emission modes; default = 0
### 0 = Center mode - create particles from the object center of the emitter
### 1 = Box mode - create particles randomly within the volume of the box formed by the mesh)
### 2 = Vertex-random mode - create particles from randomly chosen vertex positions on the mesh
### 3 = Vertex-order mode, ascending - create particles from vertex positions on the mesh, going from 0 upwards
### 4 = Vertex-order mode, descending - same as 3, but opposite direction

### partcollide (int) = type of collision for particles - only works with speed, not force; default = 0
### 0 = No collision
### 1 = Stop - on collision, stop the particle's movement
### 2 = Die - on collision, kill the particle
### 3 = Full Reflect - on collision, reflect the particle's movement, and make that reflection angle the particle's new trajectory
### 4 = Angled Reflect - on collision, reflect the particle's movement -just for this frame- (resumes original trajectory next time)

### partcollidevar (string) = what property the other object must have for particles to collide with it; default = ''
### If set to a blank string, then the particle can collide with anything

### emittertimer (int) = Number in frames between particle emissions. Default = 0 (off)

### emitterlifeskip (int) = If particles' time values (incremented by every game frame a particle is alive) exceeds this value,
### it will be calculated every OTHER frame; good for prioritizing particles' processing. Default = 0 (off)

### emittercull (bool) = Whether or not to perform camera culling for the emitter and particles; when on, if the emitter is offscreen,
### it won't emit particles. Also, if the particles are off-screen, then they destroy themselves. Good for CPU-saving. Default = On

### partposrandom (string, list) = The emitter will move the particle a random amount according to this variable; note that unlike most
### cases, the emitter will move the particle by a random amount equal to a maximum of half amount in either axis for each axis. For example,
###
### partposrandom = [1.0, 0.0, 0.0] will make the emitter randomize the newly spawned
### particle's position by a maximum and minimum of 0.5 and -0.5 on the X-axis.

### emitterkill (int) = a variable that deals with killing the emitter. A bug was that if the emitter died, then the particles would be orphaned,
### and wouldn't be calculated anymore. This variable allows you to select how and when to kill the emitter.

### 0 = Don't kill the emitter (default)
### 1 = Kill the emitter when particles are all dead (and don't create any new particles in the meantime)
### 2 = Kill the emitter and all particles as well

### emitterlife (int) = a variable that deals with the emitter's life. Another weakness of my system was that destroying an object that
### had an emitter parented to it would kill the emitter as well, leaving orphaned particles. This allows emitters to stop emitting
### particles and destroy themselves when necessary. Defaults to 0 (off)

### I know this odd, but set the emitterlife variable > 0 to make the emitter wait for the particles to die, and then destroy itself;
### Set the emitterlife variable < 0 to wait the same amount of time (even if it's negative), but have the emitter die immediately.

### emittime (int) = an internal variable. Should not be altered by default, but if you're using the timer and need the emitter to emit
### at certain times, like at the start of the scene, then use this, set to a high number.

### emittercache (bool) = a variable that tells particles to not delete themselves, but to simply respawn themselves at their origin
### points and continue from there on death. Enabled by default.

###~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

### Finally, if you find that it's running slowly on your computer, there are a few
### ways to speed it up:

### 1) Slow down the frequency of the Always sensor for the Emitter object.

### The Emitter object really doesn't need to run that much, and while it's not
### too complex, running every frame can hurt the framerate.

### 2 ) Slow down the frequency of the Always sensor for calculating the particles.

### The particle object doesn't need to (and probably shouldn't) execute its code every frame;
### The particle functions included have auto-scaling code that will speed up the 
### movement, growth, etc. if the frequency of the Always sensor slows down,
### and will slow down those calculations if the frequency speeds up. This means
### that the particles should move and act the same if the script is executed
### every frame or every 5th frame (generally; if you set the frequency of the 
### particle object very high, then the particle object will appear choppy and 
### may stay in existence longer than its life variable states it should).

### 3) Use larger and less particles than more particles that are smaller. Less particles = less to draw and perform logic for.

### 4) Group particles together (i.e. have several raindrops in a single 'raindrop particle' object).

### 5) Use the emitterlifeskip property to prioritize processing for newer particles.

### P.S. If you start up the XEmitter blend file and find that most particles don't work, make sure their
### emitteron variable is set on. I turned most of them off so as not to have too many going at once when
### you start the blend file.

from bge import logic
import math
import random

import XParticle

def Evaluate(value):			# Check to see if an object property needs to be evaluated
	if isinstance(value, str):
		return eval(value)
	else:
		return value

def Convert():

	cont = logic.getCurrentController()

	obj = cont.owner

	obj['partsize'] = Evaluate(obj['partsize'])			 # Evaluate all properties that may be strings still
	obj['partsizerandom'] = Evaluate(obj['partsizerandom'])
	obj['partspeedrandom'] = Evaluate(obj['partspeedrandom'])
	obj['partspeed'] = Evaluate(obj['partspeed'])
	obj['partfriction'] = Evaluate(obj['partfriction'])
	obj['partcolor'] = Evaluate(obj['partcolor'])
	obj['partcolorrandom'] = Evaluate(obj['partcolorrandom'])
	obj['partcolorchoose'] = Evaluate(obj['partcolorchoose'])
	obj['partobjchoose'] = Evaluate(obj['partobjchoose'])
	obj['partforce'] = Evaluate(obj['partforce'])
	obj['partposrandom'] = Evaluate(obj['partposrandom'])

def GetVertices(mesh, shared = 1):
	
	verts = []
	
	for v in range(mesh.getVertexArrayLength(0)):

		vert = mesh.getVertex(0, v)
		xyz = vert.getXYZ()
		
		if shared:		# If the function should eliminate vertices that are already present, as in certain cases, BGE meshes return more vertices than are actually there
			if not xyz in verts:
				verts.append(xyz)
		else:
			verts.append(xyz)
	
	return verts
	
def BoxVertices(mesh):

	verts = GetVertices(mesh, 1)	# New method of getting the vertices using the function above
	
	verts.sort()

	verts = [verts[0], verts[len(verts) - 1]]

	return verts

### PARTICLE CALCULATOR ###

import profile

def Calculator(cont):

	"""
	This function runs the script for each particle in each system (script name).
	This function needs to run before any particles are spawned. Be aware that if this runs afterward,
	particle prototyping may not work (the particle is spawned and then wiped from the particle list, and so
	never updates.
	
	It shouldn't be a problem otherwise.
	"""

	sce = logic.getCurrentScene()
	obj = cont.owner
	freq = cont.sensors[0].frequency + 1
	cam = sce.active_camera
	
	if not hasattr(logic, 'partsys'):
	
		logic.partinit = 1
		logic.partsys = dict({})
		logic.prevsce = None
	
	if not 'partsysflush' in obj:

		obj['partsysflush'] = 1
		logic.partsys = {}	# Flush the system before use in the game scene
	
	for system in logic.partsys:
	
		parts = logic.partsys[system]
		
		try:
			f = eval(system)
			f(parts)	
			
		except NameError:				# Module doesn't exist (i.e. MyPart.Fire)

			first = system.find('.')
			module = system[:first]		# Import the necessary module (= import MyPart)
			exec('import ' + module)
			
			f = eval(system)			# = MyPart.Fire(particle system at logic.partsys['MyPart.Fire'])
			
			f(parts)	
		
### EMITTER ###
	
def Emitter():

	sce = logic.getCurrentScene()
	cont = logic.getCurrentController()
	obj = cont.owner
	freq = cont.sensors[0].frequency + 1
	cam = sce.active_camera
		
	def Init():
	
		if not 'emitterinit' in obj:
	
			mesh = obj.meshes[0] # First mesh for the box
			
			if not 'partnum' in obj:
				obj['partnum'] = 1				  # Number of particles to spawn per frame
			
			if not 'partsize' in obj:
				obj['partsize'] = '[1.0, 1.0, 1.0]' # Size of the particles at creation  
			if not 'partsizerandom' in obj:		 # Randomness of size of particles (percentage - always additive)
				obj['partsizerandom'] = '[0.0, 0.0, 0.0]'
			
			if not 'partsizeuniform' in obj:		# If randomness of size of particles should be uniform (all axes are scaled the same)
				obj['partsizeuniform'] = 1 
			
			if not 'partfadeout' in obj:			# If the particle should fade out as it dies
				obj['partfadeout'] = 40.0		   # number = how many frames to fade out before death
			if not 'partfadein' in obj:
				obj['partfadein'] = 0.0			 # number = how many frames to fade in with
			
			if not 'partgrow' in obj:
				obj['partgrow'] = 0.0			  # Rate of growth (in percentage per frame) for the  particles
			
			if not 'partgrowrandom' in obj:		 # Randomness of rate of growth (percentage - always additive, meaning that the particle's growth will always be
				obj['partgrowrandom'] = 0.0		 # partgrow + a random value between 0 and partgrowrandom.
			
			if not 'partspeed' in obj:
				obj['partspeed'] = '[0.0, 0.0, 0.0]'
			if not 'partspeedrandom' in obj:		# Randomness of the particle's speed (percentage - always additive)
				obj['partspeedrandom'] = '[0.0, 0.0, 0.0]'
			
			if not 'partforce' in obj:
				obj['partforce'] = '[0.0, 0.0, 0.0]'
				
			if not 'partforcecompound' in obj:
				obj['partforcecompound'] = 0	  # Whether the force applied compounds over time
			
			if not 'partforcelocal' in obj:
				obj['partforcelocal'] = 0			# Whether the force is local or not	
			
			if not 'partmovelocal' in obj:		  # Whether the speed of the particles is local (i.e. they move according to local object position and rotation or not)
				obj['partmovelocal'] = 0
		   
			if not 'partfriction' in obj:		   # Friction of the particle (percentage; 0 = no friction)
				obj['partfriction'] = '[0.0, 0.0, 0.0]'

			if not 'partcolor' in obj:
				obj['partcolor'] = '[1.0, 1.0, 1.0, 1.0]' # Beginning color of each particle
			if not 'partcolorrandom' in obj:
				obj['partcolorrandom'] = '[0.0, 0.0, 0.0, 0.0]'   # Randomness of particle colors (percentage - always additive) - Note that while values can't go above 1,				
			if not 'partcolorchoose' in obj:					  # if you set them to be above that, it will lessen the chances that the number will be within the 0 - 1 range (you'll get more 1.0 values)	
				obj['partcolorchoose'] = '[]'	   # Option to choose from the specified set of colors (note that if you use this, part color won't be used							 
			
			if not 'partlife' in obj:
				obj['partlife'] = 60				# Life of the particle in frames
			if not 'partliferandom' in obj:		 # Randomness (in frames) of the particle's life (percentage - always additive)
				obj['partliferandom'] = 0
				
			if not 'partmax' in obj:				# Maximum number of particles alive at any given time
				obj['partmax'] = 100000
				
			if not 'partobj' in obj:
				obj['partobj'] = None			   # Particle to spawn
			if not 'partobjchoose' in obj:		  # List of particles to randomly decide to spawn
				obj['partobjchoose'] = '[]'
				
			if not 'partparent' in obj:			 # Whether the particles spawned should be parented to the emitter (a bit unstable)
				obj['partparent'] = 0
			
			if not 'emittercull' in obj:
				obj['emittercull'] = 0			 # Kill particles when they're offscreen

			if not 'partposrandom' in obj:
				obj['partposrandom'] = '[0.0, 0.0, 0.0]'	# Random position for the particles (additive)
					
			obj['particles'] = []
			
			if not 'emittertype' in obj:
				obj['emittertype'] = 0			   # What emission mode is enabled; 0 = center, 1 = box, 2 = vertex, 3 = vertex-ordered
			if not 'emittertimer' in obj:
				obj['emittertimer'] = 0.0		   # Timer that is customizable - this is how often the emitter should make toast. No, seriously. It's in frames.
			if not 'emitteron' in obj:
				obj['emitteron'] = 1				# If the object is emitting or not; you can use this to turn the emitter on or off.
			
			if not 'emitterlife' in obj:
				obj['emitterlife'] = 0.0			# Number of frames the emitter lives before it dies
			
			if not 'emitterseed' in obj:
				obj['emitterseed'] = None			# Seed value for randomness in particle emission
			
			obj['emitterseedprev'] = obj['emitterseed']
			
			random.seed(obj['emitterseed'])			# Set the seed for this random particle emission
			
			obj['emitterrand'] = random.getstate()	# Gets the state for this particular emitter
			
			if not 'partcollide' in obj:
				obj['partcollide'] = 0
			if not 'partcollidevar' in obj:
				obj['partcollidevar'] = ''
			
			if not 'partcache' in obj:
				obj['partcache'] = 0				# Caching for particles; with this on, old particles are re-used after death. Gives a speed increase. Should be used in conjunction with partmax
			
			obj['cachedone'] = 0					# Caching is done when the first particle dies; this is the maximum amount of particles allowed, basically.
			
			if not 'partlod' in obj:
				obj['partlod'] = 0
				
			if not 'partloddist' in obj:
				obj['partloddist'] = 15
				
			if not 'parttype' in obj:
				obj['parttype'] = 'XParticle.Generic'	# Defaults to the Generic type of the XParticle
			
			if not 'partprototype' in obj:
				obj['partprototype'] = 0			# Whether emitter prototyping is on
			
			obj['emitlifetimer'] = 0.0				# Internal timer
			obj['emittime'] = 0.0				   	# Internal timer that the emitter uses to count down to emit.
													# If you need the emitter to emit on creation, set this high (in the object properties)
			
			#### Don't alter the variables below ####
			
			obj['vertindex'] = 0					# Vertex index for vertex-order spawn mode (mode 3)
			
			obj['emitterrect'] = BoxVertices(mesh) 	# Find the furthest two vertices for box emission mode
			obj['emitterverts'] = GetVertices(mesh, 1)	# Get a list of all vertices in the emitter mesh
						
			obj['emitterpartamt'] = 0			  	# Total number of particles existing; *this shouldn't be set manually*
			obj['emitterinit'] = 1				  	# Object initialization done *this shouldn't be set manually*
			
			obj['firstparticle'] = None				# Record which particle is first (should be selected for prototyping)
			obj['emitterproto'] = []				# Prototype of how each particle should perform		
			obj['protodone'] = 0					# Whether the original prototype has finished its life
	
	def Update():
	
		if obj['emitterlife'] > 0:
			obj['emitlifetimer'] += 1.0 * freq
		else:
			obj['emitlifetimer'] -= 1.0 * freq
		
		if obj['emitterlife'] > 0 and obj['emitlifetimer'] >= obj['emitterlife']:
			obj.endObject()
				
		if obj['emitteron'] and not obj['cachedone']:
		
			Convert()						   	# Convert variable strings to actual code		
			
			#if obj['emitterseed'] != obj['emitterseedprev']:
			#	random.seed(obj['emitterseed'])

			#if obj['emitterseed'] != None and obj['emitterseed'] < 0:
			#	random.seed(None)
			#	obj['emitterseed'] = None
				
			#print (obj['emitterseed'], obj['emitterseedprev'])
				
			#obj['emitterseedprev'] = obj['emitterseed']
			
			#obj['emitterrand'] = random.getstate()
			
			random.setstate(obj['emitterrand'])	# Set the state for this particle emission to the original
			
			#if obj['emitterseed'] != obj['emitterseedprev']:
			#	random.seed(obj['emitterseed'])

			if obj['emitterseed'] != None and obj['emitterseed'] < 0:
				random.seed(None)
				obj['emitterseed'] = None
				
			if obj['emitterseed'] != obj['emitterseedprev']:
				random.seed(obj['emitterseed'])
			
			obj['emitterseedprev'] = obj['emitterseed']
			
			rand = random.random
		
			obj['emittime'] += 1.0 * freq
			#print ('')
			#print (obj['emitterproto'])
			if obj['emittime'] >= obj['emittertimer'] or obj['emittertimer'] <= 0.0:
				
				obj['emittime'] = 0.0
				
				if (cam.pointInsideFrustum(obj.position) and obj['emittercull']) or not obj['emittercull']:	# Don't emit if culling is on 
								
					for i in range(int(obj['partnum'])):			 # Repeat creation of particles for however many particles per frame
					
						if obj['emitterpartamt'] > obj['partmax']:	 # There could be too many particles in this loop
							break
							
						addobj = obj['partobj']
													
						if obj['partobjchoose'] != []:
							addobj = random.choice(obj['partobjchoose'])
						
						if obj['partliferandom'] > 0.0:
							life = obj['partlife'] + (rand() * obj['partliferandom'])
						else:
							life = obj['partlife']
						
						a = sce.addObject(addobj, obj)
						
						a['type'] = obj['parttype']
						
						if not hasattr(logic, 'partsys'):
							logic.partsys = dict({})
						
						try:										# Append the particle to the system under the specified particle system name ('Fire', 'Generic', etc)
							logic.partsys[a['type']].append(a)
						except KeyError:							# If the particle system doesn't exist yet, create the system and then append the particle
							logic.partsys[a['type']] = []
							logic.partsys[a['type']].append(a)
							
						if obj['firstparticle'] == None:			# Find your first particle spawned
							obj['firstparticle'] = a
							
						if obj['partprototype']:
							a['prototype'] = 1
						
						a['cache'] = obj['partcache']
						
						a['loddist'] = obj['partloddist']
						a['lod'] = obj['partlod']
						
						obj['emitterpartamt'] += 1									  # Add total number of particles emitted
						obj['particles'].append(a)
						
						#a.visible = 0		# Because the update process only happens every x frames, it's possible that the particle is created and is simply paused in the emitter for a few frames.
						
						a['emitter'] = obj
						a['partcull'] = obj['emittercull']
						a['life'] = life
						
						if obj['partparent']:
							a.setParent(obj)
			
						if obj['partgrowrandom'] > 0:
							a['growrate'] = obj['partgrow'] + (rand() * obj['partgrowrandom'])
						else:
							a['growrate'] = obj['partgrow']
						
						a['movelocal'] = obj['partmovelocal']
							
						a['fadeout'] = obj['partfadeout']
						a['fadein'] = obj['partfadein']
						
						if obj['partspeedrandom'][0] != 0 or obj['partspeedrandom'][1] != 0 or obj['partspeedrandom'][2] != 0:
							a['speed'] = [obj['partspeed'][0] + (rand() * obj['partspeedrandom'][0]), 
							obj['partspeed'][1] + (rand() * obj['partspeedrandom'][1]),
							obj['partspeed'][2] + (rand() * obj['partspeedrandom'][2]),]											 # Particle speed if wanted
						else:
							a['speed'] = obj['partspeed'][:]										  # Particle speed if wanted
			 
						a['friction'] = obj['partfriction']
						a['force'] = obj['partforce']
						a['forcecompound'] = obj['partforcecompound']
						a['forcelocal'] = obj['partforcelocal']
						
						a['collide'] = obj['partcollide']
						a['collidevar'] = obj['partcollidevar']
						
						c = obj['partcolor'][:]
						
						if obj['partcolorchoose'] != []:
							c = random.choice(obj['partcolorchoose'])
						
						if obj['partcolorrandom'][0] != 0 or obj['partcolorrandom'][1] != 0 or obj['partcolorrandom'][2] != 0 or obj['partcolorrandom'][3] != 0:
						
							c[0] += rand() * obj['partcolorrandom'][0]
							c[1] += rand() * obj['partcolorrandom'][1]
							c[2] += rand() * obj['partcolorrandom'][2]
							c[3] += rand() * obj['partcolorrandom'][3]	   
			  
						a.color = c
						
						if a['fadein']:
							x = a.color
							x[3] = 0.0
							a.color = x
							a['startalpha'] = c[3]			# Original (starting) alpha
							
						if obj['partsizerandom'][0] > 0 or obj['partsizerandom'][1] > 0 or obj['partsizerandom'][2] > 0:
							
							if obj['partsizeuniform']:
								r = rand()
								a.scaling = [
								obj['partsize'][0] + (r * obj['partsizerandom'][0]),
								obj['partsize'][1] + (r * obj['partsizerandom'][1]),
								obj['partsize'][2] + (r * obj['partsizerandom'][2])
								]
							else:
								a.scaling = [
								obj['partsize'][0] + (rand() * obj['partsizerandom'][0]),
								obj['partsize'][1] + (rand() * obj['partsizerandom'][1]),
								obj['partsize'][2] + (rand() * obj['partsizerandom'][2])
								]
						else:
							a.scaling = obj['partsize'][:] # Sets the scaling to normal (the smoke object has its own code scaling it,
			
						apos = obj.position.copy()									  # Makes a copy of the smoke box's position and edit it
								
						if obj['emittertype'] == 1:

							if obj['partparent']:
								apos.x = ( ( obj['emitterrect'][0][0] + (rand() * (obj['emitterrect'][1][0] - obj['emitterrect'][0][0]) ) ) )  # This moves the added particle object into
								apos.y = ( ( obj['emitterrect'][0][1] + (rand() * (obj['emitterrect'][1][1] - obj['emitterrect'][0][1]) ) ) )  # a random position in the box
								apos.z = ( ( obj['emitterrect'][0][2] + (rand() * (obj['emitterrect'][1][2] - obj['emitterrect'][0][2]) ) ) )  # When enough particle objects exist, they fill the box
							else:
								apos.x = (obj.worldPosition.x + ( obj['emitterrect'][0][0] + (rand() * (obj['emitterrect'][1][0] - obj['emitterrect'][0][0]) ) ) * obj.worldScale.x)	# This block does this relative to the emitter's position
								apos.y = (obj.worldPosition.y + ( obj['emitterrect'][0][1] + (rand() * (obj['emitterrect'][1][1] - obj['emitterrect'][0][1]) ) ) * obj.worldScale.y) 	# while the block above does the same code absolutely
								apos.z = (obj.worldPosition.z + ( obj['emitterrect'][0][2] + (rand() * (obj['emitterrect'][1][2] - obj['emitterrect'][0][2]) ) ) * obj.worldScale.z)	# because the particle has been parented.
							
							# Thanks to multiplying the position by the local scale of the object, you don't even have to apply the scaling to the smoke box mesh to get the smoke to fill the box up
							
						elif obj['emittertype'] == 2 or obj['emittertype'] == 3 or obj['emittertype'] == 4:		# Vertex-ordered spawn modes
						
							if obj['emittertype'] == 2:									# Random vertex spawn mode
								cpos = random.choice(obj['emitterverts'])
							elif obj['emittertype'] == 3 or obj['emittertype'] == 4:	# Vertex-ordered spawn mode
								cpos = obj['emitterverts'][obj['vertindex']]

								if obj['emittertype'] == 3:
									if obj['vertindex'] >= len(obj['emitterverts']) - 1:
										obj['vertindex'] = 0
									else:
										obj['vertindex'] += 1
								elif obj['emittertype'] == 4:
									if obj['vertindex'] <= 0:
										obj['vertindex'] = len(obj['emitterverts']) - 1
									else:
										obj['vertindex'] -= 1							
							
							if obj['partparent']:
								apos = cpos
								
							else:
								if obj['partparent']:
									apos.x = (cpos.x  * obj.worldScale.x)  # This moves the added smoke object into
									apos.y = (cpos.y  * obj.worldScale.y)  # a random position in the box
									apos.z = (cpos.z  * obj.worldScale.z)  # When enough smoke objects exist, they fill the box
								else:
									apos.x = (obj.worldPosition.x + (cpos.x  * obj.worldScale.x))  # This moves the added smoke object into
									apos.y = (obj.worldPosition.y + (cpos.y  * obj.worldScale.y))  # a random position in the box
									apos.z = (obj.worldPosition.z + (cpos.z  * obj.worldScale.z))  # When enough smoke objects exist, they fill the box

						if obj['partposrandom'][0] != 0.0 or obj['partposrandom'][1] != 0.0 or obj['partposrandom'][2] != 0.0:
						
							randpos = obj['partposrandom']

							apos.x += (rand() * randpos[0]) * 0.5
							apos.y += (rand() * randpos[1]) * 0.5
							apos.z += (rand() * randpos[2]) * 0.5
							
							apos.x -= (rand() * randpos[0]) * 0.5
							apos.y -= (rand() * randpos[1]) * 0.5
							apos.z -= (rand() * randpos[2]) * 0.5
							
						a.position = apos
								
			#else:   # Emitterpartamt >= partmax
				#print (obj['emitterpartamt'])
						
		obj['emitterrand'] = random.getstate()
		
	Init()
	Update()
				