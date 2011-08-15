#!


import pickle, sys, traceback


from PIL import Image

class Map:
	def __init__(self,width,height,scale):
		self.width = width
		self.height = height
		self.scale = .1
		#height
		self.buffer = array('h', [0]*self.width*self.height)
		#normals
		self.nx = array('b', [0]*self.width*self.height)
		self.ny = array('b', [0]*self.width*self.height)
		self.nz = array('b', [0]*self.width*self.height)
		
	
if __name__ == '__main__':
	try:
		file = open( 'crosscrater_norms.txt', 'rb')
		norms = []
		i = 0
		for line in file:
			if line:
				i += 1
				print("reading line ", i)
				norms += eval(line)
		file.close()		
		print(len(norms))
		for i in range(len(norms)):
			norms[i] = (norms[i][0]+127, norms[i][1]+127, norms[i][2]+127)
		#print norms[0]
		im = Image.new('RGB',(4096,4096),(0,0,0) )
		im.putdata( tuple(norms))
		im.save("test.png")
	except:
		print traceback.print_exc(file=sys.stdout)
	closing = raw_input()
