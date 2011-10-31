import sys
from code import InteractiveConsole

import bge
from bgl import *
import blf

# Console consts
PROMPT = '>>> '
PROMPT_MULTI = '... '

SCROLLBACK = (0.4 * bge.render.getWindowHeight() - 0.02 * bge.render.getWindowHeight())
WRAP = (bge.render.getWindowWidth() - 0.04 * bge.render.getWindowWidth())

def builtins():    
    return locals()

def default_namespace():
    """Add entries into this dict to be able to access it by default
    in the console, i.e, not having to define them"""
    namespace = builtins()
    
    namespace.update({\
        'bge':bge\
    })
    
    return namespace
    
def is_delimiter(ch):
    if ch == '_':
        return False
    if ch.isalnum():
        return False
    
    return True
    
def is_delimiter_autocomp(ch):
    if ch in '._':
        return False
    if ch.isalnum():
        return False
    
    return True
    
messages = []
class fileRedirect:
    def __init__(self, error):
        self.error = error
        self.used = False
    def write(self, data):
        messages.append((self.error, data))
    def read(self):
        return ''.join([m[1] for m in messages])
    def close(self):
        messages[:] = []

class Console:
    """Console object"""
    def __init__(self, font, toggle_key=None):
        """Console constructor
        
        Arguments:
            font - path to font file
            toggle_key - keycode to enable/disable console"""
        global SCROLLBACK, WRAP
        self.toggle_key = toggle_key
        
        self.active = False
        
        # GUI
        view_buf = Buffer(GL_INT, 4)
        glGetIntegerv(GL_VIEWPORT, view_buf)
        view = view_buf.to_list()
        
        self.text_size = [None] * 2
        
        self.text_fontid = blf.load(font) if font else 0
        blf.size(self.text_fontid, 14, 72)
        self.text_size[0], self.text_size[1] = blf.dimensions(self.text_fontid, "W")
        self._text = ''
        
        SCROLLBACK = int(SCROLLBACK/(2 * self.text_size[1]))
        WRAP = int(WRAP/(self.text_size[0]))
        
        # Console
        self.namespace = default_namespace()
        self.console = InteractiveConsole(self.namespace)
        self.cursor = 0
        self.edit_text = ''
        self.scrollback = []
        self.history = ['']
        self.is_multiline = False
        
        message = """Interactive Console"""
        self.add_scrollback(message)
        
    def _get_text(self):
        return self._text
    def set_text(self, value):
        self.text_size[0], self.text_size[1] = blf.dimensions(self.text_fontid, value)

        #self._update_position(size, self._base_pos)

        self._text = value
        
    def render(self):
        """Renders the GUI system"""
        ww = bge.render.getWindowWidth()
        wh = bge.render.getWindowHeight()
        # Get some viewport info
        view_buf = Buffer(GL_INT, 4)
        glGetIntegerv(GL_VIEWPORT, view_buf)
        view = view_buf.to_list()

        # Save the state
        glPushMatrix();
        glPushAttrib(GL_ALL_ATTRIB_BITS)
        
        # Diable depth test so we always draw over things
        glDisable(GL_DEPTH_TEST)
        
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Setup the matrices
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, view[2], 0, view[3])
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # Render the windows
        glColor4f(0.3, 0.3, 0.3, 0.5)
        glBegin(GL_QUADS)
        glVertex2f(0, 2*wh/3)
        glVertex2f(ww, 2*wh/3)
        glVertex2f(ww, wh)
        glVertex2f(0, wh)
        glEnd()
        
        glColor4f(0.0, 0.0, 0.0, 1.0)
        glBegin(GL_LINE_STRIP)
        glVertex2f(0, 2*wh/3)
        glVertex2f(ww, 2*wh/3)
        glEnd()
        
        blf.size(self.text_fontid, 14, 72)
            
        glColor4f(1,1,1,1)

        for i, txt in enumerate([i for i in self._text.split('\n')]):
            blf.position(self.text_fontid, 20, wh + 20 - (self.text_size[1]*(i-1)), 0)
            blf.draw(self.text_fontid, txt.replace('\t', '    '))
        
        # Reset the state
        glPopAttrib()
        glPopMatrix()
        
    def prev_char(self):
        cursor = self.cursor - 1
        if cursor < 0:
            return None
            
        try:
            return self.edit_text[cursor]
        except:
            return None
    
    def next_char(self):
        try:
            return self.edit_text[self.cursor]
        except:
            return None
            
    def fill_scrollback(self):
        sb = self.scrollback
        while len(sb) < SCROLLBACK:
            sb.append('')
            
        while len(sb) > SCROLLBACK:
            sb.pop(0)
    
    def add_scrollback(self, data):
        sb = self.scrollback
        
        
        if isinstance(data, str):
            data = data.split("\n")
            
        for line in data:
            while len(line) > WRAP:
                sb.append(line[:WRAP])
                line = line[WRAP:]
            sb.append(line)
            
        self.fill_scrollback()
    
    def cursor_left_step(self):
        self.cursor = max(0, self.cursor - 1)

    def cursor_right_step(self):
        self.cursor = min(len(self.edit_text), self.cursor + 1)
        
    def cursor_right_jump(self):
        if self.cursor >= len(self.edit_text):
            return
            
        cursor_prev = self.cursor
        while (not is_delimiter(self.edit_text[self.cursor])):
            self.cursor_right_step()
            if cursor_prev == self.cursor:
                break
            cursor_prev = self.cursor
            if self.cursor >= len(self.edit_text):
                return
                
        if self.cursor >= len(self.edit_text):
            return
            
        cursor_prev = self.cursor
        while is_delimiter(self.edit_text[self.cursor]):
            self.cursor_right_step()
            if cursor_prev == self.cursor:
                break
            cursor_prev = self.cursor
            if self.cursor >= len(self.edit_text):
                return
    
    def cursor_left_jump(self):
        if self.cursor == 0:
            reutnr
            
        cursor_prev = self.cursor
        while (not is_delimiter(self.edit_text[self.cursor-1])):
            self.cursor_left_step()
            if cursor_prev == self.cursor:
                break
            cursor_prev = self.cursor
            if self.cursor == 0:
                return
                
        cursor_prev = self.cursor
        while (is_delimiter(self.edit_text[self.cursor-1])):
            self.cursor_left_step()
            if cursor_prev == self.cursor:
                break
            cursor_prev = self.cursor
    
    def cursor_backspace_step(self):
        if self.cursor == 0:
            pass
        elif self.cursor == len(self.edit_text):
            self.edit_text = self.edit_text[:-1]
        else:
            self.edit_text = self.edit_text[:self.cursor-1] + self.edit_text[self.cursor:]
            
        self.cursor_left_step()
    
    def cursor_backspace_jump(self):
        cursor_prev = self.cursor
        self.cursor_left_jump()
        if cursor_prev != self.cursor:
            self.edit_text = self.edit_text[:self.cursor] + self.edit_text[cursor_prev:]
    
    def cursor_delete_step(self):
        if self.cursor == 0:
            self.edit_text = self.edit_text[1:]
        elif self.cursor == len(self.edit_text):
            pass
        else:
            self.edit_text = self.edit_text[:self.cursor] + self.edit_text[self.cursor+1:]
    
    def cursor_delete_jump(self):
        cursor_prev = self.cursor
        self.cursor_right_jump()
        if cursor_prev != self.cursor:
            self.edit_text = self.edit_text[:cursor_prev] + self.edit_text[self.cursor:]
        self.cursor = cursor_prev

    def cursor_insert_char(self, ch):
        if self.cursor == 0:
            self.edit_text = ch + self.edit_text
        elif self.cursor == len(self.edit_text):
            self.edit_text = self.edit_text + ch
        else:
            self.edit_text = self.edit_text[:self.cursor] + ch + self.edit_text[self.cursor:]
            
        if self.cursor > len(self.edit_text):
            self.cursor = len(self.edit_text)
        self.cursor_right_step()
    
    def cursor_home(self):
        self.cursor = 0

    def cursor_end(self):
        self.cursor = len(self.edit_text)
        
    def history_up(self):
        hs = self.history
        
        hs[0] = self.edit_text
        hs.append(hs.pop(0))
        self.edit_text = hs[0]
        self.cursor_end()
    
    def history_down(self):
        hs = self.history
        
        hs[0] = self.edit_text
        hs.insert(0, hs.pop())
        self.edit_text = hs[0]
        self.cursor_end()
    
    def execute(self):
        self.add_scrollback(self.get_text_commandline())
        stdout_redir = fileRedirect(False)
        stderr_redir = fileRedirect(True)
        
        sys.stdout = stdout_redir
        sys.stderr = stderr_redir
        
        if not self.edit_text.strip():
            pytext = '\n' # executes a multiline statement
        else:
            pytext = self.edit_text
            
        self.is_multiline = self.console.push(pytext)
        
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        sys.last_trackback = None
        
        output = stdout_redir.read()
        stdout_redir.close()

        if output:
            self.add_scrollback(output) # could be stderr_redit too
        # Avoid double ups, add the new one at the front
        if pytext != '\n':
            if self.edit_text in self.history:
                self.history.remove(self.edit_text)
                
            self.history.insert(0, self.edit_text)
            
            if '' in self.history:
                self.history[:] = [v for v in self.history if v]
                
            self.history.insert(0, '')
            self.edit_text = ''
            
        self.cursor_end()


    def autocomp(self):
        
        def do_autocomp(autocomp_prefix, autocomp_members):
            '''
            return text to insert and a list of options
            '''
            autocomp_members = [v for v in autocomp_members if v.startswith(autocomp_prefix)]
            
            if not autocomp_prefix:
                return '', autocomp_members
            elif len(autocomp_members) > 1:
                # find a common string between all members after the prefix 
                # 'ge' [getA, getB, getC] --> 'get'
                
                # get the shortest member
                min_len = min([len(v) for v in autocomp_members])
                
                autocomp_prefix_ret = ''
                
                for i in xrange(len(autocomp_prefix), min_len):
                    char_soup = set()
                    for v in autocomp_members:
                        char_soup.add(v[i])
                    
                    if len(char_soup) > 1:
                        break
                    else:
                        autocomp_prefix_ret += char_soup.pop()
                    
                return autocomp_prefix_ret, autocomp_members
            elif len(autocomp_members) == 1:
                return autocomp_members[0][len(autocomp_prefix):], []
            else:
                return '', []
        
        
        
        TEMP_NAME = '___tempname___'
        
        cursor_orig = self.cursor
        
        ch = self.prev_char()
        while ch != None and (not is_delimiter(ch)):
            ch = self.prev_char()
            self.cursor_left_step()
        
        if ch != None:
            self.cursor_right_step()
        
        cursor_base = self.cursor
        
        autocomp_prefix = self.edit_text[cursor_base:cursor_orig]
        
        # Get the previous word
        if self.prev_char == '.':
            self.cursor_left_step()
            ch = self.prev_char()
            while ch != None and is_delimiter_autocomp(ch)==False:
                ch = self.prev_char()
                self.cursor_left_step()
            
            cursor_new = self.cursor
            
            if ch != None:
                cursor_new+=1
            
            pytxt = self.edit_text[cursor_new:cursor_base-1]
            if pytxt:
                self.console.runsource(TEMP_NAME + '=' + pytxt, '<input>', 'single')
            else:
                val = None
            
            try:
                val = self.namespace[TEMP_NAME]
                del self.namespace[TEMP_NAME]
            except:
                val = None
            
            if val:
                autocomp_members = dir(val)
                
                autocomp_prefix_ret, autocomp_members = do_autocomp(autocomp_prefix, autocomp_members)
                
                self.cursor = cursor_orig
                for v in autocomp_prefix_ret:
                    self.cursor_insert_char(v)
                cursor_orig = self.cusor
                
                if autocomp_members:
                    self.add_scrollback(', '.join(autocomp_members))
            
            del val
            
        else:
            # Autocomp global namespace
            autocomp_members = self.namespace.keys()
            
            if autocomp_prefix:
                autocomp_members = [v for v in autocomp_members if v.startswith(autocomp_prefix)]
            
            autocomp_prefix_ret, autocomp_members = do_autocomp(autocomp_prefix, autocomp_members)
            
            self.cursor = cursor_orig
            for v in autocomp_prefix_ret:
                self.cursor_insert_char(v)
            cursor_orig = self.cursor
            
            if autocomp_members:
                self.add_scrollback(', '.join(autocomp_members))
        
        self.cursor = cursor_orig
    
    def get_text_commandline(self):
        self.fill_scrollback()
        
        if self.is_multiline:
            prefix = PROMPT_MULTI
        else:
            prefix = PROMPT
        
        return prefix + self.edit_text

    def get_text(self):
        self.fill_scrollback()
        return '\n'.join(self.scrollback) + '\n' + self.get_text_commandline()
    
    def handle_input(self):
        keyboard = bge.logic.keyboard
            
        key_events = keyboard.events
        
        is_shift = key_events[bge.events.LEFTSHIFTKEY] == bge.logic.KX_INPUT_ACTIVE or \
                    key_events[bge.events.RIGHTSHIFTKEY] == bge.logic.KX_INPUT_ACTIVE
        is_ctrl = key_events[bge.events.LEFTCTRLKEY] == bge.logic.KX_INPUT_ACTIVE or \
                    key_events[bge.events.RIGHTCTRLKEY] == bge.logic.KX_INPUT_ACTIVE
        
        # First deal with important keys
        if key_events[bge.events.LEFTARROWKEY] == bge.logic.KX_INPUT_JUST_ACTIVATED:
            self.cursor_left_jump() if is_ctrl else self.cursor_left_step()
            return
        if key_events[bge.events.RIGHTARROWKEY] == bge.logic.KX_INPUT_JUST_ACTIVATED:
            self.cursor_right_jump() if is_ctrl else self.cursor_right_step()
            return
        if key_events[bge.events.BACKSPACEKEY] == bge.logic.KX_INPUT_JUST_ACTIVATED:
            self.cursor_backspace_jump() if is_ctrl else self.cursor_backspace_step()
            return
        if key_events[bge.events.DELKEY] == bge.logic.KX_INPUT_JUST_ACTIVATED:
            self.cursor_delete_jump() if is_ctrl else self.cursor_delete_step()
            return
        if key_events[bge.events.HOMEKEY] == bge.logic.KX_INPUT_JUST_ACTIVATED:
            self.cursor_home()
            return
        if key_events[bge.events.ENDKEY] == bge.logic.KX_INPUT_JUST_ACTIVATED:
            self.cursor_end()
            return
        if key_events[bge.events.RETKEY] == bge.logic.KX_INPUT_JUST_ACTIVATED:
            self.execute()
            return
        if key_events[bge.events.UPARROWKEY] == bge.logic.KX_INPUT_JUST_ACTIVATED:
            self.history_up()
            return
        if key_events[bge.events.DOWNARROWKEY] == bge.logic.KX_INPUT_JUST_ACTIVATED:
            self.history_down()
            return
        if key_events[bge.events.TABKEY] == bge.logic.KX_INPUT_JUST_ACTIVATED:
            self.autocomp()
            return
        
        # Deal with characters
        for evt, val in keyboard.events.items():
            if val == bge.logic.KX_INPUT_JUST_ACTIVATED and evt != self.toggle_key:
                ch = bge.events.EventToCharacter(evt, is_shift)
                if ch:
                    self.cursor_insert_char(ch)
        
    def main(self):
        if self.toggle_key:
            if bge.logic.keyboard.events[self.toggle_key] == bge.logic.KX_INPUT_JUST_ACTIVATED:
                self.active = not self.active
                print(5)
            
        if self.active == True:
            self.handle_input()
            
            text = self.get_text()
            n = len(text) - len(self.edit_text)
            text = text[:n+self.cursor] + "_" + text[n+self.cursor:]
            self.text = text
            
            bge.logic.getCurrentScene().post_draw.append(self.render)
            
    text = property(_get_text, set_text)


    