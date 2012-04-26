
import bgui
import ui


class HUD(ui.Screen):
	""" Heads up display """

	def __init__(self, parent, name):
		super().__init__(parent, name, blocking=False)

		self.interact_label = bgui.Label(self, 'interact_label', '', pos=[0.5, 0.8], sub_theme='interact', options=bgui.BGUI_DEFAULT|bgui.BGUI_CENTERX)

	def set_interact_text(self, text, icon=None):
		""" Set the interact text and icon """
		if text == '':
			self.interact_label.visible = False
		else:
			self.interact_label.visible = True
			self.interact_label.text = text
