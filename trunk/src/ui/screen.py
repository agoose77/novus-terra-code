import bgui
import game


class Screen(bgui.Widget):
	""" Generic class for display UI screens, extend this for menus, dialogues, ect """

	def __init__(self, parent, name, blocking=False, fade=False):
		super().__init__(parent, name, size=[1, 1], pos=[0, 0], options=bgui.BGUI_DEFAULT)

		self.blocking = blocking

	def show(self, args=[]):
		""" Called when the screen is summoned, extend this

		fade : fade the screen in
		args : a list of arguments for the extending class"""
		self.visible = True

		if self.blocking:
			game.Game.singleton.world.suspend()

	def hide(self):
		""" Called when the screen is banished, extend this """
		self.visible = False

		if self.blocking:
			game.Game.singleton.world.resume()

	def main(self):
		""" Called every frame while the screen is active, override this """
		pass
