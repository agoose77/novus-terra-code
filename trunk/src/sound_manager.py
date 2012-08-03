"""
SoundManager:  The sound class.
"""
import os
import random

import aud
import bge
import game
from sound import Sound

from paths import PATH_SOUNDS, PATH_MUSIC
import sudo

class SoundManager:
	def __init__(self):
		self.sounds = []

		# AUD
		self.device = aud.device()
		
		# MUSIC
		self.current_song = {"sound":None,"handle":None, "time":0.0}
		self.last_song = {"sound":None,"handle":None, "time":0.0}
		self.music = []

		# SOUNDS
		self.factories = {}
		self.animation_sounds = {}

		# SETTINGS
		self.wait = 300.0
	
		###
		for sound in os.listdir(PATH_SOUNDS):
			if sound.endswith('.wav') or sound.endswith('.ogg'):
				self.factories[sound] = aud.Factory.file(PATH_SOUNDS+sound).buffer()

		for sound in os.listdir(PATH_MUSIC):
			if sound.endswith('.wav') or sound.endswith('.ogg'):
				self.music.append([aud.Factory.file(PATH_MUSIC+sound),sound])


	### MUSIC
	def play_song(self,song_name, fade_time=5.0,volume=1.0):
		if not len(self.music):
			return # Return if no music has been loaded

		if song_name == "Random":
			while True:
				random_number = random.randrange(0,len(self.music))
				song = self.music[random_number]

				if self.music:
					if not song == self.last_song:
						break;
				else:
					break;
		else:
			song = self.music[song_name]
		
		self.last_song = self.current_song

		s = song
		h = self.device.play(s)
		h.volume = 0.0

		self.current_song = {"sound":song,"handle":h}
		print ("--- Song Playing: " + song_name + " ---")
	
	def stop_music(self):
		pass


	### SOUNDS
	def play_sound_on_frame(self, frames, layer, armature, sound_name, sound_object=None, play_type='play', use_3d=True, lowpass=True, obstructed_lowpass=True, alert_entities=True, volume=1.0):
		""" Play a sound tied to an animation frame """

		### New sound instance
		sound = Sound()

		### Choose random sound
		if isinstance(sound_name, list):
			sound.name = sound_name[random.randrange(0,len(sound_name))]
		else: sound.name = sound_name

		###
		sound.play_on_frame = True
		sound.frames = frames
		sound.layer = layer
		sound.armature = armature
		sound.object = sound_object
		sound.play_type = play_type
		sound.use_3d = use_3d
		sound.lowpass = lowpass
		sound.obstructed_lowpass = obstructed_lowpass
		sound.alert_entities = alert_entities

		### Check for duplicates
		passed = True
		for sound_obj in self.sounds:
			if sound_obj.play_on_frame:
				if (sound_obj.armature == armature) and (sound_obj.layer == layer):
					passed = False

		if passed:
			self.sounds.append(sound)

	def play_sound(self, sound_name, sound_object=None, play_type='play', use_3d=True, lowpass=True, obstructed_lowpass=True, alert_entities=True, volume=1.0):
		""" Play a sound """

		### New sound instance
		sound = Sound()

		### Choose random sound
		if isinstance(sound_name, list):
			sound.name = sound_name[random.randrange(0,len(sound_name))]
		else: sound.name = sound_name

		###
		sound.object = sound_object
		sound.play_type = play_type
		sound.use_3d = use_3d
		sound.lowpass = lowpass
		sound.obstructed_lowpass = obstructed_lowpass
		sound.alert_entities = alert_entities

		self.sounds.append(sound)

	def stop_all_sounds(self):
		for sound in self.sounds:
			if sound.handle:
				sound.handle.stop()
				self.sounds.remove(sound)


	### CHECKS
	def handle_sounds(self):
		device = self.device

		for sound in self.sounds:

			# If a sound handle hasn't been created
			if not sound.handle:

				### If the sound is tied to an animation
				if sound.play_on_frame:
					frames = sound.frames
					sound_name = sound.name
					armature = sound.armature
					layer = sound.layer
							
					for frame in frames:
						if not sound_name in self.animation_sounds:
							self.animation_sounds[sound_name] = 0

						if armature.getActionFrame(layer) > frame-1.0 and armature.getActionFrame(layer) < frame+2.0:
							if self.animation_sounds[sound_name] == frames.index(frame):
								self.animation_sounds[sound_name] += 1

							if len(frames) <= self.animation_sounds[sound_name]:
								self.sounds.remove(sound)


				###
				print (sound.name)
				sound.factory = self.factories[sound.name] # Get factory

				dist = 0.0
				if sound.object: dist = sound.object.getDistanceTo(bge.logic.getCurrentScene().active_camera.worldPosition)
					
				# LP Filter
				if sound.lowpass:					
					e = dist/70 # Max distance = Full LP
					if e > 1.0: e = 1.0 # Clamp to 1.0

					e = 10000 - (5000*e)

					### Lowpass for sounds blocked by object
					if sound.obstructed_lowpass == True:
						pass #ray = sound['object'].rayCast(sound['object'].position, bge.logic.getCurrentScene().active_camera.position, 0, '',0,0,0) 

					f = sound.factory.lowpass(e, 0.5)
					sound.handle = device.play(f)
				
				# No lowpass
				else:
					sound.handle = device.play(sound.factory)

				###
				if sound.use_3d:
					if sound.object:
						sound.handle.relative = False
						sound.handle.location = sound.object.worldPosition

					sound.handle.distance_maximum = 500.0
					sound.handle.distance_reference = 5.0

				# Alert Entities
				""" """

				###
				sound.handle.volume = sound.volume


			# Check and delete finished handles
			else:
				if sound.get_handle_status ()== False:
					sound.handle.stop()
					self.sounds.remove(sound)


	def handle_music(self):
		if not self.music:
			return
			
		device = self.device

		# New song
		if (sudo.world.world_time - self.last_song['time'] > self.wait) or (self.current_song["sound"] == None):
			self.last_song = self.current_song

			rand = random.randrange(0, len(self.music))
			rand = self.music[rand]

			s = rand[0]
			h = device.play(s)

			self.current_song['sound'] = rand[1]
			self.current_song['handle'] = h
			self.current_song['time'] = sudo.world.world_time		


	def main(self):
		device = self.device

		device.distance_model = aud.AUD_DISTANCE_MODEL_INVERSE_CLAMPED#AUD_DISTANCE_MODEL_LINEAR#AUD_DISTANCE_MODEL_EXPONENT_CLAMPED
	
		device.listener_location = bge.logic.getCurrentScene().active_camera.worldPosition.copy()
		device.listener_orientation = bge.logic.getCurrentScene().active_camera.worldOrientation.copy().to_quaternion()

		self.handle_sounds()
		#self.handle_music()

		