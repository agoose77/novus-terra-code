from entity_base import EntityBase

class NPC(EntityBase):
    def __init__(self):
        EntityBase.__init__(self)
        
        self.conversation_file = None
        self.interact_distace = 2.0
        self.on_interact = self.start_conversation
        
    @classmethod
    def from_pickled_entity(cls, pickled_entity):
        if pickled_entity.id not in cls.entities.keys():
            entity = EntityBase(pickled_entity.object_name, pickled_entity.position,
                pickled_entity.orientation, pickled_entity.id, pickled_entity.type)
                
            entity.worldLinearVelocity = pickled_entity.linear_velocity
            entity.worldAngularVelocity = pickled_entity.angular_velocity
            
            entity.on_interact = entity.start_conversation
            entity.interact_distance = 2.2
            
            return entity
        
    def start_conversation(self):
        world = bge.logic.globalDict['game'].world
        world.player.remove_controls()
        
        world.dialogue_system.end_dialogue()
        world.dialogue_system.on_end = self.end_conversation
        world.diagloue_system.display_conversation
        
    def end_conversation(self):
        world = bge.logic.globalDict['game'].world
        world.player.restore_controls()