import configparser

# The following is a bit of a hack so we can get our own SectionProxy in.
# This allows us to return some nicer values from our config files
configparser._SectionProxy = configparser.SectionProxy

class NewSectionProxy(configparser._SectionProxy):
	
	def __getitem__(self, key):
		val = configparser._SectionProxy.__getitem__(self, key)
		
		if isinstance(val, configparser._SectionProxy):
			return val
		
		# Lets try to make a nicer value
		try:
			return float(val)
		except ValueError:
			pass
		except TypeError:
			print(type(val))
		
		if ',' in val:
			try:
				return [float(i) for i in val.split(',')]
			except ValueError:
				return val.split()
			
		return val

configparser.SectionProxy = NewSectionProxy

class Theme(configparser.SafeConfigParser):
	def __init__(self, file):
		
		configparser.SafeConfigParser.__init__(self)
		
		self.path = file
		
		if file:
			self.read(file+'/theme.cfg')
		
	def supports(self, widget):
		"""Checks to see if the theme supports a given widget.
		
		:param widget: the widget to check for support
		
		"""
		
		# First we see if we have the right section
		if not self.has_section(widget.theme_section):
			return False
		
		# Then we see if we have the required options
		for opt in widget.theme_options:
			if not self.has_option(widget.theme_section, opt):
				return False
			
		# All looks good, return True
		return True
