# -*- coding: utf-8 -*-
"""
    To think about: returning sessions, over-writing existing contexts
    Remove manifest at storage level and use discovery of contexts through search
"""        

import json
import os
import urllib
import uuid
import pathlib
import string
import copy

class StorageArea(object):
    """
    StorageArea containing one or more contexts. 
    """
        
    def __init__(self, path: str):
        """
        Opens a Storage area, creating the area if necessary 
        """
        self.manifest = {}
        self.context = {}
        self.storagePath = None
        self.writable = True
                
        # Convert string to a Path
        print("S: " + "Opening " + path)
        self.storagePath = pathlib.Path(path)
        
        # If directory does not exist, create it
        if not self.storagePath.exists():
            print("S: " + str(self.storagePath) + " does not exist, creating")
            self.storagePath.mkdir()
            self.storeManifest()
        
        # Check that we are ready to proceed
        if not self.storagePath.is_dir():
            raise IOError('Storage area is not a directory')

        # Flag if this is not writable
        if os.access(path, os.W_OK) is not True:
            print("S: " + str(self.storagePath) + " is not writable")
            self.writable = False

        # find existing Contexts and instantiate them Contexts
        # Open the stored manifest file
        self.openManifest()
        
    def storeManifest(self):
        """
        Write the manifest for the StorageArea
        """
        
        # Can we have this as an decorator?
        p = str(self.storagePath / 'storage.json')
        
        print("S: Storing manifest in " + p)
        with open(p, 'w') as handle:
            handle.write(json.dumps(self.manifest, indent=4))
            handle.close()
    
    def openManifest(self):
        """
        Open the manifest for the StorageArea
        """
        
        p = str(self.storagePath / 'storage.json')
        
        print("S: Loading manifest from " + p)
        with open(p, 'r') as handle:
            self.manifest = json.load(handle)
            handle.close()
            
    def addContext(self, name: str):
        """
        Add a context
        """
        
        print("S: Adding context " + name)
              
        # Create a Path object     
        saneName = format_filename(name)
        dirName = pathlib.Path(saneName)
        
        # Create the directory
        print("S: Creating directory " + str())
        dirPath = self.storagePath / saneName
        dirPath.mkdir();

        files = {}

        # Create a context
        entry = {'path': str(dirName), 'files': files}

        # Add to the dictionary        
        self.manifest[name] = entry
        self.context[name] = Context(name, files, self)
      
        # Update manifest
        self.storeManifest()
        
        return self.context[name]

    def deleteContext(self, name: str):
        """
        Delete a context; removing underlying files
        """

        print("S: Deleting context " + name)

        # Get the relevant context info
        entry = self.manifest[name]
        
        # Eliminate data files
        print("S: Purge context " + name)
        self.context[name].purgeContext()
        
        # Create an object
        p = self.storagePath / entry['path']
        
        # Delete the directory
        print("S: Deleting directory " + str(p))
        p.rmdir()

        # Remove the context from the list        
        del self.manifest[name]

        # Update manifest
        self.storeManifest()
   
    def addFileFromUrl(self, url: str, context: str, name: str):
        """
        Create a file from the contents of a URL
        """
                
        # Get the relevant context info
        entry = self.manifest[context]
        
        # Determine filename for output file 
        path = str(self.storagePath / entry['path'] / name)
        
        # Retrieve data into file
        print("S: Retrieving file " + str(path) + " from " + url)
        urllib.request.urlretrieve(url, path)

        # Give the path back
        return path

    def deleteFile(self, path: str):
        """
        Delete a file from storage
        """
        print("S: Deleting file " + str(path))
        if os.path.isfile(path):
            os.remove(path)

class Context(object):
    """
    Context - a collection of files identified by their file names. The source
    of these data is assumed to be accessible via HTTP
    
    To think about: returning sessions, over-writing existing contexts
    Remove manifest at storage level and use discovery of contexts through search
    """

    def __init__(self, name: str, files: dict, store: StorageArea):
        self.files = files
        self.name = name
        self.store = store
        
    def add(self, url: str, filename: str):
        """
        Add an item to the Context. It does not load it into storage.
        """
        if not self.store.writable:
            print("C: Storage in not writable, aborting")
            return

        dict = {'url': url, 'loaded': False}
        self.files[filename] = dict

         # Update stored manifest
        self.store.storeManifest()
        
    def get(self, filename: str, overwrite: bool = False):
        """
        Return the filename of the file in the storage, retrieving data from a 
        remote location and storing it in the local storage if necessary. If overwrite is true
        the file if retrieved irresepctively of whether it is in local storage
        """
        print("C: Get file " + filename + " from storage")

        if not self.store.writable:
            print("C: Storage in not writable, aborting")
            return None

        # If filename does not exist, abort
        if self.files[filename] is None:
            print("C: File is not known in context, aborting")
            return None

        entry = self.files[filename]
        if 'path' in entry:
            path = entry['path']
            # If we are not in overwrite mode and the file already exists in the cache, return file
            if overwrite is False and entry['loaded'] is True:
                print("C: Found existing file " + path)
                return path
        
        # Either the file is not loaded, or we insist on retrieving it
            
        # Get URL for filename
        url = entry['url']

        # Retrieve the file and update records
        entry['path'] = self.store.addFileFromUrl(url, self.name, filename)
        entry['loaded'] = True
        
        # Update stored manifest
        self.store.storeManifest()
        
        # Return file 
        return entry['path']

    def delete(self, filename: str):
        """
        Delete an item (including file) from the Context
        """
        print("C: Delete " + filename + " from context " + self.name)
        
        if not self.store.writable:
            print("C: Storage in not writable, aborting")
            return
        
        entry = self.files[filename]
        self.store.deleteFile(entry['path'])
        
        entry['loaded'] = False
        
        # Update dictionary
        del self.files[filename]
        
        # Update manifest
        self.store.storeManifest()

    def refreshContext(self):
        """
        Retrieves retrieves any items in the Cache which are not in the storage
        """
        print("C: Refreshing context " + self.name)

        if not self.store.writable:
            print("C: Storage in not writable, aborting")
            return

        for filename, entry in iter(self.files.items()):
            self.get(filename)

        # Update stored manifest
        self.store.storeManifest()
     
    def purgeContext(self):
        """
        Deletes all files in the Cache from local storage
        """
        print("C: Purging context " + self.name)

        if not self.store.writable:
            print("C: Storage in not writable, aborting")
            return

        for filename, entry in self.files.items(): 
            self.purgeFile(filename)

        # Update stored manifest
        self.store.storeManifest()
         
    def purgeFile(self, filename: str):
        """
        Delete a file in the Cache from local storage
        """
        print("C: Purging file " + filename + " from context")

        if not self.store.writable:
            print("C: Storage in not writable, aborting")
            return

        # If filename does not exist, abort
        if self.files[filename] is None:
            print("C: File is not known in Context, aborting")
            return

        entry = self.files[filename]
        if entry['loaded'] is True:
            print("C: File is loaded")
            self.store.deleteFile(entry['path'])
            entry['loaded'] = False
        else:
            print("C: File is not loaded")

        # Update stored manifest
        self.store.storeManifest()

    def exportContext(self, path: str):     
        """
        Dump Context metadata as a file
        """
        fileExp = copy.deepcopy(self.files)
        for filename, entry in fileExp.items():
            entry['loaded'] = False
            del entry['path']
        
        print("C: Storing context in " + path)
        with open(path, 'w') as handle:
            handle.write(json.dumps(fileExp, indent=4))
            handle.close()

    def importContext(self, file: str):
        """
        Populate the Context metadata from a file. The files will not be retrieved
        """
        print("C: Loading conext from " + file)
        with open(file, 'r') as handle:
            self.files = json.load(handle)
            handle.close()

    def importContextFromUrl(self, url: str):
        """
        Populate the Context metadata from a file. The files will not be retrieved
        """
        print("C: Loading context from " + url)
        
        data = urllib.request.urlopen(url)
        self.files = json.load(data)

def format_filename(s):
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in s if c in valid_chars)
    filename = filename.replace(' ','_')
    return filename

def getUid():
    return str(uuid.uuid4())[:8]

if __name__ == "__main__":

    home = pathlib.Path.home()
    
    S = StorageArea(str(home / 'EuclidCache'))
    testContext = getUid()
    C = S.addContext(testContext)
    C.add("http://vospace.esac.esa.int/vospace/sh/eb9834b594e8da89111147899d15c26dd5ecf9?dl=1","foo.pdf")
    C.get("foo.pdf")
    C.exportContext("foo.json")
    C.purgeFile("foo.pdf")
    S.deleteContext(testContext)
    
    nextContext = getUid()
    C = S.addContext(nextContext)
    C.importContext("foo.json")
    C.refreshContext()

    next2Context = getUid()
    C = S.addContext(next2Context)
    C.importContextFromUrl("http://vospace.esac.esa.int/vospace/sh/bfedf6f4f221ea34e880c2473da6a4d1d67b8ea1?dl=1")
    C.refreshContext()
