import os

import aud
import bge

from paths import PATH_SOUNDS, PATH_MUSIC

class SoundManager:

	def __init__(self):
		self.sounds = {}
		self.playing_sound_effect_handles = []
		self.playing_mucis_handle = None
	
	def load_sounds(self):
		# load all sound files into memory
		
		for sound in os.listdir(PATH_SOUNDS):
			self.sounds[sound] = aud.Factory.file(PATH_SOUNDS+sound).buffer()
	
	def play_sound(self, sound_name, position, type):
		'''
		types:
		'''
		
		if sound_name in self.sounds.keys():
			# sound is already loaded into memory
			factory = self.sounds[sound_name]
			handle = aud.device().play(factory)
			self.playing_sound_effect_handles.append(handle)
		else:
			# sound is not loaded into memory, likely music
			factory = aud.Factory.file(PATH_MUSIC+sound_name)
			handle = aud.device.play().play(factory)
			self.playing_music_handle = handle
		
		handle.location = position

	def stop_sound(self, sound_handle):
		sound_handle.stop()

	def stop_all_sounds(self):
		for handle in self.playing_sounds_effect_handles:
			self.playing_sound_effect_handles.remove(handle)
			handle.stop()