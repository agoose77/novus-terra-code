import os
import random

import aud
import bge

from paths import PATH_SOUNDS, PATH_MUSIC

class SoundManager:

	def __init__(self):
		self.sounds = []
		self.handles = []

	def play_sound(self, sound_name, object, type='play', multi=False):
		info = {'Name':sound_name, 'Own':object, 'Type':type, 'Multi':multi}
		self.sounds.append(info)
		print ('--- Sound Played ---')

	def play_random_sound(self, sounds, object, type='play', multi=False):
		random_n = random(0, len(sounds))

		sound_name = sounds[random_n]
		info = {'Name':sound_name, 'Own':object, 'Type':type, 'Multi':multi}
		self.sounds.append(info)
		print ('--- Random Sound Played ---')

	def stop_all_sounds(self):
		for handle in self.playing_sounds_effect_handles:
			self.playing_sound_effect_handles.remove(handle)
			handle.stop()

	def main(self):
		device = aud.device()

		for sound in self.sounds:
			print(sound)
			#if sound['Multi'] == False:
				#if not sound['Name'] in self.handles:
					#if sound['Type'] == 'play':
			handle = aud.Factory(PATH_SOUNDS+sound['Name'])
			h = device.play(handle)
			self.handles.append([h, sound])
			self.sounds.remove(sound)
			print("YOYOYOYOYOYYO*999999999999999999")

		for handle in self.handles:
			status = handle[0].status

			#if status == False:
				#self.sounds.remove(handle[1])
				#self.handles.remove(handle)