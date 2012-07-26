import bge

import bgui
import game
import tweener
import ui


class ItemSwap(ui.Screen):
        """ A screen that displays two inventories side by side, allowing the player to swap items """

        def __init__(self, parent, name):
                super().__init__(parent, name, blocking=True)

                ww = parent.size[0]
                wh = parent.size[1]

                # a frame to darken the game screen
                self.backdrop = bgui.Frame(self, 'backdrop', size=[1, 1], pos=[0, 0])
                self.backdrop.colors = [(0, 0, 0, 0.55)] * 4

                self.player_inventory = ui.InventoryWindow(self, 'player_inventory',
                        game.Game.singleton.world.player.inventory, pos=[ww // 2 - 310, 0], options=bgui.BGUI_CENTERY)

                self.other_inventory = ui.InventoryWindow(self, 'other_inventory', None, pos=[ww // 2 + 10, 0],
                        options=bgui.BGUI_CENTERY)

                self.player_label = bgui.Label(self, 'player_label', 'Player', pt_size=48,
                        color=[1, 1, 1, 1], font='./data/fonts/olney_light.otf', pos=[ww // 2 - 310,
                        wh // 2 + 220 + 10], options=bgui.BGUI_NONE)
                self.other_label = bgui.Label(self, 'other_label', '', pt_size=48,
                        color=[1, 1, 1, 1], font='./data/fonts/olney_light.otf',
                        pos=[ww // 2 + 10, wh // 2 + 220 + 10], options=bgui.BGUI_NONE)

                self.return_but = ui.Fut_Button(self, 'return', pos=[ww // 2 + 320 - 182, wh // 2 - 210 - 45 - 10],
                        size=[182, 45], text="BACK", options=bgui.BGUI_NONE)
                self.return_but.on_click = self.return_
                self.tweener = tweener.TweenManager()
                self.hook = 0.0  # for tweener

        def return_(self, widget):
                game.Game.singleton.ui_manager.hide('item_swap')

        def set_inventory(self, inventory):
                self.other_inventory.inventory = inventory
                self.other_label.text = inventory.name

                self.player_inventory.link(self.other_inventory)

                self.player_inventory.redraw()
                self.other_inventory.redraw()

        def show(self, args=[]):
                """ Display the inventory swap screen
                arg[0] = inventory to display alongside player's
                """

                self.set_inventory(args[0])
                super().show()

        def main(self):
                self.tweener.update()

                # Manually pass mouse events to the inventory widgets so that dragging
                # can occur while the mouse is outside the widget (bgui won't normally pass info)
                mouse = bge.logic.mouse

                pos = list(mouse.position)
                pos[0] *= bge.render.getWindowWidth()
                pos[1] = bge.render.getWindowHeight() - (bge.render.getWindowHeight() * pos[1])

                mouse_state = bgui.BGUI_MOUSE_NONE
                mouse_events = mouse.events

                if mouse_events[bge.events.LEFTMOUSE] == bge.logic.KX_INPUT_JUST_ACTIVATED:
                        mouse_state = bgui.BGUI_MOUSE_CLICK
                elif mouse_events[bge.events.LEFTMOUSE] == bge.logic.KX_INPUT_JUST_RELEASED:
                        mouse_state = bgui.BGUI_MOUSE_RELEASE
                elif mouse_events[bge.events.LEFTMOUSE] == bge.logic.KX_INPUT_ACTIVE:
                        mouse_state = bgui.BGUI_MOUSE_ACTIVE

                self.player_inventory.click_state = mouse_state
                self.other_inventory.click_state = mouse_state

                if self.player_inventory.dragging:
                        self.player_inventory._handle_mouse(pos, mouse_state)
                elif self.other_inventory.dragging:
                        self.other_inventory._handle_mouse(pos, mouse_state)
