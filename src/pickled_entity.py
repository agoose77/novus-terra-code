class PickledEntity:
    def __init__(self):
        self.id = None
        self.type = None
        self.class_type = None
        self.library = None
        self.object_name = None
        self.position = None
        self.orientation = None
        self.linear_velocity = None
        self.angular_velocity = None
        self.frozen = None
        
    def add_to_world(self):
        from game import Game
        Game.entity[self.class_type].from_pickled_entity(self)
        
    def remove_from_world(self):
        from entity_base import EntityBase
        from game import Game
        if self.id in EntityBase.entities.keys():
            entity = Game.entity['EntityBase'].entities[self.id]
            
            # Save position, rotation and velocity but as lists not Vectors
            self.position = entity.worldPosition[:]
            self.orientation = [\
                entity.worldOrientation[0][:],
                entity.worldOrientation[1][:],
                entity.worldOrientation[2][:]]
            self.linear_velocity = entity.worldLinearVelocity[:]
            self.angular_velocity = entity.worldAngularVelocity[:]
            
            self.frozen = entity.frozen
            
            entity.destroy()
            del(entity)
 