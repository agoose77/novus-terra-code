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
		
		self.factories = {}
		
		for sound in os.listdir(PATH_SOUNDS):
			if sound.endswith('.wav') or sound.endswith('.ogg'):
				self.factories[sound] = aud.Factory.file(PATH_SOUNDS+sound).buffer()

	def play_sound(self, sound_name, object, type='play', multi=False, use_3d=True, use_LP=True, occlude_LP=True, alert=True):
		info = {'Name':sound_name, 'Own':object, 'Type':type, 'Multi':multi, "3d":use_3d, "LP":use_LP, "occlude":occlude_LP, "alert":alert}
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
		device.listener_orientation = bge.logic.getCurrentScene().active_camera.orientation.to_quaternion()


		for sound in self.sounds:
			s = self.factories[sound['Name']] # Get factory
			dist = sound['Own'].getDistanceTo(bge.logic.getCurrentScene().active_camera.position)

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
				h.location = sound['Own'].position
				h.distance_maximum = 100.0
				h.distance_reference = 5.0


			# Alert Entities
			if sound['alert'] == True:					
				entities = sudo.entity_manager.get_within(sound['Own'].position, 100)

				for ent in entities:
					ent.alert_entity(sound['Own'])


			###
			self.handles.append([h, sound, sound['Own'].position])
			self.sounds.remove(sound)


		for handle in self.handles:
			status = handle[0].status
			h = handle[0]
			#h.location = handle[2]
			

			#if status == False:
				#self.sounds.remove(handle[1])
				#self.handles.remove(handle)