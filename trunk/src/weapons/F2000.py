import weapons


class F2000(weapons.Gun):
	def __init__(self, grid_id):
		weapons.Gun.__init__(self, grid_id, 'F2000', 'F2000', 'weapon_sound_m.ogg',
			damage=25.0,
			rate_of_fire=10.0,
			clip_size=200,
			reload_time=1.0,
			burst=200,
			ammo_id='cube')

	def speed_up():
		print ("Upgrade")
		
	def play_anim(self, anim):
		pass