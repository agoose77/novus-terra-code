# filepath constants

try:
	import bge
	PATH_SOUNDS = bge.logic.expandPath("//data/sounds\\")
	PATH_MUSIC = bge.logic.expandPath("//music\\")
except:
	pass



def safepath(filename):
	filename = filename.replace("/", "\\")
	filename = filename.replace(".\\","//")
	try: #hack for addon
		return bge.logic.expandPath(filename)
	except:
		return "bge not imported"

def safeopen(filename, arg1):
	return open(safepath(filename), arg1)