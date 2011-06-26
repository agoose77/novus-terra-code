import bge

class return_entity_base:
    def __init__(self, f):
        self.f = f
        
    def __call__(self, *args, **kwargs):
        data = self.f(*args, **kwargs)
        if isinstance(data, list):
            for n in range(len(data)):
                if isinstance(data[n], bge.types.KX_GameObject) or isinstance(data[n], bge.types.KX_Scene):
                    if 'entity_base' in data[n]:
                        data[n] = data[n]['entity_base']
        elif isinstance(data, bge.types.KX_GameObject) or isinstance(data, bge.types.KX_Scene):
            if 'entity_base' in data:
                data = data['entity_base']
        return data
                
                
class EntityBase:
    """ Base object for classes representing game objects.
    
    Maps KX_GameObject functions to the inheriting class."""
    
    entities = {}
    
    def __init__(self, object_name, position=[0,0,0], orientation=[[1,0,0], [0,1,0], [0,0,1]], id=None, type=None):
        control = bge.logic.getCurrentController().owner
        self._data = bge.logic.getCurrentScene().addObject(object_name, control)
        self._data['entity_base'] = self
        
        for item in dir(self._data):
            if hasattr(getattr(self._data, item), '__call__') and not item.startswith('__'):
                self.__dict__[item] = return_entity_base(getattr(self._data, item))
                
        self.id = id
        self.type = type
        
        self.frozen = False
        self.stored_linear_velocity = None
        self.stored_rotational_velocity = None
        
        self.on_interact = None
        self.interact_distance = 2.0
        self.interact_icon = None
        self.interact_label = ''
                
    def __getitem__(self, item):
        return self._data[item]
        
    def __setitem__(self, item, value):
        self._data[item] = value
    
    def __delitem__(self, item):
        self._data.__delitem__(item)
        
    def __repr__(self):
        return self._data.__repr__
    
    def __contains__(self, item):
        return item in self._data
        
    
        
    @property
    def actuators(self):
        return self._data.actuators
    
    @property
    def angularVelocity(self):
        return self._data.angularVelocity
        
    @angularVelocity.setter
    def angularVeloctity(self, velocity):
        self._data.angularVelocity = velocity
        
    @return_entity_base
    def get_children(self):
        return self._data.children
    children = property(get_children)
    
    @return_entity_base
    def get_children_recursive(self):
        return self._data.childrenRecursive
    childrenRecursive = property(get_children_recursive)
    
    @property
    def color(self):
        return self._data.color
        
    @property
    def controllers(self):
        return self._data.controllers
        
    @property
    def invalid(self):
        return self._data.invalid
        
    @property
    def life(self):
        return self._data.life
        
    @property
    def linVelocityMax(self):
        return self._data.linVelocityMax
        
    @property
    def linVelocityMin(self):
        return self._data.linVelocityMin
        
    @property
    def linearVelocity(self):
        return self._data.linearVelocity
        
    @linearVelocity.setter
    def linearVelocity(self, velocity):
        self._data.linearVelocity = velocity
        
    @property
    def localAngularVelocity(self):
        return self._data.localAngularVelocity
        
    @property
    def localIntertia(self):
        return self._data.localInertia
        
    @property
    def localLinearVelocity(self):
        return self._data.localLinearVelocity
        
    @localLinearVelocity.setter
    def localLinearVelocity(self, velocity):
        self._data.localLinearVelocity = velocity
        
    @property
    def localOrientation(self):
        return self._data.localOrientation
        
    @localOrientation.setter
    def localOrientation(self, orientation):
        self._data.localOrientation = orientation
        
    @property
    def localPosition(self):
        return self._data.localPosition
        
    @localPosition.setter
    def localPosition(self, position):
        self._data.localPosition = position
        
    @property
    def localScale(self):
        return self._data.localScale
        
    @property
    def mass(self):
        return self._data.mass
        
    @property
    def meshes(self):
        return self._data.meshes
        
    @property
    def name(self):
        return self._data.name
        
    @property
    def occlusion(self):
        return self._data.occlusion
        
    @property
    def orientation(self):
        return self._data.orientation
        
    @orientation.setter
    def orientation(self, orientation):
        self._data.orientation = orientation
        
    @return_entity_base
    def get_parent(self):
        return self._data.parent
    parent = property(get_parent)
    
    @property
    def position(self):
        return self._data.position
        
    @position.setter
    def position(self, position):
        self._data.position = position
        
    @property
    def scaling(self):
        return self._data.scaling
        
    @scaling.setter
    def scaling(self, scale):
        self._data.scaling = scale
        
    @property
    def sensors(self):
        return self._data.sensors
        
    @property
    def state(self):
        return self._data.state
        
    @property
    def timeOffset(self):
        return self._data.timeOffset
        
    @property
    def visible(self):
        return self._data.visible
        
    @property
    def worldAngularVelocity(self): 
        return self._data.worldAngularVelocity
        
    @worldAngularVelocity.setter
    def worldAngularVelocity(self, velocity):
        self._data.worldAngularVelocity = velocity
        
    @property
    def worldLinearVelocity(self):
        return self._data.worldLinearVelocity
        
    @worldLinearVelocity.setter
    def worldLinearVelocity(self, velocity):
        self._data.worldLinearVelocity = velocity
        
    @property
    def worldOrientation(self):
        return self._data.worldOrientation
        
    @worldOrientation.setter
    def worldOrientation(self, orientation):
        self._data.worldOrientation = orientation
        
    @property
    def worldPosition(self):
        return self._data.worldPosition
        
    @worldPosition.setter
    def worldPosition(self, position):
        self._data.worldPosition = position
        
    @property
    def worldScale(self):
        return self._data.worldScale