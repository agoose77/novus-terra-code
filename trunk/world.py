import pickle

import bge
from mathutils import Vector

from player import Player

class World:

    INTERIOR_WORLD = 0
    EXTERIOR_WORLD = 1
    
    def __init__(self):
        self.current_world_file = None
        self.current_cell = None
        self.loaded_libs = None
        self.loaded_kdtrees = None
        self.loaded_entities = None
        self.entity_loading_queue = None
        
        self.player = Player()
        self.player.worldPosition = [15,15,5]
        self.current_quest = None
        self.quest_manager = None
        
        self.world_time = None
        self.world_time_rate = None
        self.current_weather = None
        self.light_sources = None
        self.type = None
        self.gravity = Vector([0,0, -9.8])
        
    def create(self, world_file):
        # Load a world file and make it active
        # The actual loading doesn't take place until update_culling is called
        #self.current_world_file = bge.logic.globalDict['game'].current_savefile.load_file(world_file)
        file = open(bge.logic.expandPath("//novus_terra.world"), 'rb')
        self.current_world_file = pickle.load(file)
        self.type = 1#self.current_world_file['type']
        file.close()
        self.loaded_libs = {}
        self.loaded_kdtrees = []
        self.loaded_entities = []
        self.entity_loading_queue = []
        self.current_cell = None
        
    def destroy(self):
        # Frees all the data and restores the world back to its default state
        
        # remove the objects from the world
        for kdtree in self.loaded_kd_trees:
            self.free_kdtree(kdtree)
        
        # save changes
        bge.logic.globalDict['game'].savefile.pickle_file(self.current_world_file)
        
        # set default state
        self.current_world_file = None
        self.current_cell = None
        self.loaded_libs = None
        self.loaded_kdtrees = None
        self.loaded_entities = None
        self.entity_loading_queue = None
        
    def load_kdtree(self, kdtree):
        # loads a kdtree full of PickledEntities into the world
        for pickled_entity in kdtree:
            if pickled_entity.library in self.loaded_libs.keys():
                self.loaded_libs[pickled_entity.library].append(kdtree)
                
            self.entity_loading_queue.append([pickled_entity, kdtree])
            
        self.loaded_kdtrees.append(kdtree)
    
    def free_kdtree(self, kdtree):
        # frees a kdtree full of PickledEntities from the world
        for pickled_entity in kdtree:
            pickled_entity.remove_from_world()
        
        libs_to_free = []
        for (lib, kdtrees) in self.loaded_libs.items():
            if kdtree in kdtrees:
                self.loaded_libs[lib].remove(kdtree)
                if len(self.loaded_libs[lib]) == 0:
                    libs_to_free.append(lib)
                    
        for lib in libs_to_free:
            #bge.logic.FreeLib(lib)
            self.loaded_libs.pop(lib)
            
        self.loaded_kdtrees.remove(kdtree)
        
    def update_culling(self):
        # Adds/removes entities as the player moves around
        if self.type & World.EXTERIOR_WORLD:
            current_cell = self.current_world_file['data'].get_node_from_point(self.player.worldPosition)
            if self.current_cell != current_cell:
                if current_cell.key not in self.loaded_kdtrees:
                    self.load_kdtree(current_cell.key)
                
                kdtrees_to_load = []
                kdtrees_to_free = []
                
                neighbours = current_cell.get_neighbours(self.current_world_file['data'])

                loaded_kd_trees = self.loaded_kdtrees[:]
                for neighbour in neighbours:
                    if neighbour.key not in loaded_kd_trees:
                        kdtrees_to_load.append(neighbour.key)
                    else:
                        loaded_kd_trees.remove(neighbour.key) 
                kdtrees_to_free.extend(loaded_kd_trees)
                
                for kdtree in kdtrees_to_load:
                    if kdtree is not None:
                        self.load_kdtree(kdtree)
                    
                for kdtree in kdtrees_to_free:
                    if kdtree != current_cell.key:
                        self.free_kdtree(kdtree)
                    
                self.current_cell = current_cell
                    
        elif self.type & World.INTERIOR_WORLD:
            pass                   
        
    def update_entity_loading_queue(self):
        # Loads a entity into the scene every few frames
        if len(self.entity_loading_queue) != 0:
            pickled_entity, kdtree = self.entity_loading_queue.pop(0)
            
            if pickled_entity.library in self.loaded_libs.keys():
                pickled_entity.add_to_world()
            else:
                #bge.logic.LoadLib(bge.logic.expandPath(pickled_entity.library), 'Scene')
                self.loaded_libs[pickled_entity.library] = [kdtree]
                pickled_entity.add_to_world()
        
    def main(self):
        self.player.main()
        
        self.update_culling()
        self.update_entity_loading_queue()
        
        for entity in self.loaded_entities:
            entity.main()
    
    