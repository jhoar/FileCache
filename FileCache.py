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

from StorageArea import StorageArea

class SimpleCache(object):
    '''
    Simple interface based around one context located a directory
    EuclidCache located in the user's home directory. This is focused
    on loading resources as simply as possibly, e.g.:

    import FileCache
    from astropy.io import fits

    # Store files in $HOME/EuclidCache/files/ or Windows equivalent
    S = FileCache.SimpleCache()

    # Load in the descriptor containing the contents of a bundle
    S.load("http://vospace.esac.esa.int/vospace/sh/5e558f8785e775a165124178f045ba7c52e49552?dl=1")

    # List the content
    S.files()

    # S.get() retrieves the file if necessary and returns the path of the file locally
    fits_image_filename = fits.open(S.get("ick906030_prev.fits"))

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

