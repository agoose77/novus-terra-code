import pickle
import os

class Savefile:
    def __init__(self, folder):
        
        self.folder = folder
        self.world_files = []
        self.player_file = None
        self.quest_manager_file = None
        self.quest_files = None
        
        for filename in os.listdir(folder):
            if filename.endswith('.world'):
                self.world_files.append(filename)
            elif filename.endswith('.quest'):
                if filename.startswith('quest_manager'):
                    self.quest_manager_file = filename
                else:
                    self.quest_files.append(filename)
            elif filename.endswith('.player'):
                self.player_file = filename
    
    def pickle_file(self, data):
        file = open(self.folder + data['filename'], 'wb')
        pickle.dump(file, data)
        file.close()
            
    def load_file(self, filename):
        file = open(self.folder + filename, 'rb')
        data = pickle.load(file)
        file.close()
        
        return data