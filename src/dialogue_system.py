import math
import xml.etree.ElementTree as etree

import bge
import blf

import bgui

CONTENT_BOX_PADDING = 5 # in px
NAME_BOX_PADDING = 5 # in px
MORE_BUTTON_PADDING = 8 # in px
SCROLL_BAR_WIDTH = 12 # in px



def init(cont=None):
    if isinstance(cont, bge.types.SCA_PythonController):
        theme = cont.owner.get('ds_theme', None)
        if theme is not None:
            theme = bge.logic.expandPath(theme)
        bge.logic.globalDict['dialogue_system'] = DialogueSystem([cont.owner.get('ds_width', bge.render.getWindowWidth()-100),cont.owner.get('ds_height', 250)], theme)
        print ('BGE INITERESE1233333')
    else:
        bge.logic.globalDict['dialogue_system'] = DialogueSystem()
        print ("YERSYSET")

def main(cont=None):
    if 'dialogue_system' not in bge.logic.globalDict:
        init(cont)

    bge.logic.globalDict['dialogue_system'].main()

def display_dialogue_tree(other):
    if 'dialogue_system' not in bge.logic.globalDict:
        init(other)

    if isinstance(other, bge.types.SCA_PythonController):
        path = bge.logic.expandPath(other.owner.get('ds_dialogue_tree_path', ''))
        bge.logic.globalDict['dialogue_system'].display_dialogue_tree(path)
    elif isistnace(other, str):
        bge.logic.globalDict['dialogue_system'].display_dialogue_tree(other)

def end_dialogue(other):
    if 'dialogue_system' not in bge.logic.globalDict:
        init(other)

    bge.logic.globalDict['dialogue_system'].end_dialogue()



##################################
class DialogueSystem(bgui.System):
    def __init__(self, content_box_size=[bge.render.getWindowWidth()-100, 250], theme=None):
        self.current_tree = None
        self.current_tree_iter = None
        self.current_node = None
        self.current_tree_labels = {}

        self.text_init = False
        self.option_container_init = False
        self.option_init = {}
        self.current_selection = None
        self.current_option_container = []

        self.init_gui(content_box_size, theme)

    def init_gui(self, content_box_size, theme):
        bgui.System.__init__(self, theme)
        self.mouse_state = bgui.BGUI_MOUSE_NONE

        self.gui_content_box = bgui.Frame(self, 'ds_content_box', size=content_box_size, pos=[0, 50], sub_theme='content_box', options=bgui.BGUI_CENTERX|bgui.BGUI_THEMED)
        self.gui_content_box.visible = False

        self.gui_content_scrollbar = ScrollBar(self, 'ds_content_scrollbar', size=[SCROLL_BAR_WIDTH/self.size[0], content_box_size[1]/self.size[1]],
                pos=[(self.gui_content_box.position[0]+self.gui_content_box.size[0])/self.size[0], self.gui_content_box.position[1]/self.size[1]])
        self.gui_content_scrollbar.on_scroll = self.update_text_position
        self.gui_content_scrollbar.visible = False

        self.gui_content_text = TextBlock(self, 'ds_content_text', color=(1,1,1,1,),
                size=[self.gui_content_box.size[0]-2*CONTENT_BOX_PADDING, content_box_size[1]-2*CONTENT_BOX_PADDING],
                pos=[self.gui_content_box.position[0]+CONTENT_BOX_PADDING, self.gui_content_box.position[1]+CONTENT_BOX_PADDING],
                options=bgui.BGUI_NONE)
        self.gui_content_text.visible = False

        self.gui_name_box = bgui.Frame(self.gui_content_box, 'ds_name_box', size=[0,0], pos=[0,1+NAME_BOX_PADDING/self.gui_content_box.size[1]], sub_theme='name_box')
        self.gui_name_box.visible = False

        self.gui_name_text = Label(self.gui_name_box, 'ds_name_text', '', pos=[NAME_BOX_PADDING, NAME_BOX_PADDING], sub_theme='name', options=bgui.BGUI_THEMED)

        self.gui_more_button = MoreButton(self, 'ds_more_button', text='More', size=[1,1], pos=[self.gui_content_box.position[0]+self.gui_content_box.size[0],
            self.gui_content_box.position[1]], sub_theme='more_button', options=bgui.BGUI_THEMED)
        self.gui_more_button.on_click = self.end_text_node

        self.gui_selection_box = bgui.Frame(self, 'ds_selection_box', size=[content_box_size[0]-2*CONTENT_BOX_PADDING, 30], pos=[self.gui_content_box.position[0]+CONTENT_BOX_PADDING,0], sub_theme='selection_box', options=bgui.BGUI_THEMED)
        self.gui_selection_box.visible = False

    def update_mouse(self, pos, click_state=bgui.BGUI_MOUSE_NONE):
        """Extend bgui.System.update_mouse to keep track of the mouse state.
        Required for ScrollBar to function properly."""
        self.mouse_state = click_state

        bgui.System.update_mouse(self, pos, click_state)

    def display_dialogue_tree(self, filepath):
        self.end_dialogue()

        self.current_tree = etree.parse(filepath)
        self.current_node = self.current_tree.getroot()
        self.current_tree_iter_index = 0
        self.current_tree_iter = []
        for element in self.current_tree.iter():
            if element.tag == 'label':
                self.current_tree_labels[element.text] = element
            self.current_tree_iter.append(element)

    def next_node(self):
        self.current_tree_iter_index += 1
        if self.current_tree_iter_index >= len(self.current_tree_iter):
            self.end_dialogue()
        else:
            self.current_node = self.current_tree_iter[self.current_tree_iter_index]


    def end_dialogue(self):
        self.current_tree = None
        self.current_node = None
        self.current_tree_iter = None
        self.current_tree_iter_index = None

        self.text_init = False
        self.option_container_init = False
        self.option_init = []
        self.current_selection = None
        self.current_option_container = []
        self.gui_content_box.visible = False
        self.gui_content_text.text =''
        self.gui_content_text.visible = False
        self.gui_content_scrollbar.visible = False
        self.gui_name_box.visible = False
        self.gui_name_text.text = ''
        self.gui_name_text.visible = False
        self.gui_more_button.visible = False

    def handle_conversation(self):
        self.next_node()

    def end_text_node(self, widget=None):
        self.text_init = False
        self.next_node()

    def handle_text(self):
        keyboard = bge.logic.keyboard

        if self.text_init:
            if keyboard.events[bge.events.ENTERKEY] == bge.logic.KX_INPUT_JUST_ACTIVATED:
                self.end_text_node()
        else:
            self.text_init = True
            self.gui_content_text.visible = True
            self.gui_content_box.visible = True
            self.gui_content_scrollbar.visible = True
            self.gui_more_button.visible = True
            self.gui_selection_box.visible = False
            self.gui_content_text.text = self.current_node.text
            self.gui_content_scrollbar.slider_height = self.gui_content_box.size[1]/(self.gui_content_text.char_height*(1+len(self.gui_content_text._lines)))
            self.gui_content_scrollbar.slider_position = (self.gui_content_scrollbar.size[1]-self.gui_content_scrollbar.slider_height)/self.gui_content_scrollbar.size[1]

    def update_text_position(self, scrollbar):
        for line in self.gui_content_text._lines:
            line.position = [0, (line.position[1]-line.parent.position[1])/line.parent.size[1]+ (scrollbar.change * (self.gui_content_text.char_height * len(self.gui_content_text._lines) /self.gui_content_box.size[1]))]
        self.gui_content_text.update_overflow()

    def handle_name(self):
        if self.current_node.text == '' or self.current_node.text is None:
            self.gui_name_box.visible = False
            self.gui_name_text.visible = False
            self.gui_name_text.text = ''
        else:
            self.gui_name_box.visible = True
            self.gui_name_text.visible = True
            self.gui_name_text.text = self.current_node.text
            self.gui_name_box.size = [(self.gui_name_text.size[0]+2*CONTENT_BOX_PADDING)/self.gui_content_box.size[0], (self.gui_name_text.size[1]+2*CONTENT_BOX_PADDING)/self.gui_content_box.size[1]]

        self.next_node()

    def handle_portrait(self):
        self.next_node()

    def end_option_container(self):
        self.option_container_init = False
        self.current_tree_iter_index = self.current_tree_iter.index(self.current_node[self.current_selection])
        self.current_node = self.current_tree_iter[self.current_tree_iter_index]
        self.gui_selection_box.visible = False


    def handle_option_container(self):
        mouse = bge.logic.mouse
        if self.option_container_init:
            pos = self.cursor_pos
            if self.current_selection is not None:
                cur_line = self.gui_content_text._lines[self.current_selection]
                if mouse.events[bge.events.LEFTMOUSE] == bge.logic.KX_INPUT_JUST_ACTIVATED and \
                    (self.gui_content_box.gl_position[0][0] <= pos[0] <= self.gui_content_box.gl_position[1][0]) and \
                    (cur_line.gl_position[0][1] <= pos[1] <= cur_line.gl_position[2][1]):
                    self.end_option_container()
                    return

            if (self.gui_content_box.gl_position[0][0] <= pos[0] <= self.gui_content_box.gl_position[1][0]) and \
                (self.gui_content_box.gl_position[0][1] <= pos[1] <= self.gui_content_box.gl_position[2][1]):
                for line in self.gui_content_text._lines:
                    widget = line
                    if (line.gl_position[0][1] <= pos[1] <= line.gl_position[2][1]):
                            index = self.gui_content_text._lines.index(line)
                            count = 0
                            start = 0
                            end = 0
                            for id, amount in enumerate(self.gui_content_text._options):
                                if count+amount-1 < index:
                                    count += amount
                                else:
                                    start = count
                                    end = count+amount-1
                                    self.current_selection = id
                                    break
                            top = self.gui_content_text._lines[start].position[1]+self.gui_content_text.char_height*self.gui_content_text.size[1]
                            bot = self.gui_content_text._lines[end].position[1]
                            if top > self.gui_content_box.position[1]+self.gui_content_box.size[1]-CONTENT_BOX_PADDING:
                                top = self.gui_content_box.position[1]+self.gui_content_box.size[1]-CONTENT_BOX_PADDING
                            if bot < self.gui_content_box.position[1]+CONTENT_BOX_PADDING:
                                bot = self.gui_content_box.position[1]+CONTENT_BOX_PADDING
                            self.gui_selection_box.size = [self.gui_selection_box.size[0], top-bot]
                            self.gui_selection_box.position = [self.gui_selection_box.position[0], bot]
                            self.gui_selection_box.visible = True
                            return
                self.gui_selection_box.visible = False
            else:
                self.gui_selection_box.visible = False
        else:
            self.current_option_container.append(self.current_node)
            self.option_container_init = True
            self.gui_content_text.visible = True
            self.gui_content_box.visible = True
            self.gui_content_scrollbar.visible = True
            self.gui_more_button.visible = False
            text = ''
            for node in self.current_node:
                text += node.attrib['choice_text'] + " \o "
            text = text[:-3]
            self.gui_content_text.text = text
            self.gui_content_scrollbar.slider_height = self.gui_content_box.size[1]/(self.gui_content_text.char_height*(1+len(self.gui_content_text._lines)))
            self.gui_content_scrollbar.slider_position = (self.gui_content_scrollbar.size[1]-self.gui_content_scrollbar.slider_height)/self.gui_content_scrollbar.size[1]

    def handle_option(self):
        def count_children(node):
            count = 1
            for child in node:
                count += count_children(child)
            return count

        if not self.current_option_container[-1] in self.option_init:
            self.option_init.append(self.current_option_container[-1])
            self.next_node()
        else:
            self.option_init.remove(self.current_option_container[-1])
            self.current_tree_iter_index = self.current_tree_iter.index(self.current_option_container[-1])+count_children(self.current_option_container[-1])
            if self.current_tree_iter_index >= len(self.current_tree_iter):
                self.end_dialogue()
            else:
                self.current_node = self.current_tree_iter[self.current_tree_iter_index]


    def handle_label(self):
        self.next_node()

    def handle_goto(self):
        def get_parent(child):
            for node in self.current_tree_iter:
                if child in node:
                    return node

        def travel_up(cur, goal):
            if cur == goal:
                return
            else:
                cur -= 1
                node = self.current_tree_iter[cur]
                if node.tag == 'option_container' and node in self.option_init:
                    self.option_init.remove(node)
                    self.current_option_container.remove(node)
                travel_up(cur, goal)

        def travel_down():
            pass

        index = self.current_tree_iter.index(self.current_tree_labels[self.current_node.text])
        if index < self.current_tree_iter_index:
            travel_up(self.current_tree_iter_index, index)
        self.current_node = self.current_tree_iter[index]
        self.current_tree_iter_index = index

    def handle_mouse(self):
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

        self.update_mouse(pos, mouse_state)

    def main(self):
        if self.current_tree is None:
            if self.render in bge.logic.getCurrentScene().post_draw:
                bge.logic.getCurrentScene().post_draw.remove(self.render)
            return

        self.handle_mouse()

        if self.current_node is None:
            return
        elif self.current_node.tag == 'conversation':
            self.handle_conversation()
        elif self.current_node.tag == 'text':
            self.handle_text()
        elif self.current_node.tag == 'name':
            self.handle_name()
        elif self.current_node.tag == 'portrait':
            self.handle_portrait()
        elif self.current_node.tag == 'option_container':
            self.handle_option_container()
        elif self.current_node.tag == 'option':
            self.handle_option()
        elif self.current_node.tag == 'label':
            self.handle_label()
        elif self.current_node.tag == 'goto':
            self.handle_goto()

        if self.render not in bge.logic.getCurrentScene().post_draw:
            bge.logic.getCurrentScene().post_draw.append(self.render)

class ScrollBar(bgui.Widget):
    def __init__(self, parent, name, aspect=None, size=[1,1], pos=[0,0], sub_theme='', options=bgui.BGUI_DEFAULT):
        bgui.Widget.__init__(self, parent, name, aspect, size, pos, sub_theme, options)

        self._scroll_bar_slot = bgui.Frame(self, name+'_scroll_bar_slot', sub_theme='scroll_bar_slot')
        self._scroll_bar_slot.on_click = self._jump_to_point

        self._scroll_bar_slider = bgui.Frame(self._scroll_bar_slot, name+'_scroll_bar_slider', size=[1,1], pos=[0,0], sub_theme='scroll_bar_slider')
        self._scroll_bar_slider.on_click = self._begin_scroll

        self.is_being_scrolled = False
        self._jump = False
        self._scroll_offset = 0 # how many pixels from the bottom of the slider scrolling started at
        self.change = 0

        self.on_scroll = None

    @property
    def slider_height(self):
        return self._scroll_bar_slider.size[1]

    @slider_height.setter
    def slider_height(self, height):
        self._scroll_bar_slider.size = [1, min(self.size[1], height)/self.size[1]]

    @property
    def slider_position(self):
        return self._scroll_bar_slider.position[1]

    @slider_position.setter
    def slider_position(self, pos):
        self._scroll_bar_slider.position = [0, pos]

    def _jump_to_point(self, widget):
        if self.is_being_scrolled:
            return
        self._jump = True

    def _begin_scroll(self, widget):
        self.is_being_scrolled = True
        self._scroll_offset = self.system.cursor_pos[1] - self._scroll_bar_slider.position[1]

    def _draw(self):
        if self._jump and not self.is_being_scrolled:
            # jump code
            pass
        self._jump = False

        if self.is_being_scrolled:
            if self.system.mouse_state not in [bgui.BGUI_MOUSE_CLICK, bgui.BGUI_MOUSE_ACTIVE]:
                self.is_being_scrolled = False
            else:
                if int(max(self.position[1]+self._scroll_offset, min(self.position[1]+self.size[1]+self._scroll_offset, int(self.system.cursor_pos[1])))) != int(self._scroll_bar_slider.position[1]+self._scroll_offset):
                    self.change = self._scroll_bar_slider.position[1]
                    self._scroll_bar_slider.position = [0, min(1-self._scroll_bar_slider.size[1]/self.size[1], max(0, (self.system.cursor_pos[1]-self.position[1]-self._scroll_offset)/self.size[1]))]
                    self.change -= self._scroll_bar_slider.position[1]
                    if self.on_scroll:
                        self.on_scroll(self)
                else:
                    self.change = 0
        else:
            self.change = 0

        bgui.Widget._draw(self)

class TextBlock(bgui.TextBlock):
    """
    Alter the functionality of bgui.TextBlock to work nicely with the dialogue system
    """
    @property
    def text(self):
        """The text to display"""
        return self._text

    @text.setter
    def text(self, value):

        # Get rid of any old lines
        for line in self._lines:
            self._remove_widget(line)

        self._lines = []
        self._options = []
        self._text = value

        # If the string is empty, then we are done
        if not value: return

        lines = value.split('\n')
        for i, v in enumerate(lines):
            lines[i] = v.split()

        cur_line = 0
        line = Label(self, "tmp", "Mj|", sub_theme='content')
        self._remove_widget(line)
        char_height = line.size[1]
        char_height /= self.size[1]
        self.char_height = char_height

        options_count = 1

        for words in lines:
            line = Label(self, "lines_"+str(cur_line), "", pos=[0, 1-(cur_line+1)*char_height], sub_theme='content')

            while words:
                if words[0] == "\\o":
                    self._options.append(options_count)
                    self._lines.append(line)
                    cur_line += 1
                    options_count = 1
                    line = Label(self, "lines_"+str(cur_line), "", pos=[0, 1-(cur_line+1)*char_height], sub_theme='content')
                    words.remove(words[0])
                    continue

                # Try to add a word
                if line.text:
                    line.text += " " + words[0]
                else:
                    line.text = words[0]

                # The line is too big, remove the word and create a new line
                if line.size[0] > self.size[0]:
                    line.text = line.text[0:-(len(words[0])+1)]
                    self._lines.append(line)
                    cur_line += 1
                    options_count += 1
                    line = Label(self, "lines_"+str(cur_line), "", pos=[0, 1-(cur_line+1)*char_height], sub_theme='content')
                else:
                    # The word fit, so remove it from the words list
                    words.remove(words[0])

            # Add what's left
            self._lines.append(line)
            cur_line += 1
            options_count += 1

        self._options.append(options_count-1)

        self.update_overflow()

    def update_overflow(self):
        line_height = self.char_height * self.size[1]
        for line in self._lines:
            if line.position[1] < self.position[1] + self.char_height*self.size[1]:
                color = list(line.color)
                color[3] = max(0, (line.position[1] - self.position[1]) / (self.char_height*self.size[1]))
                line.color = color
            elif line.position[1] > self.position[1] + self.size[1] - self.char_height*self.size[1]:
                color = list(line.color)
                color[3] = 1+(self.position[1]+self.size[1]-line.position[1]-self.char_height*self.size[1]) / (self.char_height*self.size[1]/2)
                line.color = color
            else:
                color = list(line.color)
                color[3] = 1.0
                line.color = color

class Label(bgui.Label):
    """Make bgui.Label play nice with the dialogue system"""
    def __init__(self, parent, name, text="", font=None, pt_size=None, color=None,
                pos=[0, 0], sub_theme='', options=bgui.BGUI_DEFAULT):
        bgui.Widget.__init__(self, parent, name, None, [0,0], pos, sub_theme, options)

        if font:
            self.fontid = blf.load(font)
        elif self.theme:
            self.fontid = blf.load(bge.logic.expandPath(self.theme.get(self.theme_section, 'Font')))
        else:
            self.fontid = 0

        if pt_size:
            self.pt_size = pt_size
        elif self.theme:
            self.pt_size = int(self.theme.get(self.theme_section, 'Size'))
        else:
            self.pt_size = 30

        # Normalize the pt size (1000px height = 1)
        if self.system.normalize_text:
            self.pt_size = int(self.pt_size * (self.system.size[1]/1000))
        else:
            self.pt_size = pt_size

        if color:
            self.color = color
        elif self.theme:
            # self.color = (1, 1, 1, 1)
            # self.color = list(self.theme.get(Label.theme_section, 'Color'))
            self.color = [float(i) for i in self.theme.get(self.theme_section, 'Color').split(',')]
        else:
            # default to white
            self.color = (1, 1, 1, 1)

        self.text = text

class MoreButton(bgui.FrameButton):
    def __init__(self, *args, **kwargs):
        bgui.FrameButton.__init__(self, *args, **kwargs)

        text = self.text
        self.label = Label(self, self.name + '_label', text, pos=[0,0], sub_theme='more_button', options=bgui.BGUI_THEMED | bgui.BGUI_CENTERED)

        self.size = [self.label.size[0]+MORE_BUTTON_PADDING, self.label.size[1]+MORE_BUTTON_PADDING]
        self.position = [self.position[0]-self.size[0], self.position[1]-self.size[1]]

        self.label._update_position(self.label._base_size, self.label._base_pos)