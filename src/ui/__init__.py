""" The UI system is a high level interface, built
on top of bgui.

The system consists of the UIManager,
which moniters a stack of Screens, updating and drawing
them as required.

Screens take up the whole screen space and are,
essentially, a UI screen displaying specific
information.

"""

# Widgets
from .inventory_window import *
from .nwidgets import *
from .scrollbar import *
from .context_menu import *

# Screens
from .screen import *
from .hud import *
from .item_swap import *
from .loading import *
from .pause import *
from .start import *

# Manager
from .ui_manager import *
