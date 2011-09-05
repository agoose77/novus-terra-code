################################
### ------ MouseTools ------ ###
################################
### Copyright 2009 Chase Moskal!
# This contains MOUSE, for mouse movement related stuff,
# CURSOR, for simple cursor stuff,
# and MOUSEBUTTONS, for mouseclicks and stuff.
# lots of stuff.

INIT = 0




##############################
### ------  MOUSE   ------ ###
##############################
# For getting Mouse movement information.

# Overmind must instantiate with a mouse movement sensor.
class MOUSE:
    import math
    import Rasterizer

    def __init__(self, mousemove):
        self.mousemove = mousemove

        self.width = self.Rasterizer.getWindowWidth()
        self.height = self.Rasterizer.getWindowHeight()

        self.centerX = self.width/2
        self.centerY = self.height/2


    def reset(self):
        self.Rasterizer.setMousePosition(int(self.centerX), int(self.centerY))


    def show(self, vis=1):
        self.Rasterizer.showMouse(vis)

    def hide(self, vis=0):
        self.Rasterizer.showMouse(vis)

    def getPosition(self):
        position = self.mousemove.position

        X = position[0]
        Y = position[1]

        return X, Y


    def isAtCenter(self):
        X, Y = self.getPosition()
        center = 1

        if X != self.centerX:
            center = 0

        if Y != self.centerY:
            center = 0

        return center


    def getPositionFromCenter(self):
        X, Y = self.getPosition()

        X = (X-self.centerX)
        Y = (self.centerY-Y)

        return X, Y

    def isPositive(self):
        if self.mousemove.positive:
            return 1
        else:
            return 0

    def getMovement(self):
        if self.isPositive():
            X, Y = self.getPositionFromCenter()
        else:
            X = 0
            Y = 0
        if X or Y:
            self.reset()
        return X, Y



####################################
### ------	CURSOR	  ------ ###
####################################
# For getting cursor information, position,
# object hover...

# Overmind must insantiate with a mouse over sensor.
class CURSOR:
    import Rasterizer
    
    def __init__(self, mouseover):
        self.mouseover = mouseover
    
    def getPosition(self):
        if self.mouseover.positive:
            pos = self.mouseover.hitPosition
            return pos
        return None

    def getRaisedPosition(self, a=0.5):
        position = self.getPosition()
        if position:
            position[2] += a
        return position
    
    def getHitObject(self):
        if self.mouseover.isPositive():
            obj = self.mouseover.getHitObject()
            return obj
        return None



##################################
### ------ MOUSEBUTTONS ------ ###
##################################
# Detects clicks and stuff.

# Deprecated, because it's kinda useless and stupid.
class MOUSEBUTTONS:
    def __init__(self, LMB):
        self.LMB = LMB
        self.LMB_TOG = 0

    def lmbClick(self):
        hit = 0
        if self.LMB.positive:
            if not self.LMB_TOG:
                hit = 1
                self.LMB_TOG = 1
        else:
            self.LMB_TOG = 0
        return hit