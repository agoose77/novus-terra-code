"""
Sound:  Container object
"""
import bge
import game
import sudo

class Sound:
	def __init__(self):
		self.volume = 1.0
		self.name = None
		self.play_type = "play"
		self.use_3d = False
		self.lowpass = False
		self.obstruct_lowpass = False
		self.alert_entities = False
		self.object = None
		self.factory = None

		# Play sound on frame
		self.play_on_frame = False
		self.armature = None
		self.layer = None
		self.frames = []

		#
		self.handle = None

	def get_handle_status(self):
		return self.handle.status