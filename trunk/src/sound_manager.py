import os
import random

import aud
import bge
import game

from paths import PATH_SOUNDS, PATH_MUSIC
import sudo

class SoundManager:
	def __init__(self):
		self.sounds = []
		self.handles = []

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
			# Return if no music has been loaded
			return

		if song_name == "Random":
			while True:
				random_number = random.randrange(0,len(self.music))
				song = self.music[random_number]

				if len(self.music) > 1:
					if not song == self.last_song:
						break;
				else:
					break;
		else:
			song = self.music[song_name]
		
		self.last_song = self.current_song

		s = song#aud.Factory(song)
		h = self.device.play(s)
		h.volume = volume

		self.current_song = {"sound":song,"handle":h}
		print ("--- Song Played: " + song_name + " ---")
	
	def stop_music(self):
		pass


	### SOUNDS
	def play_sound_frame(self, frames, layer, armature, sound_name, object=None, type='play', use_3d=True, use_LP=True, occlude_LP=True, alert=True, volume=1.0):
		""" Play a sound based on a animation frame """
		for frame in frames:
			if not sound_name in self.animation_sounds:
				self.animation_sounds[sound_name] = 0

			if armature.getActionFrame(layer) > frame and armature.getActionFrame(layer) < frame+1.0:
				if self.animation_sounds[sound_name] == frames.index(frame):
					self.animation_sounds[sound_name] += 1
					sudo.sound_manager.play_sound(sound_name, object, type, use_3d, use_LP, occlude_LP, alert, volume)

				if len(frames) <= self.animation_sounds[sound_name]:
					self.animation_sounds[sound_name] = 0

	def play_sound(self, sound_name, object=None, type='play', use_3d=True, use_LP=True, occlude_LP=True, alert=True, volume=1.0):
		info = {'Name':sound_name, 'Own':object, 'Type':type, "3d":use_3d, "LP":use_LP, "occlude":occlude_LP, "alert":alert,"volume":volume}
		self.sounds.append(info)
		print ('--- Sound Played ---')

	def play_random_sound(self, sounds, object=None, type='play',use_3d=True, use_LP=True, occlude_LP=True, alert=True, volume=1.0):
		random_n = random(0, len(sounds))

		sound_name = sounds[random_n]
		info = {'Name':sound_name, 'Own':object, 'Type':type, "3d":use_3d, "LP":use_LP, "occlude":occlude_LP, "alert":alert,"volume":volume}
		
		self.sounds.append(info)
		print ('--- Random Sound Played ---')

	def stop_all_sounds(self):
		for handle in self.playing_sounds_effect_handles:
			self.playing_sound_effect_handles.remove(handle)
			handle.stop()

	def handle_sounds(self):
		device = self.device

		for sound in self.sounds:
			s = self.factories[sound['Name']] # Get factory

			if sound['Own'] != None:
				dist = sound['Own'].getDistanceTo(bge.logic.getCurrentScene().active_camera.position)
			else:
				dist = 0.0

			# LP Filter
			if sound['LP'] == True:					
				e = 10000-(dist*dist) # Low Pass Filter

				### Lowpass for sounds blocked by object
				if sound['occlude'] == True:
					#ray = sound['Own'].rayCast(sound['Own'].position, bge.logic.getCurrentScene().active_camera.position, 0, '',0,0,0) 
					pass

				f = s.lowpass(e, 0.5)
				h = device.play(f)
			
			# No LP
			else:
				h = device.play(s)

			###
			if sound['3d'] == True:
				if sound['Own'] != None:
					h.location = sound['Own'].position
				h.distance_maximum = 100.0
				h.distance_reference = 5.0


			# Alert Entities
			if sound['alert'] == True:
				if sound['Own']:						
					entities = sudo.entity_manager.get_within(sound['Own'].position, 10)

					#for ent in entities:
						#ent.alert_entity(sound['Own'])


			###
			pos = None

			if sound["Own"] != None:
				pos = sound['Own'].position

			h.volume = sound['volume']
			self.handles.append([h, sound])
			self.sounds.remove(sound)

		for handle in self.handles:
			status = handle[0].status
			h = handle[0]


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

		device.listener_location = bge.logic.getCurrentScene().active_camera.position
		device.listener_orientation = bge.logic.getCurrentScene().active_camera.orientation.to_quaternion()

		self.handle_sounds()
		self.handle_music()

		