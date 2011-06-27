import aud

class SoundManager:

	def __init__(self):
		self.sounds = []

	def play_sound(sound_name, position, type):
		'''
		types:
		'''

		d = aud.device()
		s = aud.Factory(sound_name)
		h = d.play(f)

		return h

	def stop_sound(sound_handle):
		sound_handle.stop()

	def stop_all_sounds():
		for s in self.playing_sounds:
			s.stop()