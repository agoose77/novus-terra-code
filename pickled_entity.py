import bge

from entity_base import EntityBase

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
        class_type.from_pickled_entity(self)
        
    def remove_from_world(self):
        entity = EntityBase.entities[self.id]
        
        # Save position, rotation and velocity but as lists not Vectors
        self.position = entity.worldPosition[:]
        self.orientation = [\
            entity.worldOrientation[0][:],
            entity.worldOrientation[1][:],
            entity.worldOrientation[2][:]]
        self.linear_velocity = entity.worldLinearVelocity[:]
        self.roatational_velocity = entity.worldRotationalVelocity[:]
        
        self.frozen = entity.frozen
        
        entity.destroy()
        del(entity)