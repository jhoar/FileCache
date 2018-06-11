# -*- coding: utf-8 -*-
'''

    To do/think about:
    - returning/conflicting sessions,
    - Multiple openings of the same StorageArea
    - locking contexts
    - test getFile('file://')
    - Revise writable (use StorageArea.writable, vs in-line check with os.access())
    - more tests
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
import shutil

from Context import Context

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
        logging.basicConfig()
        self.logger = logging.getLogger('FileCache')
        self.logger.setLevel(logging.ERROR)

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
        self.logger.debug("S: Checking subdirectories")
        for subDir in self.storagePath.iterdir():
            if subDir.is_dir():
                self.logger.debug("S: Found directory in " + str(subDir.stem))
                ctxt = self.addContext(str(subDir.stem), False)
                desc = subDir / "desc.json"
                if desc.is_file():
                    self.logger.debug("S: Load context")
                    ctxt.load(str(desc))

    def addContext(self, name: str, createDir: bool = True) -> Context:
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

        # Flag if this is not writable
        if not self.writable:
            self.logger.debug("S: " + str(dirPath) + " is not writable")

        if createDir is True:
            if not dirPath.exists():
                dirPath.mkdir()
            else:
                self.logger.error("S: Context directory already exists")
                # TODO Should we fail here?

        # Add to the dictionary
        self.contexts[name] = Context(name, dirPath, self)

        return self.contexts[name]


    def deleteContext(self, name: str):
        '''
        Delete a context; removing underlying files
        '''

        self.logger.debug("S: Deleting context " + name)

        if not name in self.contexts:
            self.logger.error("S: Context " + name + " does not exist")
            return

        ctxt = self.contexts[name]

        # Flag if this is not writable
        if not self.writable:
            self.logger.debug("S: " + str(ctxt.path) + " is not writable")
            return

        # Eliminate data files and directory
        self.logger.debug("S: Purge context " + name)
        ctxt.purge()
        ctxt.deleteDescriptor()
        self.logger.debug("S: Deleting context directory " + name)
        shutil.rmtree(str(ctxt.path))

        # Remove the context from the list
        del self.contexts[name]

    def listContexts(self):
        '''
        Output the available Contexts
        '''
        for name, ctxt in self.contexts.items():
            print(name + " " + str(ctxt.path) + " " + ctxt.descriptor['author'])
            ctxt.listFiles()

def format_filename(s):
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in s if c in valid_chars)
    filename = filename.replace(' ','_')
    return filename
