import os
import random

import aud
import bge
import game

from paths import PATH_SOUNDS, PATH_MUSIC

class SoundManager:

	def __init__(self):
		self.sounds = []
		self.handles = []
		
		self.factories = {}
		
		for sound in os.listdir(PATH_SOUNDS):
			if sound.endswith('.wav') or sound.endswith('.ogg'):
				self.factories[sound] = aud.Factory.file(PATH_SOUNDS+sound).buffer()

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

		device.listener_location = bge.logic.getCurrentScene().active_camera.position


		for sound in self.sounds:
			print(sound)
			#if sound['Multi'] == False:
				#if not sound['Name'] in self.handles:
					#if sound['Type'] == 'play':
			#handle = aud.Factory(PATH_SOUNDS+sound['Name'])

			#dist = sound['Own'].getDistanceTo(game.Game.singleton.world.KX_player)

			s = self.factories[sound['Name']]
			#s = aud.Factory(PATH_SOUNDS+sound['Name'])
			f = s.lowpass(0.5, 0.5)

			h = device.play(f)

			#h.location = sound['Own'].position
			#h.distance_maximum = 100.0
			#h.distance_reference = 5.0

			self.handles.append([h, sound, sound['Own'].position])
			self.sounds.remove(sound)

		for handle in self.handles:
			status = handle[0].status
			h = handle[0]
			#h.location = handle[2]
			

			#if status == False:
				#self.sounds.remove(handle[1])
				#self.handles.remove(handle)