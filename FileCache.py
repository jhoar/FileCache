# -*- coding: utf-8 -*-
'''

    To do/think about: 
    - returning/conflicting sessions, 
    - Multiple openings of the same StorageArea
    - locking contexts
    - many more tests
'''        

import json
import os
import urllib
import urllib.request
import pathlib
import string
import copy
import getpass
import logging

class StorageArea(object):
    '''
    StorageArea containing one or more contexts. 
    '''
        
    def __init__(self, path: str):
        '''
        Opens a Storage area, creating the area if necessary 
        '''        
        self.contexts = {}
        self.storagePath = None
        self.writable = True
        
        # set up logger
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger('FileCache')
        self.logger.setLevel(logging.INFO)
                
        # Convert string to a Path
        self.logger.debug("S: " + "Opening " + path)
        self.storagePath = pathlib.Path(path)
        
        # If directory does not exist, create it
        if not self.storagePath.exists():
            self.logger.info("S: " + str(self.storagePath) + " does not exist, creating")
            self.storagePath.mkdir()    
        
        # Check that we are ready to proceed
        if not self.storagePath.is_dir():
            raise IOError('Storage area is not a directory')

        # Flag if this is not writable
        if os.access(path, os.W_OK) is not True:
            self.logger.debug("S: " + str(self.storagePath) + " is not writable")
            self.writable = False

        # find existing Contexts and instantiate them Contexts
        # Get all directories
        for subDir in self.storagePath.iterdir():
            if subDir.is_dir():
                desc = subDir / "desc.json"
                if desc.is_file():
                    self.logger.debug("S: Found Context in " + str(subDir.stem))
                    ctxt = self.addContext(str(subDir.stem), False)
                    ctxt.load(str(desc))

    def addContext(self, name: str, createDir: bool = True):
        '''
        Add a context
        '''
        
        self.logger.debug("S: Adding context " + name)
        
        if(name in self.contexts):
            self.logger.debug("S: Context " + name + " already loaded")
            return self.contexts[name]
        
        # Create a Path object     
        saneName = format_filename(name)
        
        # Create the directory
        dirPath = self.storagePath / saneName
        if createDir is True:
            if not dirPath.exists():
                dirPath.mkdir();
                
        # Add to the dictionary        
        self.contexts[name] = Context(name, dirPath, self)
              
        return self.contexts[name]


    def deleteContext(self, name: str):
        '''
        Delete a context; removing underlying files
        '''

        self.logger.debug("S: Deleting context " + name)

        # Eliminate data files and directory
        self.logger.debug("S: Purge context " + name)
        self.contexts[name].purge()
        self.contexts[name].deleteDescriptor()
        self.contexts[name].path.rmdir()
                
        # Remove the context from the list        
        del self.contexts[name]
   
    def listContexts(self):
        '''
        Output the available Contexts
        '''
        for name, ctxt in self.contexts.items():
            print(name + " " + str(ctxt.path) + " " + ctxt.descriptor['author'])
            ctxt.listFiles()
    
class Context(object):
    '''
    Context - a collection of files identified by their file names. The source
    of these data is assumed to be accessible via HTTP
    '''

    def __init__(self, name: str, path: pathlib.Path, store: StorageArea):
        self.path = path
        self.store = store
        self.descriptor = {'name': name, 'author': getpass.getuser(), 'files': {}}

    def addFile(self, url: str, filename: str):
        """
        Add an item to the Context. It does not load it into storage.
        """
        if not self.store.writable:
            self.store.logger.error("C: Storage in not writable, aborting")
            return

        self.descriptor['files'][filename] = {'url': url, 'loaded': False}

         # Update stored desc
        self.writeDescriptor()
        
    def getFile(self, filename: str, overwrite: bool = False):
        '''
        Return the filename of the file in the storage, retrieving data from a 
        remote location and storing it in the local storage if necessary. If overwrite is true
        the file if retrieved irresepctively of whether it is in local storage
        '''
        self.store.logger.debug("C: Get file " + filename + " from storage")

        if not self.store.writable:
            self.store.logger.error("C: Storage in not writable, aborting")
            return None

        # If filename does not exist, abort
        if self.descriptor['files'][filename] is None:
            self.store.logger.error("C: File is not known in context, aborting")
            return None

        entry = self.descriptor['files'][filename]
        if 'path' in entry:
            path = entry['path']
            # If we are not in overwrite mode and the file already exists in the cache, return file
            if overwrite is False and entry['loaded'] is True:
                self.store.logger.debug("C: Found existing file " + path)
                return path
        
        # Either the file is not loaded, or we insist on retrieving it
            
        # Get URL for filename
        url = entry['url']

        # Retrieve the file and update records
        # Determine filename for output file 
        outfile = str(self.path / filename)
        
        # Retrieve data into file
        self.store.logger.info("C: Creating file " + str(outfile) + " from " + url)
        urllib.request.urlretrieve(url, outfile)

        entry['path'] = outfile
        entry['loaded'] = True
        
        # Update stored manifest
        self.writeDescriptor()
        
        # Return file 
        return entry['path']

    def deleteFile(self, filename: str):
        '''
        Delete an item from the Context
        '''
        self.store.logger.debug("C: Delete " + filename + " from context " + self.descriptor['name'])
        
        if not self.store.writable:
            self.store.logger.error("C: Storage in not writable, aborting")
            return
        
                # If filename does not exist, abort
        if self.descriptor['files'][filename] is None:
            self.store.logger.error("C: File is not known in context, aborting")
            return

        if 'path' in self.descriptor['files'][filename]:
            path = self.descriptor['files'][filename]['path']
            self.store.logger.debug("C: Deleting file " + path)
            if os.path.isfile(path):
                os.remove(path)
                
        # Update dictionary
        del self.descriptor['files'][filename]
        
        # Write descriptor
        self.writeDescriptor()

    def refresh(self):
        '''
        Retrieves retrieves any items in the Cache which are not in the storage
        '''
        self.store.logger.debug("C: Refreshing context " + self.descriptor['name'])

        if not self.store.writable:
            self.store.logger.error("C: Storage in not writable, aborting")
            return

        for filename, entry in self.descriptor['files'].items():
            self.getFile(filename)

        # get() takes care of the descriptor
     
    def purge(self):
        '''
        Deletes all files in the Cache from local storage
        '''
        self.store.logger.debug("C: Purging context " + self.descriptor['name'])

        if not self.store.writable:
            self.store.logger.error("C: Storage in not writable, aborting")
            return

        for filename, entry in self.descriptor['files'].items(): 
            if 'path' in entry:
                path = entry['path']
                self.store.logger.debug("C: Deleting file " + path)
                if os.path.isfile(path):
                    os.remove(path)
                
        # Update dictionary
        self.descriptor['files'].clear()
        
        # Write descriptor
        self.writeDescriptor()
         
    def writeDescriptor(self):     
        '''
        Dump Context metadata as a file
        '''        
        desc = str(self.path / "desc.json") 
        self.store.logger.debug("C: Writing descriptor in " + desc)
        with open(desc , 'w') as handle:
            handle.write(json.dumps(self.descriptor, indent=4))
            handle.close()

    def deleteDescriptor(self):     
        '''
        Delete Context metadata file
        '''        
        desc = self.path / "desc.json"
        self.store.logger.debug("C: Deleting descriptor " + str(desc))
        desc.unlink()

    def export(self, path: str):     
        '''
        Dump Context metadata as a file
        '''
        desc = copy.deepcopy(self.descriptor)
        for filename, entry in desc['files'].items():
            entry['loaded'] = False
            if 'path' in entry:
                del entry['path']
        
        self.store.logger.debug("C: Exporting context in " + path)
        with open(path, 'w') as handle:
            handle.write(json.dumps(desc, indent=4))
            handle.close()

    def load(self, location: str, merge: bool = False):
        '''
        Populate the Context metadata; determining from a file or URL. 
        
        The files will not be retrieved
        
        If merge is True, the existing list of files in the context will be merged with
        the new files. If False, the new list will replace the existing list.
        The existing context name and author will always be preserved         
        '''
        
        if urllib.parse.urlparse(location).scheme in ('http', 'https',):
            self.store.logger.debug("C: Populating context from URL " + location)
            data = urllib.request.urlopen(location)
            newDesc = json.load(data)
        else:
            self.store.logger.debug("C: Populating context from file: " + location)
            with open(location, 'r') as handle:
                newDesc = json.load(handle)
                handle.close()

        # Remove existing loaded status or paths
        for filename, entry in newDesc['files'].items():
            entry['loaded'] = False
            if 'path' in entry:
                del entry['path']

        if merge is True:
            self.descriptor['files'].update(newDesc['files'])
        else:
            self.descriptor['author'] = newDesc['author']
            self.descriptor['files'] = copy.deepcopy(newDesc['files'])
            
        self.writeDescriptor()
        
    def listFiles(self):
        '''
        List the files currently registered in the context
        '''
        for name, files in self.descriptor['files'].items():
            if files['loaded'] is True:
                print("\t" + name + " " + files['url'] + " " + files['path'])
            else:
                print("\t" + name + " " + files['url'])
                    
class SimpleCache(object):
    '''
    Simple interface based around one context located a directory
    EuclidCache located in the user's home directory. This is focused 
    on loading resources as simply as possibly, e.g.:
    
        S = FileCache.SimpleCache()
        S.load("http://vospace.esac.esa.int/vospace/sh/4807f490cec42f15d1574442881ccb1f1275bd?dl=1")
        S.get("foo.pdf")
        ...
        S.destroy() # Clean up
    
    
    '''
    def __init__(self):
        self.home = pathlib.Path.home()
        self.store = StorageArea(str(self.home / 'EuclidCache'))
        self.context = self.store.addContext('files', True)
        
    def load(self, url: str):
        self.context.load(url, True)
        self.context.refresh()
    
    def get(self, file: str):
        return self.context.getFile(file)

    def files(self):
        return self.context.listFiles()
    
    def destroy(self):
        self.context.purge()
        self.store.deleteContext('files')

def format_filename(s):
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in s if c in valid_chars)
    filename = filename.replace(' ','_')
    return filename

