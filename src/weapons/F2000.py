import weapons

class F2000(weapons.Gun):
	def __init__(self, grid_id):
		weapons.Gun.__init__(self, grid_id, 'F2000', 'F2000', 'weapon_sound_m.ogg',
			damage=25.0,
			rate_of_fire=10.0,
			zoom_lens=25.0,
			clip_size=200,
			reload_time=2.0,
			burst=200,
			ammo_id='cube',

			animations={
				"walk":20,
				"idle":101,
				"run":17,
				"reload":64})

	def speed_up():
		print ("Upgrade")
		
	def play_anim(self, anim):
		pass