class QuadNode:
    def __init__(self, key=None, centre=[0,0], radius=0, depth=0):
        # children start in the 1st quadrant and go clockwise
        self.key = key
        self.centre = centre
        self.depth = depth
        self.children = []
        
    def subdivide(self, keys=[None]*4):
        cx = self.centre[0]
        cy = self.centre[1]
        r = self.radius
        
        child1 = QuadNode(keys[0], [cx+r/2, cy+r/2], r/2, self.depth+1)
        child2 = QuadNode(keys[1], [cx+r/2, cy-r/2], r/2, self.depth+1)
        child3 = QuadNode(keys[2], [cx-r/2, cy-r/2], r/2, self.depth+1)
        child4 = QuadNode(keys[3], [cx-r/2, cy+r/2], r/2, self.depth+1)
        
        self.children = [child1, child2, child3, child4]
        
    def get_node_from_point(self, point, depth=-1):
        if len(self.children) == 0:
            return self
        else:
            if point[0] > self.centre[0] and self.point[1] > self.centre[1]:
                return self.children[0].get_node_from_point(point)
            elif point[0] > self.centre[0] and self.point[1] < self.centre[1]:
                return self.children[1].get_node_from_point(point)
            elif point[0] < self.centre[0] and self.point[1] < self.centre[1]:
                return self.children[2].get_node_from_point(point)
            else:
                return self.children[3].get_node_from_point(point)
                
    def get_neighbours(self, root_node):
        cx = self.centre[0]
        cy = self.centre[1]
        r = self.radius
        
        n1 = root_node.get_node_from_point([cx+2*r, cy], self.depth))
        n2 = root_node.get_node_from_point([cx-2*r, cy], self.depth))
        n3 = root_node.get_node_from_point([cx, cy+2*r], self.depth))
        n4 = root_node.get_node_from_point([cx, cy-2*r], self.depth))
        n5 = root_node.get_node_from_point([cx+2*r, cy+2*r], self.depth))
        n6 = root_node.get_node_from_point([cx+2*r, cy-2*r], self.depth))
        n7 = root_node.get_node_from_point([cx-2*r, cy+2*r], self.depth))
        n8 = root_node.get_node_from_point([cx-2*r, cy-2*r], self.depth))
        
        neighbours = []
        if n1:
            neighbours.append(n1)
        if n2:
            neighbours.append(n2)
        if n3:
            neighbours.append(n3)
        if n4:
            neighbours.append(n4)
        if n5:
            neighbours.append(n5)
        if n6:
            neighbours.append(n6)
        if n7:
            neighbours.append(n7)
        if n8:
            neighbours.append(n8)
        
        return neighbours