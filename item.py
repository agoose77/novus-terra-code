class Item:

    CONSUMABLE_ITEM = 1
    QUEST_ITEM = 2
    CLOTHING_ITEM = 4
    WEAPON_ITEM = 8
    
    items = {}
    
    def __init__(self, id, type, name, description='', size=1, cost=0, modify_effects={},
            modify_effects_percentage={}, modify_duration=-1):
        self.id = id
        self.type = type
        
        self.name = name
        self.description = description
        self.size = size
        self.cost = cost
        
        self.modify_effects = modify_effects
        self.modify_effects_percentage = modify_effects_percentage
        self.modify_duration = modify_duration
        
        Item.items[id] = self
        
    def activate_item(self):
        pass
        
    
        