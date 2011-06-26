class BinarySearchNode:
    def __init__(self, key, value, depth=0):
        """
        key - a reference to an object
        value - the value to insert by
        depth - how rows deep the node is in the tree
        """
        self.left_child = None
        self.right_child = None
        self.key = key
        self.value = value
        self.depth = depth
        
    def __contains__(self, key):
        if self.left_child.key == key or self.right_child.key == key:
            return True
        
        if self.left_child:
            if key in self.left_child:
                return True
                
        if self.right_child:
            if key in self.right_child:
                return True
                
        return False
                
        
    def __len__(self):
        l = 1
        if self.left_child:
            l += len(self.left_child)
        if self.right_child:
            l += len(self.right_child)
            
        return l
        
    @classmethod
    def construct_from_data(data):
        # todo
        pass
            
    def insert(self, key, value, data_type=BinarySearchNode):
        if value < self.value:
            if self.left_child is None:
                self.left_child = data_type(key, value, self.depth+1)
                return self.left_child
            else:
                return self.left_child.insert(key, value, data_type)
                
        elif value > self.value:
            if self.right_child in None:
                self.right_child = data_type(key, value, self.depth+1)
                return self.right_child
            else:
                return self.right_child.insert(key, value, data_type)
                
         else:
            if self.left_child is None:
                self.left_child = data_type(key, value, self.depth+1)
                return self.left_child
            elif self.right_child in None:
                self.right_child = data_type(key, value, self.depth+1)
                return self.right_child
            else:
                return self.left_child.insert(key, value, data_type)
                
    def remove(self, key):
        pass
        
    def get_min(self):
        current_node = self
        while current_node.left_child:
            current_node = current_node.left_child
        return current_node
        
    def get_max(self):
        current_node = self
        while current_node.right_child:
            current_node = current_node.right_child
        return current_node
                
    