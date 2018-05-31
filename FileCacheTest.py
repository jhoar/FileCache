# -*- coding: utf-8 -*-
"""
Created on Fri May  4 10:00:42 2018

@author: jhoar
"""

import unittest
import pathlib
import uuid
import FileCache
import inspect
import shutil
import os
import stat

class TestMethods(unittest.TestCase):

    def setUp(self):
        self.home = pathlib.Path.home()

    def test_initEmpty(self):
        print('test_initEmpty')
        path = self.home / getUid()
        S = FileCache.StorageArea(str(path))
        self.assertTrue(S.storagePath.exists())
        shutil.rmtree(str(path))

    def test_initNotEmpty(self):
        print('test_initNotEmpty')
        # Setup
        area = getUid()
        path = self.home / area
        S1 = FileCache.StorageArea(str(path))
        ctxt = getUid()
        S1.addContext(ctxt)

        # Test
        S2 = FileCache.StorageArea(str(path))
        k = ctxt in S2.contexts
        print(k)
        self.assertTrue(k)
        shutil.rmtree(str(path))

    def test_addContext(self):
        print('test_addContext')
        area = getUid()
        path = self.home / area
        S1 = FileCache.StorageArea(str(path))
        ctxt = getUid()
        S1.addContext(ctxt)
        cDir = S1.storagePath / ctxt
        self.assertTrue(cDir.exists())
        shutil.rmtree(str(path))

    def test_addContextDup(self):
        print('test_addContextDup')
        area = getUid()
        path = self.home / area
        S1 = FileCache.StorageArea(str(path))
        ctxt = getUid()
        S1.addContext(ctxt)
        S1.addContext(ctxt)
        shutil.rmtree(str(path))

    def test_addContextDirExist(self):
        print('test_addContextDirExist')
        area = getUid()
        path = self.home / area
        S1 = FileCache.StorageArea(str(path))
        ctxt = getUid()
        dupDir = path / ctxt
        dupDir.mkdir()
        S1.addContext(ctxt, True)
        shutil.rmtree(str(path))

    def test_addContextNotWritable(self):
        print('test_addContextNotWritable')
        area = getUid()
        path = self.home / area
        S1 = FileCache.StorageArea(str(path))
        os.chmod(str(path), 0o0077)
        ctxt = getUid()
        S1.addContext(ctxt)
        os.chmod(str(path), 0o0777)
        shutil.rmtree(str(path))

    def test_delContext(self):
        print('test_delContext')
        area = getUid()
        path = self.home / area
        S1 = FileCache.StorageArea(str(path))
        ctxt = getUid()
        S1.addContext(ctxt)
        S1.deleteContext(ctxt)
        shutil.rmtree(str(path))

    def test_delContextNoExist(self):
        print('test_delContextNoExist')
        area = getUid()
        path = self.home / area
        S1 = FileCache.StorageArea(str(path))
        ctxt = getUid()
        S1.addContext(ctxt)
        S1.deleteContext('foo')
        shutil.rmtree(str(path))

    def test_delContextNotWritable(self):
        print('test_delContextNotWritable')
        area = getUid()
        path = self.home / area
        S1 = FileCache.StorageArea(str(path))
        ctxt = getUid()
        S1.addContext(ctxt)
        S1.writable = False
        S1.deleteContext(ctxt)
        shutil.rmtree(str(path))

    def test_listContexts(self):
        print('test_listContexts')
        area = getUid()
        path = self.home / area
        S1 = FileCache.StorageArea(str(path))
        ctxt = getUid()
        S1.addContext(ctxt)
        S1.listContexts()
        shutil.rmtree(str(path))

    def test_purge(self):
        print('test_purge')
        area = getUid()
        path = self.home / area
        S1 = FileCache.StorageArea(str(path))
        ctxt = getUid()
        C1 = S1.addContext(ctxt)
        C1.addFile("http://vospace.esac.esa.int/vospace/sh/eb9834b594e8da89111147899d15c26dd5ecf9?dl=1","foo.pdf")
        C1.getFile("foo.pdf")
        C1.purge()

    def test_purgeNotWritable(self):
        print('test_purgeNotWritable')
        area = getUid()
        path = self.home / area
        S1 = FileCache.StorageArea(str(path))
        ctxt = getUid()
        C1 = S1.addContext(ctxt)
        C1.addFile("http://vospace.esac.esa.int/vospace/sh/eb9834b594e8da89111147899d15c26dd5ecf9?dl=1","foo.pdf")
        C1.getFile("foo.pdf")
        S1.writable = False
        C1.purge()

    def test_addFile(self):
        print('test_addFile')
        area = getUid()
        path = self.home / area
        S1 = FileCache.StorageArea(str(path))
        ctxt = getUid()
        C1 = S1.addContext(ctxt)
        C1.addFile("http://vospace.esac.esa.int/vospace/sh/eb9834b594e8da89111147899d15c26dd5ecf9?dl=1","foo.pdf")

    def test_addFileNotWritable(self):
        print('test_addFileNotWritable')
        area = getUid()
        path = self.home / area
        S1 = FileCache.StorageArea(str(path))
        ctxt = getUid()
        C1 = S1.addContext(ctxt)
        S1.writable = False
        C1.addFile("http://vospace.esac.esa.int/vospace/sh/eb9834b594e8da89111147899d15c26dd5ecf9?dl=1","foo.pdf")

    def test_getFile(self):
        print('test_getFile')
        area = getUid()
        path = self.home / area
        S1 = FileCache.StorageArea(str(path))
        ctxt = getUid()
        C1 = S1.addContext(ctxt)
        C1.addFile("http://vospace.esac.esa.int/vospace/sh/eb9834b594e8da89111147899d15c26dd5ecf9?dl=1","foo.pdf")
        C1.getFile("foo.pdf")

    def test_getFileNotWritable(self):
        print('test_getFileNotWritable')
        area = getUid()
        path = self.home / area
        S1 = FileCache.StorageArea(str(path))
        ctxt = getUid()
        C1 = S1.addContext(ctxt)
        C1.addFile("http://vospace.esac.esa.int/vospace/sh/eb9834b594e8da89111147899d15c26dd5ecf9?dl=1","foo.pdf")
        S1.writable = False
        C1.getFile("foo.pdf")

    def test_getFileNotExists(self):
        print('test_getFileNotExists')
        area = getUid()
        path = self.home / area
        S1 = FileCache.StorageArea(str(path))
        ctxt = getUid()
        C1 = S1.addContext(ctxt)
        C1.addFile("http://vospace.esac.esa.int/vospace/sh/blah","foo.pdf")
        C1.getFile("foo.pdf")

    def test_deleteFile(self):
        print('test_deleteFile')
        area = getUid()
        path = self.home / area
        S1 = FileCache.StorageArea(str(path))
        ctxt = getUid()
        C1 = S1.addContext(ctxt)
        C1.addFile("http://vospace.esac.esa.int/vospace/sh/eb9834b594e8da89111147899d15c26dd5ecf9?dl=1","foo.pdf")
        C1.getFile("foo.pdf")
        C1.deleteFile("foo.pdf")

    def test_deleteFileNoExist(self):
        print('test_deleteFileNoExist')
        print('test_deleteFile')
        area = getUid()
        path = self.home / area
        S1 = FileCache.StorageArea(str(path))
        ctxt = getUid()
        C1 = S1.addContext(ctxt)
        C1.addFile("http://vospace.esac.esa.int/vospace/sh/eb9834b594e8da89111147899d15c26dd5ecf9?dl=1","foo.pdf")
        C1.getFile("foo.pdf")
        C1.deleteFile("foo1.pdf")

    def test_deleteFileNotWritable(self):
        print('test_deleteFileNotWritable')
        area = getUid()
        path = self.home / area
        S1 = FileCache.StorageArea(str(path))
        ctxt = getUid()
        C1 = S1.addContext(ctxt)
        C1.addFile("http://vospace.esac.esa.int/vospace/sh/eb9834b594e8da89111147899d15c26dd5ecf9?dl=1","foo.pdf")
        C1.getFile("foo.pdf")
        S1.writable = False
        C1.deleteFile("foo.pdf")

    def test_testSimpleCache(self):
        print('test_initEmpty')
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
