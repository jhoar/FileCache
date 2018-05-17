# -*- coding: utf-8 -*-
"""
Created on Fri May  4 10:00:42 2018

@author: jhoar
"""

import unittest
import pathlib
import uuid
import FileCache

class TestStringMethods(unittest.TestCase):

    def setUp(self):
        self.home = pathlib.Path.home()

    def test_initEmpty(self):
        pass

    def test_initNotEmpty(self):
        pass

    def test_addContext(self):
        pass

    def test_addContextDup(self):
        pass

    def test_addContextDirExist(self):
        pass

    def test_addContextNotWritable(self):
        pass

    def test_delContext(self):
        pass

    def test_delContextNoExist(self):
        pass

    def test_delContextNotWritable(self):
        pass

    def test_listContext(self):
        pass

    def test_purge(self):
        pass

    def test_purgeNotWritable(self):
        pass

    def test_addFile(self):
        pass

    def test_addFileNotWritable(self):
        pass

    def test_getFile(self):
        pass

    def test_getFileNotWritable(self):
        pass

    def test_getFileNotExists(self):
        pass

    def test_getFileNoAccess(self):
        pass

    def test_deleteFile(self):
        pass

    def test_deleteFileNoExist(self):
        pass

    def test_deleteFileNotWritable(self):
        pass

    def test_testSimpleCache(self):
        S = FileCache.SimpleCache()
        S.load("http://vospace.esac.esa.int/vospace/sh/4807f490cec42f15d1574442881ccb1f1275bd?dl=1")
        S.get("foo.pdf")
    
    def test_test1(self):
        S = FileCache.StorageArea(str(self.home / 'EuclidCache'))
        testContext = getUid()
        C = S.addContext(testContext)
        C.addFile("http://vospace.esac.esa.int/vospace/sh/eb9834b594e8da89111147899d15c26dd5ecf9?dl=1","foo.pdf")
        C.getFile("foo.pdf")
        C.export("export.json")
        C.deleteFile("foo.pdf")
        S.deleteContext(testContext)
    
    def test_test2(self):
        nextContext = getUid()
        S = FileCache.StorageArea(str(self.home / 'EuclidCache'))
        C = S.addContext(nextContext)
        C.load("export.json")
        C.refresh()

    def test_test3(self):
        next2Context = getUid()
        S = FileCache.StorageArea(str(self.home / 'EuclidCache'))
        C = S.addContext(next2Context)
        C.load("http://vospace.esac.esa.int/vospace/sh/4807f490cec42f15d1574442881ccb1f1275bd?dl=1")
        C.refresh()

    def test_test4(self):
        next3Context = getUid()
        S = FileCache.StorageArea(str(self.home / 'EuclidCache'))
        C = S.addContext(next3Context) # TODO Should check for existing dirs
        C.addFile("http://vospace.esac.esa.int/vospace/sh/66ee2fc9964193fcc2984e35a25bdee14057f9?dl=1","ick906030_prev.fits")
        C.export("export1.json")
        C.addFile("http://vospace.esac.esa.int/vospace/sp/e09e212133c2c61093431c4eb13ed16e7e31bb36?dl=2","1525190698647O-result.vot")
        C.export("export2.json")
        S.deleteContext(next3Context) # TODO Check for context

    
    def test_test5(self):
        S = FileCache.StorageArea(str(self.home / 'EuclidCache'))
        S.listContexts()
    
    
    
'''
      self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)
'''

def getUid():
    return str(uuid.uuid4())[:8]

if __name__ == '__main__':
    unittest.main()