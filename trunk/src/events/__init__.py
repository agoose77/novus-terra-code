""" The event system handles the execution of events within
cells. Events are cell specific and should be used as a
way of scripting large sequences. Smaller common behaviours
(such as a door opening would be best approached by creating
an entity).
"""

from .event import *
from .event_manager import *
