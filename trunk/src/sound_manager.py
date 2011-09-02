import os

import aud
import bge

from paths import PATH_SOUNDS, PATH_MUSIC

class SoundManager:

	def __init__(self):
		self.sounds = []
		self.handles = []

	def play_sound(self, sound_name, type='play', wait=False):

		info = {'Sound':sound_name,'Type':type}

		if wait == True:
			print ('Tre')
			print (self.sounds)
			print (self.handles)

			if info in self.sounds:
				print('He!')
			else:
				self.sounds.append(info)
		else:
			self.sounds.append(info)


	def stop_sound(self, sound_handle):
		sound_handle.stop()

	def stop_all_sounds(self):
		for handle in self.playing_sounds_effect_handles:
			self.playing_sound_effect_handles.remove(handle)
			handle.stop()

	def main(self):
		device = aud.device()

		for sound in self.sounds:
			if sound['Type'] == 'play':
				handle = aud.Factory(PATH_SOUNDS+sound['Sound'])
				h = device.play(handle)
				sound['Handle'] = h
				self.handles.append(h)
				self.sounds.remove(sound)

			for handle in self.handles:
				#if sound['Handle'] != None:
				if handle.status == False:
					self.sounds.remove(handle)