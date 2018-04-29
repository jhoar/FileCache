# -*- coding: utf-8 -*-
"""

    To do/think about: 
    - discovery of contexts on StorageArea open
    - returning sessions, 
    - over-writing existing contexts
    - locking contexts
    - many more tests
"""        

import json
import os
import urllib
import uuid
import pathlib
import string
import copy
import getpass

class StorageArea(object):
    """
    StorageArea containing one or more contexts. 
    """
        
    def __init__(self, path: str):
        """
        Opens a Storage area, creating the area if necessary 
        """
        self.contexts = {}
        self.storagePath = None
        self.writable = True
                
        # Convert string to a Path
        print("S: " + "Opening " + path)
        self.storagePath = pathlib.Path(path)
        
        # If directory does not exist, create it
        if not self.storagePath.exists():
            print("S: " + str(self.storagePath) + " does not exist, creating")
            self.storagePath.mkdir()    
        
        # Check that we are ready to proceed
        if not self.storagePath.is_dir():
            raise IOError('Storage area is not a directory')

        # Flag if this is not writable
        if os.access(path, os.W_OK) is not True:
            print("S: " + str(self.storagePath) + " is not writable")
            self.writable = False

        # find existing Contexts and instantiate them Contexts
        # Get all directories
        for subDir in self.storagePath.iterdir():
            if subDir.is_dir():
                desc = subDir / "desc.json"
                if desc.is_file():
                    print("S: Found Context in " + str(subDir))
                    # TODO need dir name, not whole path
                    ctxt = self.addContext(str(subDir.stem), False)
                    ctxt.populateContext(str(desc))

    def addContext(self, name: str, createDir: bool = True):
        """
        Add a context
        """
        
        print("S: Adding context " + name)
              
        # Create a Path object     
        saneName = format_filename(name)
        
        # Create the directory
        dirPath = self.storagePath / saneName
        if createDir is True:
            print("S: Creating directory " + str(dirPath))
            dirPath.mkdir();

        # Add to the dictionary        
        self.contexts[name] = Context(name, dirPath, self)
              
        return self.contexts[name]

    def deleteContext(self, name: str):
        """
        Delete a context; removing underlying files
        """

        print("S: Deleting context " + name)

        # Eliminate data files and directory
        print("S: Purge context " + name)
        self.contexts[name].purgeContext()
        self.contexts[name].deleteDescriptor()
        self.contexts[name].path.rmdir()
                
        # Remove the context from the list        
        del self.contexts[name]
   
    def listContexts(self):
        '''
        Output the available Contexts
        '''
        pass
    
class Context(object):
    """
    Context - a collection of files identified by their file names. The source
    of these data is assumed to be accessible via HTTP
    """

    def __init__(self, name: str, path: pathlib.Path, store: StorageArea):
        self.path = path
        self.name = name
        self.store = store
        self.author = getpass.getuser()
        self.descriptor = {'name': self.name, 'author': self.author, 'files': {}}

    def add(self, url: str, filename: str):
        """
        Add an item to the Context. It does not load it into storage.
        """
        if not self.store.writable:
            print("C: Storage in not writable, aborting")
            return

        self.descriptor['files'][filename] = {'url': url, 'loaded': False}

         # Update stored desc
        self.writeDescriptor()
        
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
        if self.descriptor['files'][filename] is None:
            print("C: File is not known in context, aborting")
            return None

        entry = self.descriptor['files'][filename]
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
        # Determine filename for output file 
        outfile = str(self.path / filename)
        
        # Retrieve data into file
        print("C: Retrieving file " + str(outfile) + " from " + url)
        urllib.request.urlretrieve(url, outfile)

        entry['path'] = outfile
        entry['loaded'] = True
        
        # Update stored manifest
        self.writeDescriptor()
        
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
        
                # If filename does not exist, abort
        if self.descriptor['files'][filename] is None:
            print("C: File is not known in context, aborting")
            return
        
        path = self.descriptor['files'][filename]['path']
        print("C: Deleting file " + path)
        if os.path.isfile(path):
            os.remove(path)

        # Update dictionary
        del self.descriptor['files'][filename]
        
        # Write descriptor
        self.writeDescriptor()

    def refreshContext(self):
        """
        Retrieves retrieves any items in the Cache which are not in the storage
        """
        print("C: Refreshing context " + self.name)

        if not self.store.writable:
            print("C: Storage in not writable, aborting")
            return

        for filename, entry in self.descriptor['files'].items():
            self.get(filename)

        # Update stored manifest
        self.writeDescriptor()
     
    def purgeContext(self):
        """
        Deletes all files in the Cache from local storage
        """
        print("C: Purging context " + self.name)

        if not self.store.writable:
            print("C: Storage in not writable, aborting")
            return

        for filename, entry in self.descriptor['files'].items(): 
            self.purgeFile(filename)

        # Update stored manifest
        self.writeDescriptor()
         
    def purgeFile(self, filename: str):
        """
        Delete a file in the Cache from local storage
        """
        print("C: Purging file " + filename + " from context")

        if not self.store.writable:
            print("C: Storage in not writable, aborting")
            return

        # If filename does not exist, abort
        if self.descriptor['files'][filename] is None:
            print("C: File is not known in Context, aborting")
            return

        entry = self.descriptor['files'][filename]
        if entry['loaded'] is True:
            print("C: File is loaded, deleting file " + entry['path'])
            os.remove(entry['path'])
            entry['loaded'] = False
        else:
            print("C: File is not loaded")

        # Update stored manifest
        self.writeDescriptor()

    def writeDescriptor(self):     
        """
        Dump Context metadata as a file
        """        
        desc = str(self.path / "desc.json") 
        print("C: Writing descriptor in " + desc)
        with open(desc , 'w') as handle:
            handle.write(json.dumps(self.descriptor, indent=4))
            handle.close()


    def deleteDescriptor(self):     
        """
        Dump Context metadata as a file
        """        
        desc = self.path / "desc.json"
        print("C: Deleting descriptor " + str(desc))
        desc.unlink()

    def exportContext(self, path: str):     
        """
        Dump Context metadata as a file
        """
        desc = copy.deepcopy(self.descriptor)
        for filename, entry in desc['files'].items():
            entry['loaded'] = False
            del entry['path']
        
        print("C: Exporting context in " + path)
        with open(path, 'w') as handle:
            handle.write(json.dumps(desc, indent=4))
            handle.close()

    def populateContext(self, file: str):
        """
        Populate the Context metadata from a file. The files will not be retrieved
        - TODO what to do with existing content, merge or overwrite?
        """
        print("C: Populating context from file: " + file)
        with open(file, 'r') as handle:
            self.descriptor = json.load(handle)
            handle.close()
            
        self.writeDescriptor()

    def populateContextFromUrl(self, url: str):
        """
        Populate the Context metadata from a file. The files will not be retrieved
        - TODO what to do with existing content, merge or overwrite?
        - TODO Can we merge this with populateContext(file)?
        """
        print("C: Populating context from URL " + url)
        
        data = urllib.request.urlopen(url)
        self.descriptor = json.load(data)
        self.writeDescriptor()

def format_filename(s):
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in s if c in valid_chars)
    filename = filename.replace(' ','_')
    return filename

def getUid():
    return str(uuid.uuid4())[:8]

if __name__ == "__main__":

    home = pathlib.Path.home()
    
    print("Test 1")
    S = StorageArea(str(home / 'EuclidCache'))
    testContext = getUid()
    C = S.addContext(testContext)
    C.add("http://vospace.esac.esa.int/vospace/sh/eb9834b594e8da89111147899d15c26dd5ecf9?dl=1","foo.pdf")
    C.get("foo.pdf")
    C.exportContext("export.json")
    C.purgeFile("foo.pdf")
    S.deleteContext(testContext)
    
    print("Test 2")
    nextContext = getUid()
    C = S.addContext(nextContext)
    C.populateContext("export.json")
    C.refreshContext()

    print("Test 3")
    next2Context = getUid()
    C = S.addContext(next2Context)
    C.populateContextFromUrl("http://vospace.esac.esa.int/vospace/sh/4807f490cec42f15d1574442881ccb1f1275bd?dl=1")
    C.refreshContext()
