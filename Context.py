# -*- coding: utf-8 -*-
import json
import os
import urllib
import urllib.request
import pathlib
import copy
import getpass

import StorageArea

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

        If the store area is not writable, this method will return without updating anything
        """
        if not self.store.writable:
            self.store.logger.error("C: Storage in not writable, aborting")
            return

        self.descriptor['files'][filename] = {'url': url, 'loaded': False}

         # Update stored desc
        self.writeDescriptor()

    def getFile(self, filename: str, overwrite: bool = False) -> str:
        '''
        Return the filename of the file in the storage, retrieving data from a
        remote location and storing it in the local storage if necessary. If overwrite is true
        the file if retrieved irresepctively of whether it is in local storage.

        If the store area is not writable, this method will return None
        '''
        self.store.logger.debug("C: Get file " + filename + " from storage")

        if not self.store.writable:
            self.store.logger.error("C: Storage in not writable, aborting")
            return None

        # If filename does not exist, abort
        if not filename in self.descriptor['files']:
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
        try:
            urllib.request.urlretrieve(url, outfile)
        except urllib.error.HTTPError as err:
            self.store.logger.error("C: Failed to retrieve file, " + str(err))
            return None

        entry['path'] = outfile
        entry['loaded'] = True

        # Update stored manifest
        self.writeDescriptor()

        # Return file
        return entry['path']

    def deleteFile(self, filename: str):
        '''
        Delete an item from the Context

        If the store area is not writable, this method will return without deleting the file
        '''
        self.store.logger.debug("C: Delete " + filename + " from context " + self.descriptor['name'])

        if not self.store.writable:
            self.store.logger.error("C: Storage in not writable, aborting")
            return

                # If filename does not exist, abort
        if not filename in self.descriptor['files']:
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

        If the store area is not writable, this method will return without updating anything
        '''
        self.store.logger.debug("C: Refreshing context " + self.descriptor['name'])

        if not self.store.writable:
            self.store.logger.error("C: Storage in not writable, aborting")
            return

        for filename, entry in self.descriptor['files'].items():
            # getFile() takes care of the descriptor
            self.getFile(filename)

    def purge(self):
        '''
        Deletes all files in the Cache from local storage

        If the store area is not writable, this method will return without updating anything
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