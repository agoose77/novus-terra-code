# filepath constants

try:
	import bge
except:
	pass

PATH_SOUNDS = bge.logic.expandPath("//sounds\\")
PATH_MUSIC = bge.logic.expandPath("//music\\")

def safepath(filename):
	filename = filename.replace("/", "\\")
	filename = filename.replace(".\\","//")
	return bge.logic.expandPath(filename)
	
def safeopen(filename, arg1):
	return open(safepath(filename), arg1)