# A k-dimensional tree, used for representing spacial data, i.e, sorting points

from binary_search_node import BinarySearchNode

class KDNode(BinarySearchNode):
    def __init__(self, key, value, depth=0):
        BinarySearchNode.__init__(self, key, value[0], depth)
        
    @staticmethod
    def construct_kd_tree(object_list, depth=0):
        # from wikipedia, create a balanced kd tree from a list of objects
        if not object_list:
            return
     
        # Select axis based on depth so that axis cycles through all valid values
        axis = depth % 3
     
        # Sort point list and choose median as pivot element
        object_list.sort(key=lambda obj: ogj.worldPosition[axis])
        median = len(object_list) // 2 # choose median
     
        # Create node and construct subtrees
        node = KDNode(object_list[median])
        node.left_child = KDNode.construct_kd_tree(object_list[:median], depth + 1)
        node.right_child = KDNode.construct_kd_tree(object_list[median + 1:], depth + 1)
        return node
        
    def insert(self, key, value=None, data_type=None):
        axis = self.depth % 3 
        
        BinarySearchNode.insert(key, value[axis], KDNode)
        
    def radius_search(self, point, radius):
        # todo
        results = []
        
        axis = self.depth % 3
        
        if self.key.getDistanceTo(point) < radius:
            results.append(self.key)
            
            if self.left_child:
                results.expand(self.left_child.radius_search(point, radius))
            if self.right_child:
                results.expand(self.right_child.radius_seach(point, radius))
                
        else:
            pass
            
    def get_nearest_neighbour(self, point, neighbours=1):
        # todo
        pass