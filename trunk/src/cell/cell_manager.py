import pickle
import os
import time

import tweener
import terrain
import cell
from item import Item
from weapon import Weapon


try:
    from entity_base import EntityBase
    import bge
    import ui
    import mathutils
    from paths import *
    import session
    #import session
except:
    print("BGE imports failed, normal if you are running the cell editor")

class Prop:
    def __init__(self, name="None", co=[0.0,0.0,0.0], scale=[1.0,1.0,1.0], dimensions=[1.0,1.0,1.0], rotation=[1.0,0.0,0.0], properties1=[]):
        self.id = 0
        self.name = name
        self.co = co
        self.scale = scale
        self.dimensions = dimensions
        self.rotation = rotation
        self.game_object = 0 #the BGE object pointer
        self.properties = properties1

    def kill(self):
        cell.singleton.props_in_game.remove(self)
        self.game_object.endObject()
        self.game_object = False

class Entity:
    """ This is an entity as far as what needs to be known from a cell file.  """
    def __init__(self, name="None", co=[0.0,0.0,0.0], scale=[1.0,1.0,1.0], dimensions=[1.0,1.0,1.0], rotation=[1.0,0.0,0.0], properties=[]):
        self.id = 0
        self.name = name
        self.co = co
        self.scale = scale
        self.dimensions = dimensions
        self.rotation = rotation
        self.game_object = 0 #the BGE object pointer
        self.properties = properties

class Lamp:
    def __init__(self, name="None", co=[0.0,0.0,0.0], rotation=[1.0,0.0,0.0], type="POINT", color=[0.0,0.0,0.0], distance=0.5, energy=50, spot_size=100, spot_blend=0.25, spot_bias=2.0):
        print ('added Lamp 00000000000000000000000000000')
        self.id = 0
        self.name = name
        self.co = co
        self.rotation = rotation
        self.type = type
        self.color = color
        self.distance = distance
        self.energy = energy
        self.spot_size = spot_size
        self.spot_blend = spot_blend
        self.spot_bias= spot_bias

    def kill(self):
        cell.singleton.lamps_in_game.remove(self)
        if self.type == "SPOT":
            cell.singleton.spots.append(self.game_object.name)
        if self.type == "POINT":
            cell.singleton.points.append(self.game_object.name)
        self.game_object.endObject()
        self.game_object = False


class Cell:
    def __init__(self):
        print("CELL INIT")
        self.id = 0
        self.name = ""
        self.props = []
        self.entities = []
        self.lamps = []
        self.terrain = 0 #string of terrain file to load if needed
        self.blends = [] #list of string filenames that should be loaded before building cell
        self.models = [] #list of string object names that are used in this cell
        self.terrain = None
        self.navmesh = None #navmesh or obstical avoidance


    def save(self, filename): #this is for level creation and shouldn't be used at runtime
        for thing in self.props:
            for entry in thing:
                if entry.name not in self.models:
                    self.models.append( entry.name )
        for thing in self.entities:
            if thing.name not in self.models:
                self.models.append( thing.name )
        print( self.models)
        fo = open(filename, 'wb')
        pickle.dump(self,fo)

class CellManager:
    def __init__(self):
        self.cell = 0

        self.props_in_game = []
        self.lamps_in_game = []
        self.entities_in_game = []

        self.ready_to_load = 0
        self.hook = 0 #used for a tweener callback

        self.terrain = False

        # this will map out what objects are in what blends
        fo = open('./data/model_dict.data', 'rb')
        self.blend_dict = pickle.load( fo )
        fo.close()
        self.updatetime = time.time()
        #needs a list of loaded libraries
        #self.load should check libraries needed, diff that with what's loaded
        self.load_state = 0 #1 when a cell has been loaded and stays that way

        scene = bge.logic.getCurrentScene()
        self.clean_object_list = []
        for entry in scene.objects:
            self.clean_object_list.append(entry)


    def load(self, filepath):
        print("cell_manager.load()")
        self.cleanup()

        try:
            fo = open(filepath, 'rb')
            self.cell = pickle.load(fo)
            self.cell.name = filepath
            fo.close
        except:
            return("Failure to load "+filepath)

        scene = bge.logic.getCurrentScene()
        print (scene.objects)

        #set up a range of kdtrees
        self.kdtrees = []

        for pdata in self.cell.props:
            self.kdtrees.append( cell.kdNode( pdata ) )

        #tree for lamps
        self.lamp_kdtree = cell.kdNode( self.cell.lamps )
        print("---------")
        print("Loading "+filepath+"...")
        print("---------")
        self.load_libs()

        if "terrain" in self.cell.__dict__:
            if self.cell.terrain:
                self.load_terrain( self.cell.terrain)
            else:
                self.terrain = False


        tweener.singleton.add(self, "hook", 3, length=.5, callback=self.load_entities)    #using a callback so the entities are put into a built level
        tweener.singleton.add(ui.singleton.current, "color", "[*,*,*,0.0]", length=5.0, callback=ui.singleton.clear)

    def load_terrain(self, filename):
        print("cell_manager.load_terrain()")
        bge.logic.addScene("background", 0)
        scene = bge.logic.getCurrentScene()
        new = scene.addObject('outdoor_sun_shadow', "CELL_MANAGER_HOOK")

        terrain.tr_singleton = terrain.Map_Manager() #should do this in cell manager init
        terrain.tr_singleton.load(filename)
        terrain.cq_singleton = terrain.Chunk_Que()
        width = terrain.tr_singleton.map.width
        height = terrain.tr_singleton.map.height
        best = width
        if height > best: best = height
        ## 4096 7
        ## 2048 6
        ## 1024 5
        ## 512  4
        ## 256  3
        ## 128  2
        ## 64   1
        size, depth = 32, 0

        if best <= 4099:
            size = 4096
            depth = 7
        if best <= 2048:
            size = 2048
            depth = 6
        if best <= 1024:
            size = 1024
            depth = 5
        if best <= 512:
            size = 512
            depth = 4
        if best <= 256:
            size = 256
            depth = 3
        if best <= 128:
            size = 128
            depth = 2
        if best <= 64:
            size = 64
            depth = 1



        terrain.qt_singleton = terrain.Quadtree(int(size/2), [0,0], 1, max_depth=depth, scale = terrain.tr_singleton.map.scale)
        self.terrain = 1

    def load_internal(self, filepath):
            pass

    def load_libs(self):
        print("cell_manager.load_libs()")
        print("=========")

        scene = bge.logic.getCurrentScene()
        liblist = bge.logic.LibList()
        libs_to_load = []

        # Determine which libs to load
        for model in self.cell.models:
            if model in self.blend_dict:
                blend = self.blend_dict[model]
                if blend not in libs_to_load:
                    libs_to_load.append(blend)

        # Free un used libs
        for lib in liblist:
            if self.convert_back(lib) not in libs_to_load:
                bge.logic.LibFree(lib)
                print("[freed]", blend)
        scene = bge.logic.getCurrentScene() # neccessary?

        # Load terrain
        if self.cell.terrain:
            libs_to_load.append( './data/models/CHUNKS.blend' )

        # Load libs
        for blend in libs_to_load:
            if str(self.convert_lib_name(blend)) not in liblist:
                bge.logic.LibLoad(blend, "Scene", load_actions=1)
                print("[loaded] ", blend)

        print(scene.objectsInactive)
        print(bge.logic.LibList())

    def load_entities(self):
        if self.cell.name in session.savefile.entities: #we've visited this cell
            print( "!revisiting!: ", self.cell.name)
            self.cell.entities = session.savefile.entities[ self.cell.name ]
            for thing in self.cell.entities:
                if thing.packet:
                    ob = self.spawn_prop( thing.packet )
                    thing._wrap( ob )
            print( self.cell.entities )
            print(self.cell.entities[0]._data)
        else: #getting the list from a unvisited cell
            for thing in self.cell.entities:
                new_entity = EntityBase(thing)
                new_entity._wrap( self.spawn_prop(thing) )
                self.entities_in_game.append( new_entity )
            session.savefile.entities[ self.cell.name ] = self.entities_in_game
            print( self.entities_in_game )


    def convert_lib_name(self, given):
        given = given.replace("/","\\")
        given = given.replace(".\\", "./")
        return given

    def convert_back(self, given):
        given = given.replace("\\","/")
        return given

    def cleanup(self):
        print("cell_manager.cleanup()")
        if 'entity_hack' in self.__dict__: #JP forget what this is for
            self.__dict__.pop('entity_hack')
        self.props_in_game, self.lamps_in_game, self.entities_in_game = [], [], []
        self.kdtrees = []
        self.lamp_kdtree = None


        #Update the entities setup packet, and unwrap from their objects
        if self.cell and self.cell.name in session.savefile.entities:
            for entry in session.savefile.entities[ self.cell.name ]:
                if entry._data:
                    entry.packet.co = list( entry._data.position )
                    #print(dir(entry._data.orientation))
                    entry.packet.rotation = list(entry._data.orientation.to_euler())
                    entry._unwrap()



        tweener.singleton.nuke() #probably paranoia

        scene = bge.logic.getCurrentScene()
        for entry in scene.objects:
            if entry not in self.clean_object_list:
                #print("DIRTY:", entry)
                entry.endObject()

        #set up light que (in lieu of cucumber branch)
        self.spots = []
        self.points = []
        for entry in scene.objectsInactive:
            if "SPOT" in entry.name:
                self.spots.append(entry)
            if "POINT" in entry.name:
                self.points.append(entry)
        print(self.spots)
        print(self.points)

        #scene.restart()
        print("$$$$$$ CLEANED UP $$$$$")


    def spawn_prop(self, thing):
        scene = bge.logic.getCurrentScene()
        new = scene.addObject(thing.name, "CELL_MANAGER_HOOK")
        new.position = thing.co
        new.color = [1.0,1.0,1.0,0.0]
        new.localScale = thing.scale
        new.localOrientation = thing.rotation
        if 'properties' in thing.__dict__:
               for p in thing.properties:
                   new[p[0]] = p[1]

        print( "[spawned] ", new )
        tweener.singleton.add(new, "color", "[*,*,*,1.0]", 2.0)
        return new

    def spawn_lamp(self, thing): #thing is either a prop or entity
        print("spawning lamp")
        scene = bge.logic.getCurrentScene()

        #lightque things
        chosen = 'POINT'
        if thing.type == 'POINT':
            if len(self.points) > 0:
                chosen = self.points.pop(0)
        elif thing.type == 'SPOT':
            if len(self.spots) > 0:
                chosen = self.spots.pop(0)

        new = scene.addObject(chosen, "CELL_MANAGER_HOOK") #the main .blend should have light objects in another layer, the names should correspond to the type property
        new.position = thing.co
        new.localOrientation = thing.rotation
        new.distance = thing.distance
        new.energy = thing.energy

        if thing.type == 'SPOT':
            new.type = 0
            new.spotsize = thing.spot_size * 180 / 3.14
            new.spotblend = thing.spot_blend
            #new.bias = thing.spot_bias

        tweener.singleton.add(new, "color", str(thing.color), 2.0)
        return new

    def update(self):
        if self.load_state == 0:
            return
        #HACKS ENTITY HACKS HERE
        scene = bge.logic.getCurrentScene()
        position = 0
        if 'player' in scene.objects:
            position = scene.objects['player'].position
        else:
            for entry in self.cell.props:
                for prop in entry:
                    if prop.name == "player_location":
                        position = mathutils.Vector( prop.co )
        if 'explorer' in scene.objects:
            position = scene.objects['explorer'].position
        if position == 0:
            position = mathutils.Vector([0,0,0])
        if 'outdoor_sun_shadow' in scene.objects:
            scene.objects['outdoor_sun_shadow'].position = position

        # TERRAIN
        if self.terrain:
            terrain.qt_singleton.update_terrain(position)
            terrain.cq_singleton.update()

        if time.time() - self.updatetime > .5:
            self.updatetime = time.time()

            #lamps are seperated because they need a little different setup
            found_props = []
            found_lamps = []
            for i in range( len(self.kdtrees) ):
                self.kdtrees[i].getVertsInRange(position, pow(2,i)*6+i*60+1, found_props)
            #now add the lamps to this
            self.lamp_kdtree.getVertsInRange(position, 100, found_lamps)

            #loop for props
            to_remove = []
            for entry in self.props_in_game:
                if entry not in found_props:
                    #ENTITY HACKS
                    if entry.name not in ["player_location","Spaceship","helicopter",'Player', 'Vehicle', 'explorer']:
                        tweener.singleton.add(entry.game_object, "color", "[*,*,*,0.0]", 2.0, callback=entry.kill)

            for entry in found_props:
                if entry not in self.props_in_game:
                    if entry.name in scene.objectsInactive:
                        self.props_in_game.append(entry)
                        entry.game_object = self.spawn_prop(entry)
                    else:
                        print (entry.name)
                        print( "ERROR: Trying to spawn a prop that doesn't have an object loaded")

            #loop for lamps
            to_remove = []
            for entry in self.lamps_in_game:
                if entry not in found_lamps:
                    if entry.game_object:
                        tweener.singleton.add(entry.game_object, "color", "[0,0,0.0]", 2.0, callback=entry.kill)

            for entry in found_lamps:
                if entry not in self.lamps_in_game:
                    if ( entry.type == "POINT" and len(self.points) > 0 ) or ( entry.type == "SPOT" and len(self.spots) > 0 ):
                        self.lamps_in_game.append(entry)
                        entry.game_object = self.spawn_lamp(entry)

