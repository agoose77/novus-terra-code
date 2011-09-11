import os

import aud
import bge

from paths import PATH_SOUNDS, PATH_MUSIC

class SoundManager:

	def __init__(self):
		self.sounds = []
		self.handles = []

	def play_sound(self, sound_name, object, type='play', multi=False):
		info = {'Name':sound_name, 'Own':object, 'Type':type, 'Multi':multi}

		if not info in self.sounds:
			self.sounds.append(info)
		else:
			print ('TESTHIFINF')

	def stop_all_sounds(self):
		for handle in self.playing_sounds_effect_handles:
			self.playing_sound_effect_handles.remove(handle)
			handle.stop()

	def main(self):
		device = aud.device()

		for sound in self.sounds:
			if sound['Multi'] == False:
				if not sound['Name'] in self.handles:
					if sound['Type'] == 'play':
						handle = aud.Factory(PATH_SOUNDS+sound['Name'])
						h = device.play(handle)
						self.handles.append([h, sound])

		for handle in self.handles:
			status = handle[0].status
			print (status)

			if status == False:
				#self.sounds.remove(handle[1])
				#self.handles.remove(handle)
				print ('DO')