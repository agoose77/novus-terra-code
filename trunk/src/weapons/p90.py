import weapons


class P90(weapons.Gun):
	def __init__(self, grid_id):
		weapons.Gun.__init__(self, grid_id, 'P90', 'P90', 'weapon_sound_m.ogg',
			damage=5.0,
			rate_of_fire=10.0,
			clip_size=20,
			reload_time=1.0,
			burst=10,
			ammo_id='cube')

	def play_anim(self, anim):
		pass
