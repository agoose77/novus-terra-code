import time

import bgui
import game
import ui

class Loading(ui.Screen):
	def __init__(self, parent):
		super().__init__(parent, 'screen_loading')

		self.frame = bgui.Frame(self, 'frame', size=[1,1], pos=[0,0])
		self.frame.colors = [[0,0,0,0]] * 4

		self.label = bgui.Label(self, 'label', text="Loading...", color=[1,1,0,0], sub_theme='Large',
			options=bgui.BGUI_DEFAULT | bgui.BGUI_CENTERED)

		self.output = bgui.Label(self, 'output', text='', pos=[0,0.5])

		self.fade_out = False

	def show(self, args=[]):
		self.parent.hide('pause')
		super().show()

	def hide(self):
		# don't hide striaght away - fade out first
		self.fade_out = True

	def main(self):
		if self.fade_out:
			# Fade the menu
			alpha = self.frame.colors[1][3]

			if alpha > 0.0:
				alpha = max(0, alpha - 3.0 * max(0.01, game.Game.singleton.delta_time))
				self.frame.colors = [[0,0,0,alpha]] * 4
				self.label.color = [1,1,0,alpha]
			else:
				self.fade_out = False
				super().hide()

		else:
			# fade in
			alpha = self.frame.colors[1][3]

			if alpha < 1.0:
				alpha = min(1.0, alpha + 3.0 * game.Game.singleton.delta_time)
				self.frame.colors = [[0,0,0,alpha]] * 4
				self.label.color = [1,1,0,alpha]
			else:
				self.parent.hide('pause')